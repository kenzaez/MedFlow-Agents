"""
MCP Client Tool
---------------
Connects to the MCP server to fetch general medical orientation guidelines.
This satisfies the "au moins un outil via MCP" requirement.

The MCP server runs separately at MCP_SERVER_URL (default: http://localhost:8001).
"""
import os
import httpx
from langchain_core.tools import tool


MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
MCP_TIMEOUT = float(os.getenv("MCP_TIMEOUT", "10.0"))


@tool
def get_medical_guidelines(condition_keywords: str) -> str:
    """
    Fetches general medical orientation guidelines from the MCP server.
    Use this to enrich clinical synthesis with evidence-based orientation.

    Args:
        condition_keywords: Keywords describing the patient's condition (max 100 chars).

    Returns:
        General clinical orientation guidelines as a string, or a fallback message.
    """
    try:
        response = httpx.post(
            f"{MCP_SERVER_URL}/tools/get_guidelines",
            json={"keywords": condition_keywords[:100]},
            timeout=MCP_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("guidelines", "Aucune recommandation spécifique disponible.")

    except httpx.ConnectError:
        return (
            "MCP server non disponible. "
            "Synthèse basée uniquement sur les réponses du patient."
        )
    except httpx.TimeoutException:
        return "MCP server timeout. Synthèse basée uniquement sur les réponses du patient."
    except Exception as e:
        return f"Erreur MCP ({type(e).__name__}). Synthèse basée sur les données patient."
