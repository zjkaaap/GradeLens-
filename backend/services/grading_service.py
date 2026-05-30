from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from config import settings
from services.llm_client import get_client
from utils.image_utils import image_to_data_url
from utils.prompt_templates import (
    GRADE_PAPER_SYSTEM,
    GRADE_PAPER_USER_TEMPLATE,
    GRADE_SYSTEM,
    GRADE_USER_TEMPLATE,
)

JSON_OBJECT_PAT = re.compile(r"\{[\s\S]*\}")

_LATEX_CTRL_FIX = str.maketrans({
    "\t": "\\t",
    "\b": "\\b",
    "\f": "\\f",
    "\r": "\\r",
    "\v": "\\v",
})


def _restore_latex(text: str) -> str:
    """模型在 JSON 字符串里写单反斜杠 \\frac \\text，被 JSON 解析吞成 FF/TAB/BS。
    这些控制字符在数学作答里几乎不会出现，安全地把它们还原为字面反斜杠。"""
    if not isinstance(text, str):
        return text
    return text.translate(_LATEX_CTRL_FIX)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = JSON_OBJECT_PAT.search(text)
    if not m:
        raise ValueError(f"模型未返回有效 JSON：{text[:200]}")
    return json.loads(m.group())


def grade_with_image(
    qno: str,
    stem: str,
    answer: str,
    explanation: str,
    full_score: int,
    image_path: str | Path,
) -> dict[str, Any]:
    """Send the student's answer image directly to qwen3.6-plus for one-shot
    vision understanding + grading. Avoids OCR loss on handwritten content."""
    client = get_client()
    data_url = image_to_data_url(image_path, compress=True)
    prompt = GRADE_USER_TEMPLATE.format(
        qno=qno,
        full_score=full_score,
        stem=stem,
        answer=answer or "（试卷未给出标准答案，请基于题干合理推断）",
        explanation=explanation or "（无）",
    )
    resp = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": GRADE_SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": prompt},
                ],
            },
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content or ""
    data = _extract_json(raw)

    belongs = data.get("belongs_to_this_question", True)
    if isinstance(belongs, str):
        belongs = belongs.strip().lower() not in {"false", "0", "no", ""}
    belongs = bool(belongs)

    score = int(data.get("score", 0))
    score = max(0, min(score, full_score))
    deductions = data.get("deductions") or []
    norm_deductions = []
    for d in deductions:
        if isinstance(d, dict):
            norm_deductions.append({
                "point": str(d.get("point", "")).strip(),
                "deduct": int(d.get("deduct", 0)),
            })

    transcribed = _restore_latex(str(data.get("transcribed_answer", "")).strip())
    comment = str(data.get("comment", "")).strip()

    if not belongs:
        score = 0
        if not norm_deductions:
            norm_deductions = [{
                "point": "学生作答与本题不符（题目对象/字母与作答不一致）",
                "deduct": full_score,
            }]
        if not comment:
            comment = "作答与本题不匹配"

    return {
        "transcribed_answer": transcribed,
        "score": score,
        "full_score": full_score,
        "deductions": norm_deductions,
        "comment": comment,
    }


def _normalize_deductions(raw: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(raw, list):
        return out
    for d in raw:
        if isinstance(d, dict):
            try:
                deduct = int(d.get("deduct", 0))
            except (TypeError, ValueError):
                deduct = 0
            out.append({
                "point": str(d.get("point", "")).strip(),
                "deduct": deduct,
            })
    return out


def grade_paper_with_images(
    questions: list[dict[str, Any]],
    image_paths: list[str | Path],
) -> list[dict[str, Any]]:
    """One-shot grading of a whole paper: send all student-answer images plus
    the full question list to qwen3.6-plus, get back per-question grading."""
    if not questions:
        return []
    if not image_paths:
        raise ValueError("至少需要一张学生作答图片")

    client = get_client()
    questions_payload = [
        {
            "qno": q["qno"],
            "stem": q.get("stem", ""),
            "answer": q.get("answer", "") or "（试卷未给出标准答案，请基于题干合理推断）",
            "explanation": q.get("explanation", "") or "（无）",
            "full_score": int(q.get("score", 5) or 5),
        }
        for q in questions
    ]
    full_score_total = sum(item["full_score"] for item in questions_payload)
    prompt = GRADE_PAPER_USER_TEMPLATE.format(
        question_count=len(questions_payload),
        full_score_total=full_score_total,
        image_count=len(image_paths),
        questions_json=json.dumps(questions_payload, ensure_ascii=False, indent=2),
    )

    user_content: list[dict[str, Any]] = []
    for p in image_paths:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": image_to_data_url(p, compress=True)},
        })
    user_content.append({"type": "text", "text": prompt})

    resp = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": GRADE_PAPER_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content or ""
    data = _extract_json(raw)
    items_raw = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items_raw, list):
        raise ValueError(f"模型返回 items 字段缺失或非数组：{raw[:200]}")

    by_qno: dict[str, dict[str, Any]] = {}
    for it in items_raw:
        if not isinstance(it, dict):
            continue
        qno = str(it.get("qno", "")).strip()
        if not qno:
            continue
        by_qno[qno] = it

    results: list[dict[str, Any]] = []
    for q in questions:
        qno = str(q["qno"]).strip()
        full_score = int(q.get("score", 5) or 5)
        it = by_qno.get(qno)
        if it is None:
            results.append({
                "qno": qno,
                "matched": False,
                "transcribed_answer": "",
                "score": 0,
                "full_score": full_score,
                "deductions": [],
                "comment": "模型未返回该题评分",
            })
            continue

        belongs = it.get("belongs_to_this_question", True)
        if isinstance(belongs, str):
            belongs = belongs.strip().lower() not in {"false", "0", "no", ""}
        belongs = bool(belongs)

        try:
            score = int(it.get("score", 0))
        except (TypeError, ValueError):
            score = 0
        score = max(0, min(score, full_score))

        transcribed = _restore_latex(str(it.get("transcribed_answer", "")).strip())
        comment = str(it.get("comment", "")).strip()
        deductions = _normalize_deductions(it.get("deductions"))

        if not belongs:
            score = 0
            transcribed = ""
            if not comment:
                comment = "未作答"
            deductions = []

        results.append({
            "qno": qno,
            "matched": True,
            "transcribed_answer": transcribed,
            "score": score,
            "full_score": full_score,
            "deductions": deductions,
            "comment": comment,
        })
    return results
