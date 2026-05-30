from __future__ import annotations


def _char_overlap(a: str, b: str) -> int:
    return len(set(a) & set(b))


def match_question(
    questions: list[dict],
    qno: str = "",
    keyword: str = "",
) -> dict | None:
    if qno:
        target = str(qno).strip()
        for q in questions:
            if str(q.get("qno", "")).strip() == target:
                return q

    if keyword:
        kw = keyword.strip()
        if not kw:
            return None
        contains = [q for q in questions if kw in (q.get("stem") or "")]
        if contains:
            return contains[0]
        scored = sorted(questions, key=lambda q: -_char_overlap(kw, q.get("stem") or ""))
        return scored[0] if scored else None

    return None
