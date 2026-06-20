"""
MCP Server — Medical Guidelines Provider
-----------------------------------------
A simple FastAPI server that acts as an MCP (Model Context Protocol) tool provider.
The backend's mcp_client.py calls POST /tools/get_guidelines to fetch
general medical orientation guidelines based on symptom keywords.

Run:
    uvicorn server:app --host 0.0.0.0 --port 8001 --reload
"""
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="MCP Server — Medical Guidelines",
    description="Fournit des recommandations d'orientation clinique générales.",
    version="1.0.0",
)


# ── Hardcoded guidelines dictionary ─────────────────────────────────────────

GUIDELINES_DB: dict[str, str] = {
    "fièvre": (
        "Repos recommandé, hydratation abondante (eau, tisanes), "
        "surveillance de la température toutes les 4 heures. "
        "Paracétamol si T > 38.5 °C. Consulter si fièvre > 39 °C persistante "
        "ou si signes d'alerte (raideur de nuque, confusion)."
    ),
    "toux": (
        "Éviter l'air sec, maintenir une bonne hydratation. "
        "Miel et boissons chaudes pour soulager l'irritation. "
        "Consulter si persistance > 7 jours, expectoration colorée, "
        "ou difficultés respiratoires associées."
    ),
    "douleur thoracique": (
        "⚠️ Consulter immédiatement un médecin ou appeler les urgences. "
        "Peut indiquer une urgence cardiaque (infarctus, embolie pulmonaire). "
        "Ne pas faire d'effort physique. "
        "Prendre de l'aspirine 300 mg si suspicion cardiaque (sauf allergie)."
    ),
    "maux de tête": (
        "Repos dans une pièce sombre et calme, hydratation suffisante. "
        "Paracétamol en première intention. "
        "Consulter si céphalées brutales intenses ('coup de tonnerre'), "
        "si accompagnées de fièvre élevée, raideur de nuque ou troubles visuels."
    ),
    "diarrhée": (
        "Réhydratation orale prioritaire (eau, solutés de réhydratation). "
        "Éviter les aliments lourds, gras et les produits laitiers. "
        "Régime BRAT recommandé (bananes, riz, compote, toast). "
        "Consulter si sang dans les selles, fièvre élevée ou durée > 3 jours."
    ),
    "fatigue": (
        "Repos suffisant, hygiène du sommeil, alimentation équilibrée. "
        "Bilan sanguin recommandé si persistance > 2 semaines "
        "(NFS, ferritine, TSH, glycémie). "
        "Rechercher causes sous-jacentes : anémie, hypothyroïdie, dépression."
    ),
    "nausée": (
        "Repas légers et fractionnés, éviter les odeurs fortes. "
        "Gingembre ou menthe poivrée peuvent soulager. "
        "Consulter si vomissements persistants, déshydratation, "
        "ou si associée à des douleurs abdominales intenses."
    ),
    "vomissement": (
        "Réhydratation progressive par petites gorgées. "
        "Jeûne court puis reprise alimentaire légère. "
        "Consulter en urgence si vomissements de sang, "
        "si associés à une douleur abdominale aiguë ou si durée > 24 h."
    ),
    "douleur abdominale": (
        "Repos, éviter les repas copieux, application de chaleur locale. "
        "Consulter si douleur aiguë intense, fièvre associée, "
        "défense abdominale ou sang dans les selles. "
        "Urgence si douleur brutale en coup de poignard."
    ),
    "éruption cutanée": (
        "Éviter de gratter, appliquer une crème hydratante ou apaisante. "
        "Antihistaminique si prurit important. "
        "Consulter si fièvre associée, extension rapide, "
        "ou si vésicules/cloques suspectes."
    ),
    "essoufflement": (
        "⚠️ Consultation urgente recommandée. "
        "Position assise ou semi-assise pour faciliter la respiration. "
        "Peut indiquer asthme, pneumonie, embolie pulmonaire. "
        "Appeler les urgences si dyspnée sévère ou cyanose."
    ),
    "vertiges": (
        "S'allonger immédiatement pour éviter les chutes. "
        "Hydratation, éviter les mouvements brusques. "
        "Consulter si vertiges rotatoires persistants, perte auditive, "
        "ou si associés à des troubles neurologiques."
    ),
    "mal de gorge": (
        "Gargarismes à l'eau salée tiède, hydratation, pastilles pour la gorge. "
        "Paracétamol pour la douleur. "
        "Consulter si difficulté à avaler, fièvre > 38.5 °C persistante, "
        "ou si durée > 5 jours (test streptocoque recommandé)."
    ),
    "insomnie": (
        "Hygiène du sommeil : horaires réguliers, éviter les écrans 1 h avant le coucher, "
        "chambre fraîche et sombre. Limiter caféine après 14 h. "
        "Techniques de relaxation (respiration, méditation). "
        "Consulter si persistance > 3 semaines."
    ),
    "anxiété": (
        "Techniques de respiration profonde (cohérence cardiaque 3-6-5). "
        "Activité physique régulière, réduction des stimulants. "
        "Consulter un professionnel si anxiété invalidante, "
        "attaques de panique, ou retentissement sur la vie quotidienne."
    ),
}

FALLBACK_GUIDELINE = (
    "Aucune recommandation spécifique trouvée pour ces symptômes. "
    "Recommandation générale : repos, hydratation, surveillance de l'évolution. "
    "Consulter un professionnel de santé si les symptômes persistent ou s'aggravent."
)


# ── Pydantic models ─────────────────────────────────────────────────────────

class GuidelinesRequest(BaseModel):
    keywords: str


class GuidelinesResponse(BaseModel):
    guidelines: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/tools/get_guidelines", response_model=GuidelinesResponse)
async def get_guidelines(body: GuidelinesRequest):
    """
    Match keywords against the conditions dictionary and return
    concatenated clinical orientation guidelines.
    """
    keywords_lower = body.keywords.lower()
    matched: list[str] = []

    for condition, guideline in GUIDELINES_DB.items():
        if condition in keywords_lower:
            matched.append(f"**{condition.capitalize()}** : {guideline}")

    if matched:
        guidelines_text = "\n\n".join(matched)
    else:
        guidelines_text = FALLBACK_GUIDELINE

    return GuidelinesResponse(guidelines=guidelines_text)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/tools")
async def list_tools():
    """Lists all available MCP tools."""
    return {
        "tools": [
            {
                "name": "get_guidelines",
                "description": (
                    "Retourne des recommandations d'orientation clinique "
                    "générales basées sur des mots-clés de symptômes."
                ),
                "endpoint": "POST /tools/get_guidelines",
                "input_schema": {"keywords": "string"},
                "output_schema": {"guidelines": "string"},
            }
        ]
    }


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
