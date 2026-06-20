"""
PhysicianReview Node  — Human-in-the-Loop
------------------------------------------
The graph pauses here and presents the diagnostic summary + interim care
to the treating physician (screen 3 on the frontend).

The physician submits a treatment plan or conduct via POST /consultation/resume.
"""
from app.state import MedicalState
from langgraph.types import interrupt


def physician_review_node(state: MedicalState) -> dict:
    """
    Interrupts the graph and sends the diagnostic synthesis to the physician.
    Waits for the physician's treatment / conduct (resumed via API).
    """
    physician_input = interrupt({
        "type": "physician_review",
        "patient_name": state.get("patient_name", "Patient"),
        "patient_complaint": state.get("patient_complaint", ""),
        "diagnostic_summary": state.get("diagnostic_summary", ""),
        "interim_care": state.get("interim_care", ""),
        "prompt": (
            "En tant que médecin traitant, veuillez proposer un traitement "
            "ou une conduite à tenir pour ce patient."
        ),
    })

    return {
        "physician_treatment": str(physician_input),
        "next": "report_agent",
    }
