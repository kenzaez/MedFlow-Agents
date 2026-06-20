import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

# =========================================================
# Canvas class for dynamic headers and page numbers
# =========================================================
class TechnicalReportCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_elements(page_count)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        # Page 1: Cover page (no header/footer)
        if self._pageNumber == 1:
            return
            
        self.saveState()
        
        # Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor('#0B1F33'))
        self.drawString(2.5 * cm, 28 * cm, "Rapport de projet d'année")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#6B7280'))
        self.drawRightString(21 * cm - 2.5 * cm, 28 * cm, "Système de Consultation Médicale Multi-Agents")
        
        # Header line
        self.setStrokeColor(colors.HexColor('#E5E7EB'))
        self.setLineWidth(0.5)
        self.line(2.5 * cm, 27.7 * cm, 21 * cm - 2.5 * cm, 27.7 * cm)
        
        # Footer page number
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor('#374151'))
        page_num_str = f"{self._pageNumber}"
        self.drawCentredString(21 * cm / 2.0, 1.5 * cm, page_num_str)
        
        self.restoreState()

# =========================================================
# Main PDF generation logic
# =========================================================
def generate_pdf(output_filename="Rapport_Technique_Systeme_Medical.pdf"):
    # Target size is A4 with 2.5cm margins
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    primary_color = colors.HexColor('#0B1F33')  # Main Blue
    accent_blue = colors.HexColor('#155E75')    # Accent Blue
    accent_teal = colors.HexColor('#0F766E')    # Accent Teal
    dark_gray = colors.HexColor('#374151')      # Dark Gray
    light_gray = colors.HexColor('#F3F4F6')     # Light Gray
    code_bg = colors.HexColor('#F8FAFC')        # Code Background
    border_color = colors.HexColor('#E5E7EB')
    
    # Custom Paragraph Styles
    style_cover_emsi = ParagraphStyle(
        'CoverEMSI',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=TA_CENTER
    )
    style_cover_subemsi = ParagraphStyle(
        'CoverSubEMSI',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=dark_gray,
        alignment=TA_CENTER
    )
    style_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        alignment=TA_CENTER
    )
    style_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=dark_gray,
        alignment=TA_CENTER
    )
    style_heading1 = ParagraphStyle(
        'ChapterHeading',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=18,
        spaceAfter=8,
        keepWithNext=True
    )
    style_heading2 = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=accent_blue,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    style_heading3 = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=dark_gray,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=dark_gray,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    style_body_center = ParagraphStyle(
        'BodyTextCustomCenter',
        parent=style_body,
        alignment=TA_CENTER,
        spaceAfter=8
    )
    style_bullet = ParagraphStyle(
        'BulletCustom',
        parent=style_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    style_code = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )
    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        textColor=colors.white,
        alignment=TA_LEFT
    )
    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=dark_gray,
        alignment=TA_LEFT
    )
    style_legal = ParagraphStyle(
        'LegalCustom',
        parent=style_body,
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=dark_gray,
        alignment=TA_CENTER
    )

    story = []

    # =========================================================
    # PAGE 1: COVER PAGE
    # =========================================================
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("EMSI Casablanca", style_cover_emsi))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("École Marocaine des Sciences de l'Ingénieur<br/>Filière Ingénierie en Intelligence Artificielle & Science des Données", style_cover_subemsi))
    story.append(Spacer(1, 1 * cm))
    
    # Emblem/Logo Placeholder graphic (Drawn using colored blocks)
    logo_data = [[
        Paragraph("<font size=14 color='#ffffff'><b>EMSI</b></font>", ParagraphStyle('LogoTxt', parent=style_body_center, textColor=colors.white))
    ]]
    logo_table = Table(logo_data, colWidths=[2.5*cm], rowHeights=[2.5*cm])
    logo_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(logo_table)
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph("Rapport de fin de module", style_cover_subemsi))
    story.append(Spacer(1, 0.8 * cm))
    
    # Title Rule
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[1.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Système de Consultation Médicale<br/>Multi-Agents", style_title))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Conception d'un système d'orientation clinique préliminaire basé sur LangGraph", style_subtitle))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[1.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 2.5 * cm))
    
    # Author and Supervisor
    names_data = [
        [
            Paragraph("<b>Réalisé par :</b><br/>Kenza Ezzahed<br/>4<sup>ème</sup> année — AI & Data Science", ParagraphStyle('LeftNm', parent=style_body, alignment=TA_LEFT)),
            Paragraph("<b>Encadrant :</b><br/>Khalid El Amraoui", ParagraphStyle('RightNm', parent=style_body, alignment=TA_RIGHT))
        ]
    ]
    names_table = Table(names_data, colWidths=[8*cm, 8*cm])
    names_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(names_table)
    story.append(Spacer(1, 1.8 * cm))
    
    # Tech Stack
    story.append(Paragraph("Python | LangGraph | FastAPI | MCP | Streamlit & Next.js | Groq LLM", style_cover_subemsi))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Juin 2026", style_cover_subemsi))
    story.append(Spacer(1, 0.6 * cm))
    
    # Legal Box
    legal_data = [[Paragraph("Ce système est un exercice académique. Il ne constitue pas un dispositif médical et ne fournit pas de diagnostic définitif. Ce rapport est rédigé à titre pédagogique uniquement.", style_legal)]]
    legal_table = Table(legal_data, colWidths=[14*cm])
    legal_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, primary_color),
        ('BACKGROUND', (0,0), (-1,-1), light_gray),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(legal_table)
    
    story.append(PageBreak())

    # =========================================================
    # PAGE 2: RÉSUMÉ
    # =========================================================
    story.append(Paragraph("Résumé", style_heading1))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[0.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph(
        "Ce rapport présente la conception et l'implémentation d'un système multi-agents d'orientation clinique "
        "préliminaire développé dans le cadre d'un projet académique. Le système repose sur le framework LangGraph pour "
        "orchestrer un workflow collaboratif impliquant quatre agents spécialisés : un Supervisor, un DiagnosticAgent, "
        "un nœud de validation médicale Human-in-the-Loop et un ReportAgent. L'ensemble du pipeline est exposé via "
        "une API FastAPI, enrichi par une intégration du Model Context Protocol (MCP), et accessible au travers de deux "
        "interfaces utilisateur : un prototype rapide en Streamlit et une application web moderne en Next.js. Ce document "
        "décrit l'architecture du système, les choix de conception retenus, ainsi que les modalités d'intégration et de test.",
        style_body
    ))
    
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph("<b>Mots-clés :</b> LangGraph, système multi-agents, Human-in-the-Loop, FastAPI, MCP, Next.js, Streamlit, orientation clinique préliminaire.", style_body))
    
    story.append(PageBreak())

    # =========================================================
    # PAGE 3: TABLE DES MATIÈRES (STATIC)
    # =========================================================
    story.append(Paragraph("Table des matières", style_heading1))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[0.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.5 * cm))
    
    def toc_line(title, page):
        dot_count = 110 - len(title) - len(str(page))
        dots = "." * max(dot_count, 10)
        return Paragraph(f"<b>{title}</b> {dots} <b>{page}</b>", style_body)

    story.append(toc_line("Résumé", "ii"))
    story.append(Spacer(1, 0.15 * cm))
    story.append(toc_line("Chapitre I — Introduction et Contexte", "1"))
    story.append(Paragraph("&nbsp;&nbsp;1.1 Contexte du projet", style_body))
    story.append(Paragraph("&nbsp;&nbsp;1.2 Objectifs pédagogiques", style_body))
    story.append(Paragraph("&nbsp;&nbsp;1.3 Cadre éthique", style_body))
    
    story.append(Spacer(1, 0.15 * cm))
    story.append(toc_line("Chapitre II — Architecture du Système", "2"))
    story.append(Paragraph("&nbsp;&nbsp;2.1 Vue d'ensemble", style_body))
    story.append(Paragraph("&nbsp;&nbsp;2.2 Structure du projet", style_body))
    story.append(Paragraph("&nbsp;&nbsp;2.3 État partagé — MedicalState", style_body))
    
    story.append(Spacer(1, 0.15 * cm))
    story.append(toc_line("Chapitre III — Implémentation des Agents", "4"))
    story.append(Paragraph("&nbsp;&nbsp;3.1 Supervisor", style_body))
    story.append(Paragraph("&nbsp;&nbsp;3.2 Diagnostic Agent", style_body))
    story.append(Paragraph("&nbsp;&nbsp;3.3 Physician Review — Human-in-the-Loop", style_body))
    story.append(Paragraph("&nbsp;&nbsp;3.4 Report Agent", style_body))
    story.append(Paragraph("&nbsp;&nbsp;3.5 Workflow LangGraph", style_body))
    
    story.append(Spacer(1, 0.15 * cm))
    story.append(toc_line("Chapitre IV — Intégration Technique", "6"))
    story.append(Paragraph("&nbsp;&nbsp;4.1 Serveur MCP", style_body))
    story.append(Paragraph("&nbsp;&nbsp;4.2 API FastAPI", style_body))
    story.append(Paragraph("&nbsp;&nbsp;4.3 Interfaces Utilisateurs — Streamlit et Next.js", style_body))
    story.append(Paragraph("&nbsp;&nbsp;4.4 LangGraph Studio", style_body))
    
    story.append(Spacer(1, 0.15 * cm))
    story.append(toc_line("Chapitre V — Tests et Validation", "8"))
    story.append(Paragraph("&nbsp;&nbsp;5.1 Scénarios de test", style_body))
    story.append(Paragraph("&nbsp;&nbsp;5.2 Résultats attendus", style_body))
    story.append(Paragraph("&nbsp;&nbsp;5.3 Choix technologiques", style_body))
    
    story.append(Spacer(1, 0.15 * cm))
    story.append(toc_line("Conclusion et Perspectives", "10"))
    story.append(Spacer(1, 0.15 * cm))
    story.append(toc_line("Annexes", "11"))
    
    story.append(PageBreak())

    # =========================================================
    # CHAPITRE I: INTRODUCTION ET CONTEXTE
    # =========================================================
    story.append(Paragraph("Chapitre I — Introduction et Contexte", style_heading1))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[0.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("1.1 Contexte du projet", style_heading2))
    story.append(Paragraph(
        "Dans le cadre d'un projet académique de systèmes multi-agents, ce travail porte sur la conception d'une "
        "application d'orientation clinique préliminaire basée sur LangGraph. Le système simule un workflow de consultation "
        "médicale piloté par plusieurs agents intelligents : recueil des symptômes, synthèse clinique, validation par un "
        "médecin traitant et génération d'un rapport structuré.",
        style_body
    ))
    story.append(Paragraph(
        "Ce projet ne constitue pas un dispositif médical. Il ne produit aucun diagnostic définitif et s'inscrit "
        "exclusivement dans un objectif pédagogique : maîtriser la conception de workflows multi-agents modernes "
        "avec des interruptions humaines gérées nativement par le framework.",
        style_body
    ))
    
    story.append(Paragraph("1.2 Objectifs pédagogiques", style_heading2))
    story.append(Paragraph("Les objectifs clés définis pour ce projet d'étude sont :", style_body))
    story.append(Paragraph("<bullet>&bull;</bullet>Modéliser un workflow multi-agents avec LangGraph : StateGraph, nœuds, arêtes conditionnelles.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Gérer un état partagé persistant entre plusieurs agents via un TypedDict : MedicalState.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Implémenter le Human-in-the-Loop (HITL) natif via le mécanisme interrupt() de LangGraph.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Exposer le graphe via une API REST FastAPI avec persistance SQLite entre les requêtes.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Intégrer le Model Context Protocol (MCP) comme fournisseur d'outils externes.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Développer deux interfaces utilisateur : Streamlit (Python) et Next.js (React / TypeScript).", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Tester et visualiser le graphe dans LangGraph Studio.", style_bullet))
    
    story.append(Paragraph("1.3 Cadre éthique", style_heading2))
    story.append(Paragraph(
        "Conformément aux recommandations du cahier des charges, le système respecte un cadre éthique strict. La "
        "terminologie utilisée se limite à : orientation clinique préliminaire, synthèse clinique, recommandation "
        "intermédiaire. Chaque rapport généré inclut obligatoirement la mention : « Ce système ne remplace pas une "
        "consultation médicale. » Le médecin traitant valide systématiquement la synthèse avant la génération du rapport "
        "final, et aucun médicament spécifique n'est prescrit par le système.",
        style_body
    ))
    
    story.append(PageBreak())

    # =========================================================
    # CHAPITRE II: ARCHITECTURE DU SYSTÈME
    # =========================================================
    story.append(Paragraph("Chapitre II — Architecture du Système", style_heading1))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[0.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("2.1 Vue d'ensemble", style_heading2))
    story.append(Paragraph(
        "Le système est organisé en plusieurs composants indépendants qui communiquent via HTTP. Cette séparation "
        "en couches permet à chaque composant d'évoluer indépendamment et garantit une bonne séparation des responsabilités.",
        style_body
    ))
    
    # Table 1: Architecture components
    arch_headers = [Paragraph("<b>Composant</b>", style_table_header), Paragraph("<b>Technologie</b>", style_table_header), Paragraph("<b>Port</b>", style_table_header), Paragraph("<b>Rôle</b>", style_table_header)]
    arch_row1 = [Paragraph("Backend", style_table_cell), Paragraph("Python / LangGraph / FastAPI", style_table_cell), Paragraph("8000", style_table_cell), Paragraph("Orchestration multi-agents et API REST", style_table_cell)]
    arch_row2 = [Paragraph("MCP Server", style_table_cell), Paragraph("FastAPI / Python", style_table_cell), Paragraph("8001", style_table_cell), Paragraph("Recommandations cliniques et guidelines", style_table_cell)]
    arch_row3 = [Paragraph("Frontend (Streamlit)", style_table_cell), Paragraph("Streamlit (Python)", style_table_cell), Paragraph("8501", style_table_cell), Paragraph("Prototype d'interface rapide — 4 écrans", style_table_cell)]
    arch_row4 = [Paragraph("Frontend (Next.js)", style_table_cell), Paragraph("Next.js / React / TS / Tailwind", style_table_cell), Paragraph("3000", style_table_cell), Paragraph("Interface web moderne premium — 4 écrans", style_table_cell)]
    
    arch_table = Table([arch_headers, arch_row1, arch_row2, arch_row3, arch_row4], colWidths=[3.2*cm, 4.8*cm, 1.8*cm, 6.2*cm])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 0.6 * cm))
    
    story.append(Paragraph("2.2 Structure du projet", style_heading2))
    story.append(Paragraph(
        "L'arborescence du projet suit la structure recommandée par le cahier des charges, avec une séparation claire "
        "entre backend, MCP server et les deux architectures frontends :",
        style_body
    ))
    
    # Code block block project layout
    struct_code = (
        "project/\n"
        "  backend/\n"
        "    app/\n"
        "      graph.py            <- Definition et compilation du graphe LangGraph\n"
        "      state.py            <- MedicalState (TypedDict partage)\n"
        "      nodes/              <- supervisor, diagnostic_agent, physician_review, report_agent\n"
        "      tools/              <- patient_tools, care_tools, mcp_client\n"
        "      api.py              <- FastAPI (5 endpoints)\n"
        "    langgraph.json        <- Configuration LangGraph Studio\n"
        "    requirements.txt\n"
        "  mcp_server/\n"
        "    server.py             <- Serveur MCP - POST /tools/get_guidelines\n"
        "    requirements.txt\n"
        "  frontend/\n"
        "    app.py                <- Prototype Streamlit - 4 écrans\n"
        "    requirements.txt\n"
        "  frontend2/\n"
        "    app/                  <- Next.js (App Router)\n"
        "      page.tsx            <- Composants d'interface reactive premium\n"
        "      lib/api.ts          <- Service d'appels API (fetch)\n"
        "    package.json\n"
        "  README.md"
    )
    
    code_flow = []
    for line in struct_code.split('\n'):
        code_flow.append(Paragraph(line.replace(' ', '&nbsp;'), style_code))
    code_table = Table([[code_flow]], colWidths=[16*cm])
    code_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), code_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(code_table)
    story.append(Spacer(1, 0.6 * cm))
    
    story.append(Paragraph("2.3 État partagé — MedicalState", style_heading2))
    story.append(Paragraph(
        "L'état partagé constitue la colonne vertébrale du système. Il est défini comme un TypedDict Python et persiste "
        "entre les interruptions grâce au checkpointer SQLite intégré dans LangGraph. Chaque nœud lit et écrit dans cet "
        "état de manière partielle, avec total=False, garantissant un faible couplage.",
        style_body
    ))
    
    # Table 2: MedicalState fields
    state_headers = [Paragraph("<b>Champ</b>", style_table_header), Paragraph("<b>Type Python</b>", style_table_header), Paragraph("<b>Rôle</b>", style_table_header), Paragraph("<b>Écran</b>", style_table_header)]
    state_rows = [
        [Paragraph("messages", style_table_cell), Paragraph("Annotated[list]", style_table_cell), Paragraph("Messages LangChain, append-only via add_messages", style_table_cell), Paragraph("—", style_table_cell)],
        [Paragraph("next", style_table_cell), Paragraph("Literal[...]", style_table_cell), Paragraph("Clé de routage lue par le Supervisor", style_table_cell), Paragraph("—", style_table_cell)],
        [Paragraph("patient_name", style_table_cell), Paragraph("str", style_table_cell), Paragraph("Nom du patient saisi à l'écran 1", style_table_cell), Paragraph("1", style_table_cell)],
        [Paragraph("patient_complaint", style_table_cell), Paragraph("str", style_table_cell), Paragraph("Plainte initiale du patient", style_table_cell), Paragraph("1", style_table_cell)],
        [Paragraph("qa_pairs", style_table_cell), Paragraph("List[QAPair]", style_table_cell), Paragraph("5 paires question / réponse accumulées", style_table_cell), Paragraph("2", style_table_cell)],
        [Paragraph("question_count", style_table_cell), Paragraph("int", style_table_cell), Paragraph("Nombre de questions posées (de 0 à 5)", style_table_cell), Paragraph("2", style_table_cell)],
        [Paragraph("diagnostic_summary", style_table_cell), Paragraph("str", style_table_cell), Paragraph("Synthèse clinique préliminaire générée par LLM", style_table_cell), Paragraph("3", style_table_cell)],
        [Paragraph("interim_care", style_table_cell), Paragraph("str", style_table_cell), Paragraph("Recommandation intermédiaire (appel tool)", style_table_cell), Paragraph("3", style_table_cell)],
        [Paragraph("physician_treatment", style_table_cell), Paragraph("str", style_table_cell), Paragraph("Traitement prescrit par le médecin", style_table_cell), Paragraph("3", style_table_cell)],
        [Paragraph("final_report", style_table_cell), Paragraph("str", style_table_cell), Paragraph("Rapport final markdown en 7 sections", style_table_cell), Paragraph("4", style_table_cell)]
    ]
    
    state_table = Table([state_headers] + state_rows, colWidths=[3.2*cm, 3.2*cm, 8.4*cm, 1.2*cm])
    state_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(state_table)
    
    story.append(PageBreak())

    # =========================================================
    # CHAPITRE III: IMPLÉMENTATION DES AGENTS
    # =========================================================
    story.append(Paragraph("Chapitre III — Implémentation des Agents", style_heading1))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[0.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("Vue d'ensemble des agents", style_heading2))
    
    # Table 3: Agents overview
    agents_headers = [Paragraph("<b>Agent</b>", style_table_header), Paragraph("<b>Fichier</b>", style_table_header), Paragraph("<b>Responsabilité</b>", style_table_header), Paragraph("<b>Appel LLM</b>", style_table_header)]
    agents_rows = [
        [Paragraph("Supervisor", style_table_cell), Paragraph("supervisor.py", style_table_cell), Paragraph("Routeur déterministe — analyse l'état et route vers le nœud suivant", style_table_cell), Paragraph("Non", style_table_cell)],
        [Paragraph("DiagnosticAgent", style_table_cell), Paragraph("diagnostic_agent.py", style_table_cell), Paragraph("Pose 5 questions via interrupt(), génère synthèse et recommandations", style_table_cell), Paragraph("Oui", style_table_cell)],
        [Paragraph("PhysicianReview", style_table_cell), Paragraph("physician_review.py", style_table_cell), Paragraph("Nœud HITL — suspend le graphe, attend le traitement médecin", style_table_cell), Paragraph("Non", style_table_cell)],
        [Paragraph("ReportAgent", style_table_cell), Paragraph("report_agent.py", style_table_cell), Paragraph("Assemble le rapport final structuré en 7 sections markdown", style_table_cell), Paragraph("Oui", style_table_cell)]
    ]
    
    agents_table = Table([agents_headers] + agents_rows, colWidths=[3.0*cm, 3.2*cm, 8.3*cm, 1.5*cm])
    agents_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(agents_table)
    story.append(Spacer(1, 0.4 * cm))
    
    story.append(Paragraph("3.1 Supervisor", style_heading2))
    story.append(Paragraph(
        "Le Supervisor est le nœud central du graphe. Il joue le rôle de routeur déterministe : il lit l'état partagé et "
        "décide, sans appel au LLM, vers quel nœud diriger le flux d'exécution. Ce choix de conception garantit un "
        "comportement entièrement prévisible et facilement testable, qualité essentielle dans un contexte où la fiabilité "
        "du routage est critique.",
        style_body
    ))
    story.append(Paragraph("<b>Logique de routage :</b>", style_body))
    story.append(Paragraph("<bullet>&bull;</bullet>Si <i>final_report</i> est présent &rarr; FINISH (consultation terminée).", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Si <i>physician_treatment</i> et <i>diagnostic_summary</i> sont présents &rarr; <i>report_agent</i>.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Si <i>diagnostic_summary</i> est présent &rarr; <i>physician_review</i>.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Sinon, état initial &rarr; <i>diagnostic_agent</i>.", style_bullet))
    
    story.append(Paragraph("3.2 Diagnostic Agent", style_heading2))
    story.append(Paragraph(
        "Le DiagnosticAgent est l'agent principal d'anamnèse. Il utilise un modèle de langage (Groq / LLaMA-3.3-70b avec "
        "temperature=0) pour générer cinq questions cliniques adaptées à la plainte du patient. Chaque question est "
        "posée individuellement via le mécanisme interrupt() de LangGraph, qui suspend le graphe, persiste l'état "
        "complet via SQLite, et attend la réponse du patient via l'API.",
        style_body
    ))
    story.append(Paragraph(
        "L'utilisation de la température 0 est capitale : lors du rejeu LangGraph après chaque interruption, le nœud "
        "est ré-exécuté depuis le début, et les questions générées dynamiquement doivent rester strictement identiques "
        "pour que la boucle d'anamnèse s'apparie correctement avec les réponses déjà stockées dans l'état.",
        style_body
    ))
    
    story.append(Paragraph("3.3 Physician Review — Human-in-the-Loop", style_heading2))
    story.append(Paragraph(
        "Le nœud PhysicianReview implémente la validation humaine obligatoire (Human-in-the-Loop) représentant le médecin "
        "traitant. Il suspend le graphe et présente au médecin la synthèse clinique préliminaire (<i>diagnostic_summary</i>) "
        "ainsi que la recommandation intermédiaire (<i>interim_care</i>). Le médecin saisit son traitement ou sa conduite "
        "à tenir, qui est transmis au graphe via POST /consultation/resume et stocké dans <i>physician_treatment</i>.",
        style_body
    ))
    
    story.append(Paragraph("3.4 Report Agent", style_heading2))
    story.append(Paragraph(
        "Le ReportAgent génère le rapport final structuré en markdown en sept sections prédéfinies : Informations Patient, "
        "Motif de Consultation, Anamnèse (Questions / Réponses), Synthèse Clinique Préliminaire, Recommandation Intermédiaire, "
        "Traitement et Conduite à Tenir, Conclusion. Le rapport se termine obligatoirement par la mention légale : "
        "« ⚠️ Ce système ne remplace pas une consultation médicale. Ce rapport est généré à titre académique uniquement. »",
        style_body
    ))
    
    story.append(PageBreak())

    # =========================================================
    # IMPLÉMENTATION DES AGENTS (WORKFLOW)
    # =========================================================
    story.append(Paragraph("3.5 Workflow LangGraph", style_heading2))
    story.append(Paragraph(
        "Le tableau suivant décrit la séquence complète du workflow, des transitions entre nœuds et des points "
        "d'interruption HITL.",
        style_body
    ))
    
    # Table 4: Workflow steps
    wf_headers = [Paragraph("<b>Étape</b>", style_table_header), Paragraph("<b>Nœud / Action</b>", style_table_header), Paragraph("<b>Type</b>", style_table_header), Paragraph("<b>Description</b>", style_table_header)]
    wf_rows = [
        [Paragraph("1", style_table_cell), Paragraph("START &rarr; Supervisor", style_table_cell), Paragraph("Entrée", style_table_cell), Paragraph("Initialisation avec patient_name et patient_complaint.", style_table_cell)],
        [Paragraph("2", style_table_cell), Paragraph("Supervisor", style_table_cell), Paragraph("Routeur", style_table_cell), Paragraph("Analyse de l'état : aucun champ rempli &rarr; route vers DiagnosticAgent.", style_table_cell)],
        [Paragraph("3", style_table_cell), Paragraph("DiagnosticAgent", style_table_cell), Paragraph("Agent LLM", style_table_cell), Paragraph("Génération de 5 questions adaptées via LLM (temp=0).", style_table_cell)],
        [Paragraph("4", style_table_cell), Paragraph("interrupt() &times; 5", style_table_cell), Paragraph("HITL", style_table_cell), Paragraph("Pause graphe — le patient répond aux questions via l'API.", style_table_cell)],
        [Paragraph("5", style_table_cell), Paragraph("MCP : get_medical_guidelines", style_table_cell), Paragraph("Tool MCP", style_table_cell), Paragraph("Récupération des recommandations externes basées sur les symptômes.", style_table_cell)],
        [Paragraph("6", style_table_cell), Paragraph("recommend_interim_care", style_table_cell), Paragraph("Tool", style_table_cell), Paragraph("Génération d'une recommandation intermédiaire de prudence.", style_table_cell)],
        [Paragraph("7", style_table_cell), Paragraph("DiagnosticAgent &rarr; Supervisor", style_table_cell), Paragraph("Transition", style_table_cell), Paragraph("Mise à jour de la synthèse et des recommandations dans l'état.", style_table_cell)],
        [Paragraph("8", style_table_cell), Paragraph("Supervisor", style_table_cell), Paragraph("Routeur", style_table_cell), Paragraph("diagnostic_summary présent &rarr; route vers PhysicianReview.", style_table_cell)],
        [Paragraph("9", style_table_cell), Paragraph("interrupt() &times; 1", style_table_cell), Paragraph("HITL", style_table_cell), Paragraph("Pause graphe — le médecin saisit et valide son traitement.", style_table_cell)],
        [Paragraph("10", style_table_cell), Paragraph("PhysicianReview &rarr; Supervisor", style_table_cell), Paragraph("Transition", style_table_cell), Paragraph("physician_treatment mis à jour dans l'état partagé.", style_table_cell)],
        [Paragraph("11", style_table_cell), Paragraph("Supervisor", style_table_cell), Paragraph("Routeur", style_table_cell), Paragraph("physician_treatment présent &rarr; route vers ReportAgent.", style_table_cell)],
        [Paragraph("12", style_table_cell), Paragraph("ReportAgent", style_table_cell), Paragraph("Agent LLM", style_table_cell), Paragraph("Génération du rapport final structuré en 7 sections markdown.", style_table_cell)],
        [Paragraph("13", style_table_cell), Paragraph("ReportAgent &rarr; Supervisor", style_table_cell), Paragraph("Transition", style_table_cell), Paragraph("final_report mis à jour dans l'état partagé.", style_table_cell)],
        [Paragraph("14", style_table_cell), Paragraph("Supervisor &rarr; END", style_table_cell), Paragraph("Fin", style_table_cell), Paragraph("Rapport final présent &rarr; arrêt complet de la consultation.", style_table_cell)]
    ]
    
    wf_table = Table([wf_headers] + wf_rows, colWidths=[1.1*cm, 4.0*cm, 2.0*cm, 8.9*cm])
    wf_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(wf_table)
    
    story.append(PageBreak())

    # =========================================================
    # CHAPITRE IV: INTÉGRATION TECHNIQUE
    # =========================================================
    story.append(Paragraph("Chapitre IV — Intégration Technique", style_heading1))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[0.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("4.1 Serveur MCP", style_heading2))
    story.append(Paragraph(
        "L'intégration du Model Context Protocol (MCP) est réalisée via un serveur FastAPI dédié, port 8001. Ce serveur joue "
        "le rôle de fournisseur d'outils externes : il expose un endpoint POST /tools/get_guidelines qui, à partir de mots-clés "
        "de symptômes, retourne des recommandations d'orientation clinique générales issues d'une base de connaissances codée "
        "en dur, avec 15 conditions courantes.",
        style_body
    ))
    story.append(Paragraph(
        "Le client MCP, mcp_client.py, intègre une gestion d'erreur robuste : en cas d'indisponibilité du serveur, "
        "ConnectError ou TimeoutException, le DiagnosticAgent continue son exécution avec un message de fallback, sans "
        "interrompre le workflow principal.",
        style_body
    ))
    
    # Table 5: MCP Integration
    mcp_headers = [Paragraph("<b>Composant</b>", style_table_header), Paragraph("<b>Action</b>", style_table_header), Paragraph("<b>Détail</b>", style_table_header)]
    mcp_rows = [
        [Paragraph("DiagnosticAgent", style_table_cell), Paragraph("Appelle get_medical_guidelines", style_table_cell), Paragraph("Après la collecte des 5 réponses, avant la synthèse LLM.", style_table_cell)],
        [Paragraph("mcp_client.py", style_table_cell), Paragraph("POST /tools/get_guidelines", style_table_cell), Paragraph("httpx, timeout 10s, fallback gracieux si indisponible.", style_table_cell)],
        [Paragraph("mcp_server/", style_table_cell), Paragraph("Match keywords &rarr; guidelines", style_table_cell), Paragraph("15 conditions courantes : fièvre, toux, douleur thoracique, etc.", style_table_cell)]
    ]
    mcp_table = Table([mcp_headers] + mcp_rows, colWidths=[3.5*cm, 4.5*cm, 8.0*cm])
    mcp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(mcp_table)
    story.append(Spacer(1, 0.4 * cm))
    
    story.append(Paragraph("4.2 API FastAPI", style_heading2))
    story.append(Paragraph(
        "L'API REST expose le graphe LangGraph via cinq endpoints qui couvrent l'intégralité du cycle de vie d'une "
        "consultation. La communication des interruptions entre le frontend et le graphe est gérée via le mécanisme "
        "Command(resume=user_input) de LangGraph, associé à la persistance SQLite.",
        style_body
    ))
    
    # Table 6: API endpoints
    api_headers = [Paragraph("<b>Méthode</b>", style_table_header), Paragraph("<b>Endpoint</b>", style_table_header), Paragraph("<b>Corps / Réponse</b>", style_table_header)]
    api_rows = [
        [Paragraph("POST", style_table_cell), Paragraph("/sessions/start", style_table_cell), Paragraph("Réponse : {thread_id: UUID}", style_table_cell)],
        [Paragraph("POST", style_table_cell), Paragraph("/consultation/start", style_table_cell), Paragraph("Corps : {patient_name, patient_complaint} | Réponse : status + question ou completed", style_table_cell)],
        [Paragraph("POST", style_table_cell), Paragraph("/consultation/resume", style_table_cell), Paragraph("Corps : {thread_id, user_input} | Réponse : status + données selon phase", style_table_cell)],
        [Paragraph("GET", style_table_cell), Paragraph("/consultation/{thread_id}", style_table_cell), Paragraph("Réponse : snapshot état complet + interruption courante", style_table_cell)],
        [Paragraph("GET", style_table_cell), Paragraph("/consultation/{thread_id}/report", style_table_cell), Paragraph("Réponse : final_report markdown | 202 si non terminé", style_table_cell)]
    ]
    api_table = Table([api_headers] + api_rows, colWidths=[2.2*cm, 5.0*cm, 8.8*cm])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(api_table)
    
    story.append(PageBreak())

    # =========================================================
    # INTÉGRATION TECHNIQUE (FRONTENDS & STUDIO)
    # =========================================================
    story.append(Paragraph("4.3 Interfaces Utilisateurs — Streamlit et Next.js", style_heading2))
    story.append(Paragraph(
        "Pour répondre aux différents besoins de déploiement et d'évaluation, deux interfaces frontends distinctes ont été "
        "réalisées, toutes deux structurées autour du même cycle à quatre écrans successifs.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Streamlit (port 8501) :</b> Interface écrite en Python pur, permettant un prototypage immédiat et une intégration "
        "directe avec l'API FastAPI pour l'évaluation interne.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Next.js (port 3000) :</b> Application monopage (SPA) moderne écrite en React/TypeScript et stylisée avec Tailwind CSS. "
        "Elle intègre des animations de chargement fluides (sonner, Lucide icons), des indicateurs d'étapes circulaires "
        "réactifs, et un rendu optimal du markdown.",
        style_body
    ))
    
    # Table 7: Frontend screens
    fe_headers = [Paragraph("<b>Écran</b>", style_table_header), Paragraph("<b>État, step</b>", style_table_header), Paragraph("<b>Description fonctionnelle</b>", style_table_header)]
    fe_rows = [
        [Paragraph("Écran 1 — Saisie Patient", style_table_cell), Paragraph("\"input\"", style_table_cell), Paragraph("Formulaire nom + plainte. POST /consultation/start. Redirige vers Écran 2.", style_table_cell)],
        [Paragraph("Écran 2 — Questions Médicales", style_table_cell), Paragraph("\"qna\"", style_table_cell), Paragraph("Progress bar Q1/5 à Q5/5. POST /consultation/resume x 5. Redirige vers Écran 3.", style_table_cell)],
        [Paragraph("Écran 3 — Revue Médecin", style_table_cell), Paragraph("\"physician\"", style_table_cell), Paragraph("Affiche synthèse + interim_care. Saisie traitement. POST /consultation/resume.", style_table_cell)],
        [Paragraph("Écran 4 — Rapport Final", style_table_cell), Paragraph("\"report\"", style_table_cell), Paragraph("Rapport markdown complet. Téléchargement .txt et réinitialisation.", style_table_cell)]
    ]
    fe_table = Table([fe_headers] + fe_rows, colWidths=[4.0*cm, 3.0*cm, 9.0*cm])
    fe_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(fe_table)
    story.append(Spacer(1, 0.4 * cm))
    
    story.append(Paragraph("4.4 LangGraph Studio", style_heading2))
    story.append(Paragraph(
        "Le graphe est configuré pour LangGraph Studio via le fichier langgraph.json situé à la racine du dossier backend. "
        "La fonction build_graph() exporte le StateGraph non compilé, sans checkpointer, car LangGraph Studio gère sa propre "
        "persistance. La fonction compile_graph() avec SQLite est réservée à l'API FastAPI.",
        style_body
    ))
    
    # Code block langgraph.json
    lg_json_code = (
        "{\n"
        "  \"dependencies\": [\".\"],\n"
        "  \"graphs\": {\n"
        "    \"medical_consultation\": \"./app/graph.py:build_graph\"\n"
        "  },\n"
        "  \"env\": \".env\"\n"
        "}"
    )
    code_flow_lg = []
    for line in lg_json_code.split('\n'):
        code_flow_lg.append(Paragraph(line.replace(' ', '&nbsp;'), style_code))
    lg_code_table = Table([[code_flow_lg]], colWidths=[16*cm])
    lg_code_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), code_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(lg_code_table)
    
    story.append(PageBreak())

    # =========================================================
    # CHAPITRE V: TESTS ET VALIDATION
    # =========================================================
    story.append(Paragraph("Chapitre V — Tests et Validation", style_heading1))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[0.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("5.1 Scénarios de test", style_heading2))
    story.append(Paragraph(
        "Trois scénarios de test sont définis pour couvrir les cas d'usage typiques du système. Pour chaque scénario, "
        "le test vérifie la pose des 5 questions, la génération de la recommandation intermédiaire, le bon fonctionnement "
        "de l'interruption médecin et la production du rapport final.",
        style_body
    ))
    
    # Table 8: Test scenarios
    test_headers = [Paragraph("<b>Cas</b>", style_table_header), Paragraph("<b>Plainte initiale</b>", style_table_header), Paragraph("<b>Interim care attendu</b>", style_table_header), Paragraph("<b>Résultat attendu</b>", style_table_header)]
    test_rows = [
        [Paragraph("Cas 1 — Syndrome respiratoire simple", style_table_cell), Paragraph("Toux sèche et fièvre légère depuis 3 jours", style_table_cell), Paragraph("Repos, hydratation, paracétamol si T &gt; 38.5 °C", style_table_cell), Paragraph("Rapport : orientation médecin généraliste", style_table_cell)],
        [Paragraph("Cas 2 — Red Flags, urgence cardiaque", style_table_cell), Paragraph("Douleur thoracique intense, difficultés à respirer", style_table_cell), Paragraph("URGENCE — Appeler le 15/SAMU immédiatement", style_table_cell), Paragraph("Red flags détectés, orientation services d'urgence", style_table_cell)],
        [Paragraph("Cas 3 — Cas bénin, fatigue", style_table_cell), Paragraph("Légère fatigue sans fièvre depuis 1 semaine", style_table_cell), Paragraph("Repos, hydratation, bilan sanguin si persistance", style_table_cell), Paragraph("Rapport bénin sans urgence, conseils d'hygiène", style_table_cell)]
    ]
    test_table = Table([test_headers] + test_rows, colWidths=[3.2*cm, 4.0*cm, 4.3*cm, 4.5*cm])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(test_table)
    story.append(Spacer(1, 0.4 * cm))
    
    story.append(Paragraph("5.2 Résultats attendus", style_heading2))
    story.append(Paragraph("Pour chaque scénario, la validation porte sur les critères de succès suivants :", style_body))
    story.append(Paragraph("<bullet>&bull;</bullet>Exactement 5 questions générées et posées successivement au patient.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Synthèse clinique préliminaire produite par le LLM après la collecte des réponses.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Recommandation intermédiaire prudente générée par le tool recommend_interim_care.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Interruption médecin fonctionnelle avec affichage de la synthèse et recommandation.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Rapport final structuré en 7 sections avec mention légale obligatoire.", style_bullet))
    story.append(Paragraph("<bullet>&bull;</bullet>Cas 2 : détection explicite des red flags et recommandation d'urgence dans interim_care.", style_bullet))
    story.append(Spacer(1, 0.2 * cm))
    
    story.append(Paragraph("5.3 Choix technologiques", style_heading2))
    
    # Table 9: Choices
    choice_headers = [Paragraph("<b>Technologie</b>", style_table_header), Paragraph("<b>Rôle</b>", style_table_header), Paragraph("<b>Justification du choix</b>", style_table_header)]
    choice_rows = [
        [Paragraph("LangGraph &ge; 0.2.28", style_table_cell), Paragraph("Framework multi-agents", style_table_cell), Paragraph("HITL natif via interrupt(), persistance SQLite, support Studio.", style_table_cell)],
        [Paragraph("Groq / LLaMA-3.3-70b", style_table_cell), Paragraph("Modèle LLM principal", style_table_cell), Paragraph("Inférence ultra-rapide (&lt; 2s), temp=0 pour cohérence au rejeu.", style_table_cell)],
        [Paragraph("SQLite checkpointer", style_table_cell), Paragraph("Persistance", style_table_cell), Paragraph("Léger, sans serveur de base de données, persistance des threads.", style_table_cell)],
        [Paragraph("FastAPI / Uvicorn", style_table_cell), Paragraph("API REST", style_table_cell), Paragraph("Validation Pydantic, doc OpenAPI auto, performances asynchrones.", style_table_cell)],
        [Paragraph("Next.js &ge; 15 / React", style_table_cell), Paragraph("Frontend (Premium)", style_table_cell), Paragraph("Interface web réactive haute performance, typage statique TypeScript.", style_table_cell)],
        [Paragraph("Streamlit", style_table_cell), Paragraph("Frontend (Prototype)", style_table_cell), Paragraph("Itération et prototypage ultra-rapide en Python pur.", style_table_cell)],
        [Paragraph("httpx", style_table_cell), Paragraph("Client MCP", style_table_cell), Paragraph("Timeout configurable, gestion d'erreur propre pour les appels MCP.", style_table_cell)]
    ]
    choice_table = Table([choice_headers] + choice_rows, colWidths=[3.5*cm, 3.5*cm, 9.0*cm])
    choice_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(choice_table)
    
    story.append(PageBreak())

    # =========================================================
    # CONCLUSION ET PERSPECTIVES
    # =========================================================
    story.append(Paragraph("Conclusion et Perspectives", style_heading1))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[0.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("Bilan", style_heading2))
    story.append(Paragraph(
        "Ce projet a permis de concevoir et d'implémenter un système complet de consultation médicale multi-agents, en mobilisant "
        "les technologies les plus récentes du domaine des agents internes. L'ensemble du pipeline — de la saisie initiale du "
        "patient jusqu'à la génération du rapport final — est orchestré par LangGraph, un framework qui a démontré toute sa puissance "
        "pour modéliser des workflows complexes avec des états partagés et des interruptions humaines.",
        style_body
    ))
    
    story.append(Paragraph("Architecture et conception", style_heading2))
    story.append(Paragraph(
        "L'architecture retenue repose sur quatre agents spécialisés communiquant exclusivement via l'état partagé MedicalState. "
        "Ce choix garantit un faible couplage entre les composants et facilite la maintenance et l'évolution du système. Le "
        "Supervisor, conçu comme un routeur déterministe sans appel LLM, assure un comportement entièrement prévisible et testable, "
        "qualité essentielle dans un contexte où la fiabilité du routage est critique.",
        style_body
    ))
    
    story.append(Paragraph("Human-in-the-Loop", style_heading2))
    story.append(Paragraph(
        "L'intégration du Human-in-the-Loop via le mécanisme natif interrupt() de LangGraph constitue l'un des points forts "
        "de cette architecture. Cette approche permet de suspendre le graphe proprement, de persister l'état complet grâce "
        "au checkpointer SQLite, et de reprendre exactement où le workflow s'était arrêté. Ce mécanisme garantit la fiabilité "
        "du processus dans un contexte où les interactions humaines sont par nature asynchrones.",
        style_body
    ))
    
    story.append(Paragraph("Respect du cadre éthique", style_heading2))
    story.append(Paragraph(
        "Sur le plan éthique, toutes les contraintes du cahier des charges ont été scrupuleusement respectées : aucun diagnostic "
        "définitif, terminologie limitée à l'orientation clinique préliminaire, mention légale obligatoire dans chaque rapport, "
        "et validation systématique par un médecin traitant avant la génération du rapport final.",
        style_body
    ))
    
    story.append(Paragraph("Perspectives", style_heading2))
    story.append(Paragraph(
        "En perspective, ce système pourrait être enrichi par : l'export du rapport au format PDF, la persistance historique "
        "des consultations en base de données relationnelle, des tests unitaires et d'intégration automatisés, ainsi qu'une "
        "conteneurisation Docker pour faciliter le déploiement. Ces extensions constitueraient une feuille de route naturelle "
        "pour porter ce prototype académique vers un niveau de maturité industrielle.",
        style_body
    ))
    
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("<i>Ce système est un exercice académique. Il ne constitue pas un dispositif médical et ne fournit pas de diagnostic définitif. Ce rapport est rédigé à titre pédagogique uniquement.</i>", style_body_center))
    
    story.append(PageBreak())

    # =========================================================
    # ANNEXE A: CAPTURES D'ÉCRAN
    # =========================================================
    story.append(Paragraph("Annexe A — Captures d'écran : Interface Utilisateur", style_heading1))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[0.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("Les figures suivantes représentent des emplacements réservés pour les captures d'écran de l'interface lors de la démonstration finale.", style_body))
    story.append(Spacer(1, 0.4 * cm))
    
    def placeholder_box(label):
        p_cell = Paragraph(f"<font color='#6B7280'>[ Emplacement capture d'écran ]<br/><b>{label}</b></font>", style_body_center)
        p_table = Table([[p_cell]], colWidths=[14*cm], rowHeights=[4.0*cm])
        p_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_gray),
            ('BOX', (0,0), (-1,-1), 1.0, primary_color),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return p_table

    story.append(Paragraph("<b>Écran 1 — Saisie du Cas Patient (step = \"input\")</b>", style_heading2))
    story.append(placeholder_box("Saisie du nom et de la plainte initiale"))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("<b>Écran 2 — Questions Médicales, Q/R (step = \"qna\")</b>", style_heading2))
    story.append(placeholder_box("Visualisation d'une question en cours d'anamnèse"))
    
    story.append(PageBreak())
    
    story.append(Paragraph("<b>Écran 3 — Revue Médecin Traitant (step = \"physician\")</b>", style_heading2))
    story.append(placeholder_box("Interface médecin avec synthèse et conduite à tenir"))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("<b>Écran 4 — Rapport Final (step = \"report\")</b>", style_heading2))
    story.append(placeholder_box("Rapport final généré avec mention légale visible"))
    
    story.append(PageBreak())

    # =========================================================
    # ANNEXE B: LANGGRAPH STUDIO
    # =========================================================
    story.append(Paragraph("Annexe B — Captures d'écran : LangGraph Studio", style_heading1))
    story.append(Table([[""]], colWidths=[16*cm], rowHeights=[0.5], style=[('BACKGROUND', (0,0), (-1,-1), primary_color)]))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("Les figures suivantes représentent des emplacements réservés pour les captures d'écran de l'environnement de développement LangGraph Studio.", style_body))
    story.append(Spacer(1, 0.4 * cm))
    
    story.append(Paragraph("<b>Vue Globale du Graphe LangGraph Studio</b>", style_heading2))
    story.append(placeholder_box("Visualisation des nœuds et des arêtes conditionnelles"))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("<b>Interruption Patient — interrupt() actif</b>", style_heading2))
    story.append(placeholder_box("Graphe suspendu sur le nœud diagnostic_agent"))
    
    story.append(PageBreak())
    
    story.append(Paragraph("<b>Interruption Médecin — Human-in-the-Loop</b>", style_heading2))
    story.append(placeholder_box("Graphe suspendu sur le nœud physician_review"))
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("<b>État Final — Rapport généré</b>", style_heading2))
    story.append(placeholder_box("Visualisation de l'état final et fin du graphe"))

    # Build the document
    doc.build(story, canvasmaker=TechnicalReportCanvas)
    print(f"Successfully generated PDF: {output_filename}")

if __name__ == "__main__":
    generate_pdf()
