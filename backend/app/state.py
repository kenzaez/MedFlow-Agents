from __future__ import annotations
from typing import Annotated, List, Optional
from typing_extensions import TypedDict, Literal
from langgraph.graph.message import add_messages


class QAPair(TypedDict):
    question: str
    answer: str


class MedicalState(TypedDict, total=False):
    # LangChain messages (append-only)
    messages: Annotated[list, add_messages]

    # Supervisor routing key
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]

    # Patient info
    patient_name: str
    patient_complaint: str  # initial complaint entered on screen 1

    # Diagnostic phase
    qa_pairs: List[QAPair]   # [{question, answer}, ...] accumulated across interrupts
    question_count: int
    diagnostic_summary: str  # preliminary clinical synthesis
    interim_care: str        # intermediate recommendation

    # Physician phase
    physician_treatment: str # physician's treatment / conduct

    # Final
    final_report: str
