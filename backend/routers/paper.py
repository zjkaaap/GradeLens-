from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import GradingRecord, Paper, Question
from schemas import (
    ApiResponse,
    PaperBrief,
    PaperDetail,
    PaperUploadResult,
    QuestionOut,
)
from services.docx_parser import parse_docx_with_llm

router = APIRouter()


def _save_upload(file: UploadFile, dest_dir: Path) -> Path:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix != ".docx":
        raise HTTPException(400, "仅支持 .docx 文件")
    content = file.file.read()
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"文件超过 {settings.MAX_UPLOAD_MB}MB 限制")
    dest = dest_dir / f"{uuid.uuid4().hex}{suffix}"
    dest.write_bytes(content)
    return dest


@router.post("/upload", response_model=ApiResponse[PaperUploadResult])
async def upload_paper(
    file: UploadFile = File(...),
    paper_name: str = Form(...),
    db: Session = Depends(get_db),
):
    dest = _save_upload(file, settings.PAPERS_DIR)
    try:
        questions = parse_docx_with_llm(dest)
    except Exception as e:
        dest.unlink(missing_ok=True)
        raise HTTPException(500, f"解析 docx 失败: {e}") from e

    if not questions:
        dest.unlink(missing_ok=True)
        raise HTTPException(422, "未能从该 docx 中识别出题目，请确认试卷格式")

    paper = Paper(name=paper_name.strip(), file_path=str(dest))
    db.add(paper)
    db.flush()
    for q in questions:
        db.add(Question(
            paper_id=paper.id,
            qno=q["qno"],
            stem=q["stem"],
            answer=q["answer"],
            explanation=q["explanation"],
            score=q["score"],
        ))
    db.commit()
    db.refresh(paper)

    preview = [QuestionOut.model_validate(q) for q in paper.questions[:5]]
    return ApiResponse(data=PaperUploadResult(
        paper_id=paper.id,
        paper_name=paper.name,
        question_count=len(paper.questions),
        questions_preview=preview,
    ))


@router.get("/list", response_model=ApiResponse[list[PaperBrief]])
def list_papers(db: Session = Depends(get_db)):
    papers = db.query(Paper).order_by(Paper.created_at.desc()).all()
    data = [
        PaperBrief(
            paper_id=p.id,
            paper_name=p.name,
            question_count=len(p.questions),
            created_at=p.created_at,
        )
        for p in papers
    ]
    return ApiResponse(data=data)


@router.get("/{paper_id}", response_model=ApiResponse[PaperDetail])
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(404, "试卷不存在")
    return ApiResponse(data=PaperDetail(
        paper_id=paper.id,
        paper_name=paper.name,
        questions=[QuestionOut.model_validate(q) for q in paper.questions],
    ))


@router.delete("/{paper_id}", response_model=ApiResponse[dict])
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.get(Paper, paper_id)
    if not paper:
        raise HTTPException(404, "试卷不存在")
    if paper.file_path:
        Path(paper.file_path).unlink(missing_ok=True)
    db.query(GradingRecord).filter(GradingRecord.paper_id == paper_id).delete()
    db.delete(paper)
    db.commit()
    return ApiResponse(data={"paper_id": paper_id})
