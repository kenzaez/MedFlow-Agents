"""
Patient Tools
-------------
Tools used by the DiagnosticAgent to interact with patient data.
These are LangChain @tool decorated functions, satisfying the spec requirement
that "questions must be managed via a tool."
"""
from langchain_core.tools import tool
from typing import List


@tool
def ask_patient(question: str, question_number: int) -> str:
    """
    Formats a clinical question to be presented to the patient.
    The actual answer is collected via LangGraph's interrupt() mechanism.
    
    Args:
        question: The clinical question text.
        question_number: Position in the 5-question sequence (1-5).
    
    Returns:
        Formatted question string for display.
    """
    return f"[Question {question_number}/5] {question}"


@tool
def parse_patient_answers(qa_pairs: List[dict]) -> str:
    """
    Formats the collected Q&A pairs into a readable clinical summary string.
    
    Args:
        qa_pairs: List of dicts with 'question' and 'answer' keys.
    
    Returns:
        Formatted string of all Q&A pairs.
    """
    lines = []
    for i, qa in enumerate(qa_pairs, 1):
        lines.append(f"Q{i}: {qa.get('question', '')}")
        lines.append(f"Réponse: {qa.get('answer', '')}")
        lines.append("")
    return "\n".join(lines)
