"""
DiagnosticAgent Node
--------------------
Responsibilities:
  1. Generate 5 targeted clinical questions via LLM (temperature=0 for stability).
  2. Ask each question one at a time using LangGraph's interrupt() — the graph
     pauses here and waits for the patient's answer via POST /consultation/resume.
  3. After all 5 answers, produce a preliminary clinical synthesis.
  4. Call the recommend_interim_care tool to generate intermediate recommendations.

LangGraph interrupt() behaviour:
  When this node calls interrupt(), the graph is checkpointed and suspended.
  On the next resume (Command(resume=answer)), LangGraph replays this node
  and returns the cached answer for already-answered interrupts, so the for-loop
  picks up at the correct question automatically.
"""
import os
import json
from langchain_groq import ChatGroq
from langgraph.types import interrupt
from app.state import MedicalState, QAPair
from app.tools.care_tools import recommend_interim_care
from app.tools.mcp_client import get_medical_guidelines


LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")


def _get_llm() -> ChatGroq:
    return ChatGroq(model=LLM_MODEL, temperature=0)


def _generate_questions(complaint: str, patient_name: str) -> list[str]:
    """Generate exactly 5 clinical questions tailored to the complaint."""
    llm = _get_llm()
    prompt = f"""Tu es un assistant médical clinique. 
Un patient nommé {patient_name} se présente avec la plainte suivante :
"{complaint}"

Génère exactement 5 questions cliniques en français pour mieux évaluer son état.
Les questions doivent couvrir : durée/onset, intensité, localisation, symptômes associés, antécédents.
Retourne UNIQUEMENT un JSON array de 5 strings, sans markdown. 
Exemple: ["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]"""

    response = llm.invoke([{"role": "user", "content": prompt}])
    
    try:
        # Strip any accidental markdown fences
        content = response.content.strip().strip("```json").strip("```").strip()
        questions = json.loads(content)
        if isinstance(questions, list) and len(questions) >= 5:
            return questions[:5]
    except Exception:
        pass

    # Fallback: generic clinical questions
    return [
        "Depuis combien de temps ressentez-vous ces symptômes ?",
        "Comment évaluez-vous l'intensité de vos symptômes sur une échelle de 1 à 10 ?",
        "Avez-vous d'autres symptômes associés (fièvre, douleur, nausées, etc.) ?",
        "Avez-vous des antécédents médicaux ou des traitements en cours ?",
        "Avez-vous remarqué des facteurs qui aggravent ou soulagent vos symptômes ?",
    ]


def _generate_summary(complaint: str, qa_pairs: list[QAPair], guidelines: str) -> str:
    """Produce a preliminary clinical synthesis from Q&A pairs."""
    llm = _get_llm()

    qa_text = "\n".join(
        [f"Q{i+1}: {qa['question']}\nRéponse: {qa['answer']}" for i, qa in enumerate(qa_pairs)]
    )

    prompt = f"""Tu es un assistant médical. 
Produis une synthèse clinique préliminaire basée sur les informations suivantes.

Plainte initiale : {complaint}

Questions et réponses du patient :
{qa_text}

Recommandations cliniques générales disponibles :
{guidelines}

Instructions :
- Ne commence PAS la réponse par un titre ou en-tête principal (comme "Synthèse Clinique Préliminaire" ou "# Synthèse Clinique Préliminaire") car l'interface affiche déjà ce titre. Rédige directement le premier paragraphe.
- Résume les éléments cliniques pertinents.
- Identifie les symptômes principaux et les éventuels signaux d'alerte (red flags).
- Propose une orientation clinique préliminaire (PAS un diagnostic définitif).
- Utilise les termes : "orientation clinique préliminaire", "synthèse clinique", "recommandation intermédiaire".
- Termine OBLIGATOIREMENT par : "⚠️ Ce système ne remplace pas une consultation médicale."

Rédige en français, de manière claire et structurée."""

    response = llm.invoke([{"role": "user", "content": prompt}])
    return response.content


def diagnostic_agent_node(state: MedicalState) -> dict:
    """
    Main diagnostic agent node.
    Uses LangGraph interrupt() in a loop to collect 5 patient answers,
    then generates the clinical synthesis and interim care recommendation.
    """
    complaint = state.get("patient_complaint", "Plainte non spécifiée")
    patient_name = state.get("patient_name", "Patient")
    
    print(f"DEBUG: diagnostic_agent_node called with complaint={complaint}, name={patient_name}")

    # ── Step 1: Generate 5 questions ─────────────────────────────────────────
    # With temperature=0, re-generation on resume produces identical questions.
    try:
        questions = _generate_questions(complaint, patient_name)
        print(f"DEBUG: Generated questions: {questions}")
    except Exception as e:
        print(f"ERROR in _generate_questions: {e}")
        import traceback
        traceback.print_exc()
        raise

    # ── Step 2: Ask each question via interrupt ───────────────────────────────
    # LangGraph replays previously answered interrupts instantly on resume.
    qa_pairs: list[QAPair] = []
    for i, question in enumerate(questions):
        answer = interrupt({
            "type": "patient_question",
            "question": question,
            "question_number": i + 1,
            "total_questions": 5,
        })
        qa_pairs.append({"question": question, "answer": str(answer)})

    # ── Step 3: Fetch MCP guidelines (enriches the summary) ──────────────────
    try:
        guidelines = get_medical_guidelines.invoke({"condition_keywords": complaint[:100]})
    except Exception:
        guidelines = "Aucune recommandation externe disponible."

    # ── Step 4: Generate clinical synthesis ──────────────────────────────────
    diagnostic_summary = _generate_summary(complaint, qa_pairs, guidelines)

    # ── Step 5: Generate interim care recommendation ──────────────────────────
    try:
        interim_care = recommend_interim_care.invoke({"diagnostic_summary": diagnostic_summary})
    except Exception:
        interim_care = "Repos recommandé. Hydratation suffisante. Consultez un médecin si aggravation."

    return {
        "qa_pairs": qa_pairs,
        "question_count": 5,
        "diagnostic_summary": diagnostic_summary,
        "interim_care": interim_care,
        "next": "physician_review",
    }
