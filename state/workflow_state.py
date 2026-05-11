import operator
from typing import TypedDict, Annotated, Optional

class GradingState(TypedDict):
    file_id: str
    file_content: str
    file_name: str
    student_name: Optional[str]
    total_score: Optional[float]
    email_draft: Optional[str]
    teacher_approved: bool
    rubric_content: str