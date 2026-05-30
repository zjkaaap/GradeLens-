from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    msg: str = "ok"
    data: Optional[T] = None


class QuestionOut(BaseModel):
    id: Optional[int] = None
    qno: str
    stem: str
    answer: str = ""
    explanation: str = ""
    score: int = 5

    model_config = {"from_attributes": True}


class PaperBrief(BaseModel):
    paper_id: int
    paper_name: str
    question_count: int
    created_at: datetime


class PaperUploadResult(BaseModel):
    paper_id: int
    paper_name: str
    question_count: int
    questions_preview: List[QuestionOut] = Field(default_factory=list)


class PaperDetail(BaseModel):
    paper_id: int
    paper_name: str
    questions: List[QuestionOut]


class DeductionItem(BaseModel):
    point: str
    deduct: int


class GradeResult(BaseModel):
    record_id: int
    matched_question: QuestionOut
    student_answer_ocr: str
    score_obtained: int
    full_score: int
    deductions: List[DeductionItem] = Field(default_factory=list)
    deduction_reason: str
    ai_comment: str


class PaperGradeItem(BaseModel):
    record_id: Optional[int] = None
    qno: str
    question: Optional[QuestionOut] = None
    matched: bool = True
    student_answer_ocr: str = ""
    score_obtained: int = 0
    full_score: int = 0
    deductions: List[DeductionItem] = Field(default_factory=list)
    deduction_reason: str = ""
    ai_comment: str = ""


class PaperGradeRequest(BaseModel):
    paper_id: int
    images_b64: List[str] = Field(default_factory=list)


class PaperGradeResult(BaseModel):
    paper_id: int
    paper_name: str
    total_score: int
    full_score: int
    items: List[PaperGradeItem]
