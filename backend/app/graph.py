"""
Medical Consultation Graph
--------------------------
Defines and compiles the LangGraph multi-agent workflow.

Topology:
  START → supervisor → diagnostic_agent → supervisor
                                       → physician_review → supervisor
                                       → report_agent → supervisor → END

The supervisor reads state['next'] and routes deterministically.
Interrupts (patient questions + physician review) are handled inside nodes.
"""
from langgraph.graph import StateGraph, END

from app.state import MedicalState
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node


def _route_from_supervisor(state: MedicalState) -> str:
    """Conditional edge: reads state['next'] set by supervisor_node."""
    return state.get("next", "diagnostic_agent")


def build_graph() -> StateGraph:
    """Build (but don't compile) the graph. Used for LangGraph Studio."""
    builder = StateGraph(MedicalState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("diagnostic_agent", diagnostic_agent_node)
    builder.add_node("physician_review", physician_review_node)
    builder.add_node("report_agent", report_agent_node)

    builder.set_entry_point("supervisor")

    builder.add_conditional_edges(
        "supervisor",
        _route_from_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            "FINISH": END,
        },
    )

    builder.add_edge("diagnostic_agent", "supervisor")
    builder.add_edge("physician_review", "supervisor")
    builder.add_edge("report_agent", "supervisor")

    return builder


def compile_graph(db_path: str = "./consultations.db"):
    """Compile the graph with SQLite checkpointer for persistence across HTTP calls."""
    try:
        import sqlite3
        from langgraph.checkpoint.sqlite import SqliteSaver
        print(f"DEBUG: Compiling graph with db_path={db_path}")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.isolation_level = None  # autocommit — avoids threading issues
        checkpointer = SqliteSaver(conn)
        print(f"DEBUG: Created SqliteSaver")
        checkpointer.setup()
        print(f"DEBUG: Setup checkpointer")
        compiled = build_graph().compile(checkpointer=checkpointer)
        print(f"DEBUG: Graph compiled successfully")
        return compiled
    except Exception as e:
        print(f"ERROR in compile_graph: {e}")
        import traceback
        traceback.print_exc()
        raise


# Singleton graph instance used by the API
print("DEBUG: Initializing graph module...")
try:
    graph = compile_graph()
    print("DEBUG: Graph initialized successfully")
except Exception as e:
    print(f"ERROR: Failed to initialize graph: {e}")
    raise
