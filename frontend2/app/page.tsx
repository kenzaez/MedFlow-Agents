"use client"

import { useState, useRef } from "react"
import { startConsultation, resumeConsultation, type ApiResponse } from "./lib/api"

// ── Types ─────────────────────────────────────────────────────────────────

type Step = "input" | "qna" | "physician" | "report"

// ── Markdown renderer (no external deps) ──────────────────────────────────

function renderMarkdown(text: string) {
  const lines = text.split("\n")
  const elements: React.ReactNode[] = []
  let key = 0

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    if (line.startsWith("# ")) {
      elements.push(
        <h1 key={key++} className="text-2xl font-semibold text-foreground mt-6 mb-3 pb-2 border-b border-border">
          {line.slice(2)}
        </h1>
      )
    } else if (line.startsWith("## ")) {
      elements.push(
        <h2 key={key++} className="text-lg font-semibold text-foreground mt-5 mb-2">
          {line.slice(3)}
        </h2>
      )
    } else if (line.startsWith("### ")) {
      elements.push(
        <h3 key={key++} className="text-base font-semibold text-foreground mt-4 mb-1">
          {line.slice(4)}
        </h3>
      )
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(
        <li key={key++} className="ml-4 text-sm text-foreground/80 leading-relaxed list-disc">
          {inlineFormat(line.slice(2))}
        </li>
      )
    } else if (line.trim() === "") {
      elements.push(<div key={key++} className="h-2" />)
    } else {
      elements.push(
        <p key={key++} className="text-sm text-foreground/80 leading-relaxed">
          {inlineFormat(line)}
        </p>
      )
    }
  }

  return elements
}

function inlineFormat(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return parts.map((part, i) =>
    part.startsWith("**") && part.endsWith("**")
      ? <strong key={i} className="font-semibold text-foreground">{part.slice(2, -2)}</strong>
      : part
  )
}

// ── Step indicator ────────────────────────────────────────────────────────

const STEPS: { id: Step; label: string }[] = [
  { id: "input",    label: "Patient"   },
  { id: "qna",      label: "Questions" },
  { id: "physician",label: "Medecin"   },
  { id: "report",   label: "Rapport"   },
]

function StepBar({ current }: { current: Step }) {
  const idx = STEPS.findIndex(s => s.id === current)
  return (
    <div className="flex items-center justify-center gap-0 mb-10">
      {STEPS.map((step, i) => {
        const done    = i < idx
        const active  = i === idx
        const pending = i > idx
        return (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center gap-1.5">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all ${
                  done    ? "bg-primary text-primary-foreground"  :
                  active  ? "bg-primary text-primary-foreground ring-4 ring-primary/20" :
                            "bg-muted text-muted-foreground"
                }`}
              >
                {done ? (
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M2 7l3.5 3.5L12 3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : (
                  i + 1
                )}
              </div>
              <span className={`text-xs font-medium ${active ? "text-foreground" : "text-muted-foreground"}`}>
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div className={`h-px w-16 mx-2 mb-5 transition-all ${i < idx ? "bg-primary" : "bg-border"}`} />
            )}
          </div>
        )
      })}
    </div>
  )
}

// ── Shared UI primitives ──────────────────────────────────────────────────

function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-card rounded-2xl border border-border shadow-sm p-8 ${className}`}>
      {children}
    </div>
  )
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <label className="block text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">
      {children}
    </label>
  )
}

function Input({ ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className="w-full bg-input border border-border rounded-xl px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition"
    />
  )
}

function Textarea({ ...props }: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      {...props}
      className="w-full bg-input border border-border rounded-xl px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition resize-none"
    />
  )
}

function Button({
  children,
  loading = false,
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { loading?: boolean; variant?: "primary" | "secondary" }) {
  return (
    <button
      {...props}
      disabled={loading || props.disabled}
      className={`w-full py-3.5 px-6 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${
        variant === "primary"
          ? "bg-primary text-primary-foreground hover:bg-primary/90 active:scale-[0.98]"
          : "bg-secondary text-secondary-foreground border border-border hover:bg-muted active:scale-[0.98]"
      }`}
    >
      {loading && (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
        </svg>
      )}
      {children}
    </button>
  )
}

function ErrorBox({ message }: { message: string }) {
  return (
    <div className="mt-4 bg-destructive/10 border border-destructive/20 text-destructive rounded-xl px-4 py-3 text-sm">
      {message}
    </div>
  )
}

// ── Screen 1 — Patient Input ──────────────────────────────────────────────

function PatientInputScreen({
  onComplete,
}: {
  onComplete: (res: ApiResponse) => void
}) {
  const [name, setName]           = useState("")
  const [complaint, setComplaint] = useState("")
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState<string | null>(null)

  async function handleSubmit() {
    if (!name.trim() || !complaint.trim()) {
      setError("Veuillez remplir tous les champs.")
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await startConsultation(name.trim(), complaint.trim())
      onComplete(res)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erreur serveur.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-1">
          Nouvelle consultation
        </p>
        <h1 className="text-2xl font-semibold text-foreground">
          Informations patient
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Renseignez vos informations pour commencer l'orientation clinique.
        </p>
      </div>

      <div className="space-y-5">
        <div>
          <Label>Nom du patient</Label>
          <Input
            placeholder="Ex : Mohamed Alami"
            value={name}
            onChange={e => setName(e.target.value)}
          />
        </div>
        <div>
          <Label>Description des symptomes</Label>
          <Textarea
            placeholder="Ex : Toux seche et fievre legere depuis 3 jours, fatigue generale..."
            rows={5}
            value={complaint}
            onChange={e => setComplaint(e.target.value)}
          />
        </div>
      </div>

      <div className="mt-8">
        <Button loading={loading} onClick={handleSubmit}>
          {loading ? "Initialisation..." : "Demarrer la consultation"}
        </Button>
      </div>

      {error && <ErrorBox message={error} />}
    </Card>
  )
}

// ── Screen 2 — Patient Q&A ────────────────────────────────────────────────

function QnAScreen({
  threadId,
  question,
  questionNumber,
  onComplete,
}: {
  threadId: string
  question: string
  questionNumber: number
  onComplete: (res: ApiResponse) => void
}) {
  const [answer, setAnswer]   = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<string | null>(null)

  async function handleSubmit() {
    if (!answer.trim()) {
      setError("Veuillez entrer une reponse.")
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await resumeConsultation(threadId, answer.trim())
      setAnswer("")
      onComplete(res)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erreur serveur.")
    } finally {
      setLoading(false)
    }
  }

  const progress = (questionNumber / 5) * 100

  return (
    <Card>
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
            Questions cliniques
          </p>
          <span className="text-xs font-semibold text-muted-foreground bg-muted px-2.5 py-1 rounded-full">
            {questionNumber} / 5
          </span>
        </div>
        {/* Progress bar */}
        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Question card */}
      <div className="bg-accent/30 border border-accent/50 rounded-xl px-5 py-4 mb-6">
        <p className="text-xs font-semibold uppercase tracking-widest text-accent-foreground/60 mb-1.5">
          Question {questionNumber}
        </p>
        <p className="text-sm font-medium text-foreground leading-relaxed">
          {question}
        </p>
      </div>

      <div>
        <Label>Votre reponse</Label>
        <Textarea
          placeholder="Decrivez votre reponse ici..."
          rows={4}
          value={answer}
          onChange={e => setAnswer(e.target.value)}
        />
      </div>

      <div className="mt-6">
        <Button loading={loading} onClick={handleSubmit}>
          {loading ? "Traitement..." : "Repondre"}
        </Button>
      </div>

      {error && <ErrorBox message={error} />}
    </Card>
  )
}

// ── Screen 3 — Physician Review ───────────────────────────────────────────

function PhysicianScreen({
  threadId,
  diagnosticSummary,
  interimCare,
  onComplete,
}: {
  threadId: string
  diagnosticSummary: string
  interimCare: string
  onComplete: (res: ApiResponse) => void
}) {
  const [treatment, setTreatment] = useState("")
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState<string | null>(null)

  async function handleSubmit() {
    if (!treatment.trim()) {
      setError("Veuillez entrer le traitement et la conduite a tenir.")
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await resumeConsultation(threadId, treatment.trim())
      onComplete(res)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erreur serveur.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-5">
      {/* Physician badge */}
      <div className="flex items-center gap-2 bg-muted border border-border rounded-xl px-4 py-3">
        <div className="w-2 h-2 bg-primary rounded-full" />
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">
          Interface medecin traitant — acces restreint
        </p>
      </div>

      {/* Diagnostic summary */}
      <Card>
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
          Synthese clinique preliminaire
        </p>
        <div className="text-sm text-foreground/80 leading-relaxed space-y-2">
          {diagnosticSummary ? renderMarkdown(diagnosticSummary) : "Aucune synthese disponible."}
        </div>
      </Card>

      {/* Interim care */}
      <Card>
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
          Recommandation intermediaire
        </p>
        <div className="bg-accent/20 border border-accent/40 rounded-xl px-4 py-3 space-y-2">
          {interimCare ? renderMarkdown(interimCare) : "Aucune recommandation disponible."}
        </div>
      </Card>

      {/* Treatment input */}
      <Card>
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
          Traitement et conduite a tenir
        </p>
        <Textarea
          placeholder="Ex : Paracetamol 1g x 3/jour pendant 5 jours, repos, hydratation..."
          rows={5}
          value={treatment}
          onChange={e => setTreatment(e.target.value)}
        />
        <div className="mt-5">
          <Button loading={loading} onClick={handleSubmit}>
            {loading ? "Generation du rapport..." : "Valider et generer le rapport"}
          </Button>
        </div>
        {error && <ErrorBox message={error} />}
      </Card>
    </div>
  )
}

// ── Screen 4 — Final Report ───────────────────────────────────────────────

function ReportScreen({
  report,
  threadId,
  onReset,
}: {
  report: string
  threadId: string | null
  onReset: () => void
}) {
  function downloadReport() {
    if (!threadId) return;
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    window.open(`${API_URL}/consultation/${threadId}/report/pdf`, "_blank");
  }

  return (
    <div className="space-y-5">
      {/* Success banner */}
      <div className="bg-primary/20 border border-primary/40 rounded-xl px-5 py-3 flex items-center gap-3">
        <div className="w-2 h-2 bg-primary rounded-full shrink-0" />
        <p className="text-sm font-semibold text-foreground">
          Consultation terminee — rapport genere avec succes
        </p>
      </div>

      {/* Report content */}
      <Card>
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-5">
          Rapport de consultation clinique
        </p>
        <div className="divide-y divide-border/50">
          {renderMarkdown(report)}
        </div>
      </Card>

      {/* Actions */}
      <div className="grid grid-cols-2 gap-3">
        <Button variant="primary" onClick={downloadReport}>
          Telecharger le rapport
        </Button>
        <Button variant="secondary" onClick={onReset}>
          Nouvelle consultation
        </Button>
      </div>
    </div>
  )
}

// ── Root page ─────────────────────────────────────────────────────────────

export default function HomePage() {
  const [step, setStep]                     = useState<Step>("input")
  const [threadId, setThreadId]             = useState<string | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState("")
  const [questionNumber, setQuestionNumber] = useState(1)
  const [diagnosticSummary, setDiagnosticSummary] = useState("")
  const [interimCare, setInterimCare]       = useState("")
  const [finalReport, setFinalReport]       = useState("")

  function handleApiResponse(res: ApiResponse) {
    setThreadId(res.thread_id)

    if (res.status === "awaiting_patient") {
      setCurrentQuestion(res.question ?? "")
      setQuestionNumber(res.question_number ?? 1)
      setStep("qna")
    } else if (res.status === "awaiting_physician") {
      setDiagnosticSummary(res.diagnostic_summary ?? "")
      setInterimCare(res.interim_care ?? "")
      setStep("physician")
    } else if (res.status === "completed") {
      setFinalReport(res.final_report ?? "")
      setStep("report")
    }
  }

  function handleReset() {
    setStep("input")
    setThreadId(null)
    setCurrentQuestion("")
    setQuestionNumber(1)
    setDiagnosticSummary("")
    setInterimCare("")
    setFinalReport("")
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              EMSI Casablanca
            </p>
            <h1 className="text-base font-semibold text-foreground">
              Consultation Medicale
            </h1>
          </div>
          <span className="text-xs font-medium bg-muted text-muted-foreground px-3 py-1.5 rounded-full border border-border">
            Projet academique
          </span>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-2xl mx-auto px-6 py-10">
        <StepBar current={step} />

        {step === "input" && (
          <PatientInputScreen onComplete={handleApiResponse} />
        )}

        {step === "qna" && threadId && (
          <QnAScreen
            threadId={threadId}
            question={currentQuestion}
            questionNumber={questionNumber}
            onComplete={handleApiResponse}
          />
        )}

        {step === "physician" && threadId && (
          <PhysicianScreen
            threadId={threadId}
            diagnosticSummary={diagnosticSummary}
            interimCare={interimCare}
            onComplete={handleApiResponse}
          />
        )}

        {step === "report" && (
          <ReportScreen report={finalReport} threadId={threadId} onReset={handleReset} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border mt-16">
        <div className="max-w-2xl mx-auto px-6 py-5 text-center">
          <p className="text-xs text-muted-foreground">
            Ce systeme ne remplace pas une consultation medicale. Application academique uniquement.
          </p>
        </div>
      </footer>
    </div>
  )
}
