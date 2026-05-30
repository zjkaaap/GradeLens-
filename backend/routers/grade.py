from __future__ import annotations

import base64
import binascii
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import GradingRecord, Paper, Question
from schemas import (
    ApiResponse,
    GradeResult,
    PaperGradeItem,
    PaperGradeRequest,
    PaperGradeResult,
    QuestionOut,
)
from services.grading_service import grade_paper_with_images, grade_with_image
from services.matcher import match_question

router = APIRouter()


def _save_image(file: UploadFile) -> Path:
    suffix = Path(file.filename or "").suffix.lower() or ".png"
    if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        raise HTTPException(400, "仅支持 png/jpg/jpeg/webp/bmp 图片")
    content = file.file.read()
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"图片超过 {settings.MAX_UPLOAD_MB}MB 限制")
    dest = settings.STUDENT_IMGS_DIR / f"{uuid.uuid4().hex}{suffix}"
    dest.write_bytes(content)
    return dest


def _save_image_b64(b64: str, idx: int) -> Path:
    raw = b64.strip()
    suffix = ".png"
    if raw.startswith("data:"):
        head, _, body = raw.partition(",")
        if "image/jpeg" in head or "image/jpg" in head:
            suffix = ".jpg"
        elif "image/webp" in head:
            suffix = ".webp"
        elif "image/bmp" in head:
            suffix = ".bmp"
        raw = body
    try:
        content = base64.b64decode(raw, validate=False)
    except (binascii.Error, ValueError) as e:
        raise HTTPException(400, f"第 {idx + 1} 张图片 base64 解码失败：{e}") from e
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"第 {idx + 1} 张图片超过 {settings.MAX_UPLOAD_MB}MB 限制")
    dest = settings.STUDENT_IMGS_DIR / f"{uuid.uuid4().hex}{suffix}"
    dest.write_bytes(content)
    return dest


def _format_deduction_reason(deductions: list[dict]) -> str:
    if not deductions:
        return "无明显扣分点"
    parts = []
    for d in deductions:
        point = (d.get("point") or "").strip()
        deduct = d.get("deduct", 0)
        if point:
            parts.append(f"{point}（-{deduct}分）")
    return "；".join(parts) if parts else "无明显扣分点"


@router.post("/grade", response_model=ApiResponse[GradeResult])
async def grade_student(
    image: UploadFile = File(...),
    paper_id: int = Form(...),
    question_no: str = Form(""),
    stem_keyword: str = Form(""),
    db: Session = Depends(get_db),
):
    paper = db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(404, "试卷不存在")
    if not paper.questions:
        raise HTTPException(400, "试卷未解析出题目")

    questions_data = [
        {
            "id": q.id,
            "qno": q.qno,
            "stem": q.stem or "",
            "answer": q.answer or "",
            "explanation": q.explanation or "",
            "score": q.score or 5,
        }
        for q in paper.questions
    ]
    matched = match_question(questions_data, qno=question_no, keyword=stem_keyword)
    if not matched:
        raise HTTPException(404, "未在该试卷中匹配到对应题目，请检查题号或关键字")

    img_path = _save_image(image)

    try:
        result = grade_with_image(
            qno=matched["qno"],
            stem=matched["stem"],
            answer=matched["answer"],
            explanation=matched["explanation"],
            full_score=matched["score"],
            image_path=img_path,
        )
    except Exception as e:
        raise HTTPException(502, f"AI 评分调用失败：{e}") from e

    deduction_reason = _format_deduction_reason(result["deductions"])

    record = GradingRecord(
        paper_id=paper_id,
        question_id=matched["id"],
        image_path=str(img_path),
        student_ocr=result["transcribed_answer"],
        score_obtained=result["score"],
        full_score=result["full_score"],
        deduction_reason=deduction_reason,
        ai_comment=result["comment"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ApiResponse(data=GradeResult(
        record_id=record.id,
        matched_question=QuestionOut(
            id=matched["id"],
            qno=matched["qno"],
            stem=matched["stem"],
            answer=matched["answer"],
            explanation=matched["explanation"],
            score=matched["score"],
        ),
        student_answer_ocr=result["transcribed_answer"],
        score_obtained=result["score"],
        full_score=result["full_score"],
        deductions=result["deductions"],
        deduction_reason=deduction_reason,
        ai_comment=result["comment"],
    ))


@router.get("/grade/{record_id}", response_model=ApiResponse[dict])
def get_grade_record(record_id: int, db: Session = Depends(get_db)):
    rec = db.get(GradingRecord, record_id)
    if not rec:
        raise HTTPException(404, "评分记录不存在")
    return ApiResponse(data={
        "record_id": rec.id,
        "paper_id": rec.paper_id,
        "question_id": rec.question_id,
        "student_ocr": rec.student_ocr,
        "score_obtained": rec.score_obtained,
        "full_score": rec.full_score,
        "deduction_reason": rec.deduction_reason,
        "ai_comment": rec.ai_comment,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
    })


@router.post("/grade_paper", response_model=ApiResponse[PaperGradeResult])
async def grade_student_paper(
    payload: PaperGradeRequest,
    db: Session = Depends(get_db),
):
    if not payload.images_b64:
        raise HTTPException(400, "请至少上传一张作答图片")
    if len(payload.images_b64) > 9:
        raise HTTPException(400, "单次最多上传 9 张图片")

    paper = db.get(Paper, payload.paper_id)
    if not paper:
        raise HTTPException(404, "试卷不存在")
    if not paper.questions:
        raise HTTPException(400, "试卷未解析出题目")

    questions_data = [
        {
            "id": q.id,
            "qno": q.qno,
            "stem": q.stem or "",
            "answer": q.answer or "",
            "explanation": q.explanation or "",
            "score": q.score or 5,
        }
        for q in paper.questions
    ]

    saved_paths = [_save_image_b64(b, i) for i, b in enumerate(payload.images_b64)]

    try:
        graded = grade_paper_with_images(
            questions=questions_data,
            image_paths=saved_paths,
        )
    except Exception as e:
        raise HTTPException(502, f"AI 评分调用失败：{e}") from e

    by_qno = {str(q["qno"]).strip(): q for q in questions_data}
    image_path_str = ",".join(str(p) for p in saved_paths)

    items: list[PaperGradeItem] = []
    total_score = 0
    full_score_total = 0
    for g in graded:
        qno = g["qno"]
        q = by_qno.get(qno)
        deduction_reason = _format_deduction_reason(g["deductions"])
        full_score_total += g["full_score"]
        total_score += g["score"]

        record_id: int | None = None
        if q is not None and g.get("matched"):
            record = GradingRecord(
                paper_id=payload.paper_id,
                question_id=q["id"],
                image_path=image_path_str,
                student_ocr=g["transcribed_answer"],
                score_obtained=g["score"],
                full_score=g["full_score"],
                deduction_reason=deduction_reason,
                ai_comment=g["comment"],
            )
            db.add(record)
            db.flush()
            record_id = record.id

        items.append(PaperGradeItem(
            record_id=record_id,
            qno=qno,
            question=QuestionOut(
                id=q["id"] if q else None,
                qno=qno,
                stem=q["stem"] if q else "",
                answer=q["answer"] if q else "",
                explanation=q["explanation"] if q else "",
                score=g["full_score"],
            ),
            matched=bool(g.get("matched")),
            student_answer_ocr=g["transcribed_answer"],
            score_obtained=g["score"],
            full_score=g["full_score"],
            deductions=g["deductions"],
            deduction_reason=deduction_reason,
            ai_comment=g["comment"],
        ))

    db.commit()

    return ApiResponse(data=PaperGradeResult(
        paper_id=payload.paper_id,
        paper_name=paper.name,
        total_score=total_score,
        full_score=full_score_total,
        items=items,
    ))
