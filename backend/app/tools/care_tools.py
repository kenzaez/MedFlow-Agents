"""
Care Tools
----------
Tool for generating intermediate/interim care recommendations.
Called by the DiagnosticAgent after producing the clinical synthesis.
"""
import os
from langchain_core.tools import tool
from langchain_groq import ChatGroq


@tool
def recommend_interim_care(diagnostic_summary: str) -> str:
    """
    Generates a prudent interim care recommendation based on the clinical synthesis.
    Recommendations may include rest, hydration, monitoring, or urgent consultation.
    Never replaces medical advice — remains general and cautious.

    Args:
        diagnostic_summary: The preliminary clinical synthesis text.

    Returns:
        A short interim care recommendation (2-4 sentences, in French).
    """
    llm = ChatGroq(
        model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        temperature=0,
    )

    prompt = f"""Tu es un assistant médical. 
Génère une recommandation intermédiaire courte et prudente (2 à 4 phrases maximum).

Elle peut inclure parmi : repos, hydratation suffisante, surveillance des symptômes, 
consultation rapide en cas d'aggravation, éviter certains aliments/activités.

Elle NE DOIT PAS : poser un diagnostic, prescrire un médicament spécifique, remplacer un avis médical.

Synthèse clinique :
{diagnostic_summary}

Réponds uniquement avec la recommandation, en français."""

    response = llm.invoke([{"role": "user", "content": prompt}])
    return response.content
