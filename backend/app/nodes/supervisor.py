from app.state import MedicalState


def supervisor_node(state: MedicalState) -> dict:
    """
    Orchestrates the workflow by routing to the correct next node.
    Sets state['next'] based on what has been completed so far.
    This is a deterministic router — no LLM call needed here.
    """
    # Already has a final report → done
    if state.get("final_report"):
        return {"next": "FINISH"}

    # Physician has submitted treatment → generate report
    if state.get("physician_treatment") and state.get("diagnostic_summary"):
        return {"next": "report_agent"}

    # Diagnostic complete → send to physician review
    if state.get("diagnostic_summary"):
        return {"next": "physician_review"}

    # Default → diagnostic agent (first entry or resumed mid-diagnosis)
    return {"next": "diagnostic_agent"}
