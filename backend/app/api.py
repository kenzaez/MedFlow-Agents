"""
FastAPI Medical Consultation API
---------------------------------
Exposes the LangGraph workflow via HTTP endpoints.

Endpoints:
  POST /sessions/start              → create a new session (thread_id)
  POST /consultation/start          → start consultation with patient info
  POST /consultation/resume         → resume after an interrupt (patient answer or physician input)
  GET  /consultation/{thread_id}    → get current state snapshot
  GET  /consultation/{thread_id}/report → get final report

Flow:
  1. POST /consultation/start  →  returns first patient question
  2. POST /consultation/resume (×5, patient answers)
  3. POST /consultation/resume →  returns physician interrupt data
  4. POST /consultation/resume (physician treatment)
  5. GET  /consultation/{id}/report
"""
import uuid
import os
import traceback
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langgraph.types import Command

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

from app.graph import graph


app = FastAPI(
    title="Medical Consultation API",
    description="Multi-agent clinical orientation system — academic project",
    version="1.0.0",
)


@app.exception_handler(Exception)
async def debug_exception_handler(request, exc):
    tb = traceback.format_exc()
    print(f"UNHANDLED: {type(exc).__name__}: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"error": type(exc).__name__, "detail": str(exc)}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ──────────────────────────────────────────────────────────

class StartConsultationRequest(BaseModel):
    patient_name: str
    patient_complaint: str
    thread_id: Optional[str] = None


class ResumeRequest(BaseModel):
    thread_id: str
    user_input: str


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _extract_interrupt(thread_id: str) -> Optional[dict]:
    config = _get_config(thread_id)
    snapshot = graph.get_state(config)
    for task in snapshot.tasks:
        if task.interrupts:
            return task.interrupts[0].value
    return None


def _build_response(thread_id: str) -> dict:
    interrupt_value = _extract_interrupt(thread_id)

    if interrupt_value is None:
        config = _get_config(thread_id)
        snapshot = graph.get_state(config)
        state_values = snapshot.values
        return {
            "thread_id": thread_id,
            "status": "completed",
            "final_report": state_values.get("final_report"),
            "diagnostic_summary": state_values.get("diagnostic_summary"),
            "interim_care": state_values.get("interim_care"),
        }

    interrupt_type = interrupt_value.get("type")

    if interrupt_type == "patient_question":
        return {
            "thread_id": thread_id,
            "status": "awaiting_patient",
            "question": interrupt_value.get("question"),
            "question_number": interrupt_value.get("question_number"),
            "total_questions": interrupt_value.get("total_questions", 5),
        }

    if interrupt_type == "physician_review":
        return {
            "thread_id": thread_id,
            "status": "awaiting_physician",
            "patient_name": interrupt_value.get("patient_name"),
            "patient_complaint": interrupt_value.get("patient_complaint"),
            "diagnostic_summary": interrupt_value.get("diagnostic_summary"),
            "interim_care": interrupt_value.get("interim_care"),
            "prompt": interrupt_value.get("prompt"),
        }

    return {
        "thread_id": thread_id,
        "status": "interrupted",
        "data": interrupt_value,
    }


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/sessions/start")
def create_session():
    thread_id = str(uuid.uuid4())
    return {"thread_id": thread_id}


@app.post("/consultation/start")
def start_consultation(body: StartConsultationRequest):
    """
    Start a new consultation.
    Runs the graph until the first patient question interrupt.
    """
    thread_id = body.thread_id or str(uuid.uuid4())
    config = _get_config(thread_id)

    print(f"DEBUG: start_consultation called — name={body.patient_name}, complaint={body.patient_complaint}")

    initial_state = {
        "patient_name": body.patient_name,
        "patient_complaint": body.patient_complaint,
    }

    try:
        print(f"DEBUG: Invoking graph...")
        graph.invoke(initial_state, config)
    except Exception as e:
        print(f"DEBUG: graph.invoke exception (may be expected interrupt): {type(e).__name__}: {e}")
        traceback.print_exc()

    return _build_response(thread_id)


@app.post("/consultation/resume")
def resume_consultation(body: ResumeRequest):
    """
    Resume a paused consultation with the user's input.
    Works for both patient answers (×5) and physician treatment (×1).
    """
    config = _get_config(body.thread_id)

    try:
        snapshot = graph.get_state(config)
    except Exception:
        raise HTTPException(status_code=404, detail="Thread not found.")

    if not snapshot.tasks:
        raise HTTPException(
            status_code=400,
            detail="Consultation is already complete or not started.",
        )

    try:
        graph.invoke(Command(resume=body.user_input), config)
    except Exception as e:
        print(f"DEBUG: resume graph.invoke exception (may be expected): {type(e).__name__}: {e}")

    return _build_response(body.thread_id)


@app.get("/consultation/{thread_id}")
def get_consultation_state(thread_id: str):
    config = _get_config(thread_id)
    try:
        snapshot = graph.get_state(config)
    except Exception:
        raise HTTPException(status_code=404, detail="Thread not found.")

    state = snapshot.values
    interrupt_value = _extract_interrupt(thread_id)

    return {
        "thread_id": thread_id,
        "patient_name": state.get("patient_name"),
        "patient_complaint": state.get("patient_complaint"),
        "question_count": state.get("question_count", 0),
        "qa_pairs": state.get("qa_pairs", []),
        "diagnostic_summary": state.get("diagnostic_summary"),
        "interim_care": state.get("interim_care"),
        "physician_treatment": state.get("physician_treatment"),
        "final_report": state.get("final_report"),
        "current_interrupt": interrupt_value,
        "next_node": list(snapshot.next) if snapshot.next else [],
    }


@app.get("/consultation/{thread_id}/report")
def get_final_report(thread_id: str):
    config = _get_config(thread_id)
    try:
        snapshot = graph.get_state(config)
    except Exception:
        raise HTTPException(status_code=404, detail="Thread not found.")

    report = snapshot.values.get("final_report")
    if not report:
        raise HTTPException(
            status_code=202,
            detail="Report not yet generated. Complete the consultation first.",
        )

    return {
        "thread_id": thread_id,
        "final_report": report,
        "patient_name": snapshot.values.get("patient_name"),
        "patient_complaint": snapshot.values.get("patient_complaint"),
    }


def markdown_to_pdf_buffer(report_text: str, patient_name: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm
    )
    
    class ReportCanvas(canvas.Canvas):
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
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor('#0B1F33'))
            self.drawString(2.0 * cm, 28 * cm, "Rapport de Consultation Clinique")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor('#6B7280'))
            self.drawRightString(21 * cm - 2.0 * cm, 28 * cm, f"Patient : {patient_name}")
            self.setStrokeColor(colors.HexColor('#E5E7EB'))
            self.setLineWidth(0.5)
            self.line(2.0 * cm, 27.7 * cm, 21 * cm - 2.0 * cm, 27.7 * cm)
            
            # Footer
            self.setFont("Helvetica", 9)
            self.setFillColor(colors.HexColor('#374151'))
            page_num_str = f"Page {self._pageNumber} sur {page_count}"
            self.drawCentredString(21 * cm / 2.0, 1.2 * cm, page_num_str)
            self.restoreState()

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor('#0B1F33')
    accent_blue = colors.HexColor('#155E75')
    dark_gray = colors.HexColor('#374151')
    light_gray = colors.HexColor('#F3F4F6')
    border_color = colors.HexColor('#E5E7EB')
    
    style_title = ParagraphStyle(
        'RepTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=primary_color, alignment=TA_CENTER, spaceAfter=15
    )
    style_heading2 = ParagraphStyle(
        'RepH2', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=12, leading=15,
        textColor=accent_blue, spaceBefore=12, spaceAfter=6, keepWithNext=True
    )
    style_body = ParagraphStyle(
        'RepBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14,
        textColor=dark_gray, alignment=TA_JUSTIFY, spaceAfter=6
    )
    style_bullet = ParagraphStyle(
        'RepBullet', parent=style_body,
        leftIndent=15, firstLineIndent=-10, spaceAfter=3
    )

    story = [Spacer(1, 0.5 * cm)]
    
    lines = report_text.split('\n')
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        if line_str.startswith('# '):
            title_text = line_str[2:].replace('**', '').replace('__', '')
            story.append(Paragraph(title_text, style_title))
            story.append(Spacer(1, 0.2 * cm))
        elif line_str.startswith('## '):
            section_text = line_str[3:].replace('**', '').replace('__', '')
            story.append(Paragraph(section_text, style_heading2))
        elif line_str.startswith('- ') or line_str.startswith('* '):
            bullet_text = line_str[2:]
            formatted_text = ""
            parts = bullet_text.split('**')
            for idx, part in enumerate(parts):
                if idx % 2 == 1:
                    formatted_text += f"<b>{part}</b>"
                else:
                    formatted_text += part
            story.append(Paragraph(f"<bullet>&bull;</bullet>{formatted_text}", style_bullet))
        else:
            formatted_text = ""
            parts = line_str.split('**')
            for idx, part in enumerate(parts):
                if idx % 2 == 1:
                    formatted_text += f"<b>{part}</b>"
                else:
                    formatted_text += part
            story.append(Paragraph(formatted_text, style_body))
            
    doc.build(story, canvasmaker=ReportCanvas)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


@app.get("/consultation/{thread_id}/report/pdf")
def get_final_report_pdf(thread_id: str):
    config = _get_config(thread_id)
    try:
        snapshot = graph.get_state(config)
    except Exception:
        raise HTTPException(status_code=404, detail="Thread not found.")

    report = snapshot.values.get("final_report")
    patient_name = snapshot.values.get("patient_name", "Patient")
    if not report:
        raise HTTPException(
            status_code=202,
            detail="Report not yet generated. Complete the consultation first.",
        )

    try:
        pdf_bytes = markdown_to_pdf_buffer(report, patient_name)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=rapport_{patient_name}.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")


@app.get("/health")
def health():
    return {"status": "ok", "service": "medical-consultation-api"}

