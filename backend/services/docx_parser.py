"""Parse exam papers by uploading docx to Alibaba Cloud's qwen-long model.

This replaces local python-docx parsing which loses math formulas (OMML).
qwen-long can read the full docx natively via fileid:// and output structured JSON.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from services.llm_client import get_client
from config import settings

PARSE_SYSTEM = '''你是试卷结构化解析助手。你将看到一份完整的试卷文档（含题目、标准答案、解析）。
请提取每一道题，输出 JSON：
{"questions": [{"qno": "1", "stem": "题干（含选项）", "answer": "标准答案", "explanation": "解析", "score": 5}, ...]}

要求：
- qno 用阿拉伯数字字符串
- 数学公式用 LaTeX 表达（如 \\frac{a}{b}, x^2, \\sqrt{x}）
- 单选题5分、多选题6分、填空题5分、解答题12分（除非文档明确给出其他分值）
- stem 包含完整题干和选项（如有）
- answer 包含完整标准答案
- explanation 包含完整解析过程
- 只输出 JSON，不要其他说明文字'''

JSON_OBJECT_PAT = re.compile(r"\{[\s\S]*\}")


def parse_docx_with_llm(docx_path: str | Path) -> list[dict]:
    """Upload docx to DashScope file API, then ask qwen-long to structure it."""
    client = get_client()

    file_obj = client.files.create(
        file=Path(docx_path),
        purpose="file-extract",
    )

    try:
        resp = client.chat.completions.create(
            model="qwen-long",
            messages=[
                {"role": "system", "content": f"fileid://{file_obj.id}"},
                {"role": "system", "content": PARSE_SYSTEM},
                {"role": "user", "content": "请输出本试卷的结构化 JSON。"},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
    finally:
        try:
            client.files.delete(file_obj.id)
        except Exception:
            pass

    raw = resp.choices[0].message.content or ""
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = JSON_OBJECT_PAT.search(raw)
        if not m:
            raise ValueError(f"qwen-long 未返回有效 JSON：{raw[:200]}")
        data = json.loads(m.group())

    questions = data.get("questions", [])
    if not questions:
        raise ValueError("qwen-long 未能从文档中提取出题目")

    result = []
    for q in questions:
        result.append({
            "qno": str(q.get("qno", "")).strip(),
            "stem": str(q.get("stem", "")).strip(),
            "answer": str(q.get("answer", "")).strip(),
            "explanation": str(q.get("explanation", "")).strip(),
            "score": int(q.get("score", 5)),
        })
    return result
