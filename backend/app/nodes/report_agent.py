"""
ReportAgent Node
----------------
Generates the structured final report combining:
  - Patient complaint
  - Q&A pairs from the diagnostic phase
  - Preliminary clinical synthesis
  - Interim care recommendations
  - Physician's treatment / conduct

Outputs a clean markdown report stored in state['final_report'].
"""
import os
from datetime import datetime
from langchain_groq import ChatGroq
from app.state import MedicalState


LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")


def report_agent_node(state: MedicalState) -> dict:
    llm = ChatGroq(model=LLM_MODEL, temperature=0)

    patient_name = state.get("patient_name", "Patient inconnu")
    complaint = state.get("patient_complaint", "")
    qa_pairs = state.get("qa_pairs", [])
    diagnostic_summary = state.get("diagnostic_summary", "")
    interim_care = state.get("interim_care", "")
    physician_treatment = state.get("physician_treatment", "")
    date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")

    qa_text = "\n".join(
        [f"  Q{i+1}: {qa['question']}\n  R: {qa['answer']}" for i, qa in enumerate(qa_pairs)]
    )

    prompt = f"""Tu es un assistant médical rédacteur. 
Génère un rapport médical final structuré en markdown.

Données à intégrer :
- Patient : {patient_name}
- Date : {date_str}
- Plainte initiale : {complaint}
- Questions/Réponses patient :
{qa_text}
- Synthèse clinique préliminaire : {diagnostic_summary}
- Recommandation intermédiaire : {interim_care}
- Traitement / conduite à tenir prescrit par le médecin : {physician_treatment}

Structure du rapport (utilise ces sections exactes) :
# Rapport de Consultation Clinique
## Informations Patient
## Motif de Consultation
## Anamnèse (Questions / Réponses)
## Synthèse Clinique Préliminaire
## Recommandation Intermédiaire
## Traitement et Conduite à Tenir
## Conclusion

OBLIGATOIRE : termine la conclusion par la phrase exacte :
"⚠️ Ce système ne remplace pas une consultation médicale. Ce rapport est généré à titre académique uniquement."

Rédige en français, de manière professionnelle et structurée."""

    response = llm.invoke([{"role": "user", "content": prompt}])

    return {
        "final_report": response.content,
        "next": "FINISH",
    }
