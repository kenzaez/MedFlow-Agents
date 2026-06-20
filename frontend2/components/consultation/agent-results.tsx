"use client"

import { User, Check, Loader2, AlertCircle, Stethoscope, MessageSquare, ClipboardCheck, FileText } from "lucide-react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { PatientData, AgentResult } from "@/app/page"

interface AgentResultsProps {
  patient: PatientData
  results: AgentResult[]
  currentStep: number
  isProcessing: boolean
}

const agentIcons = [
  AlertCircle,
  MessageSquare,
  Stethoscope,
  FileText,
]

const agentColors = [
  "bg-chart-1/20 text-chart-1",
  "bg-chart-2/20 text-chart-2",
  "bg-chart-3/20 text-chart-3",
  "bg-chart-4/20 text-chart-4",
]

export function AgentResults({ patient, results, currentStep, isProcessing }: AgentResultsProps) {
  return (
    <div className="space-y-6">
      {/* Patient Summary Card */}
      <Card className="border-border shadow-sm">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-secondary flex items-center justify-center">
                <User className="w-7 h-7 text-muted-foreground" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-foreground">{patient.name}</h2>
                <p className="text-muted-foreground">
                  {patient.sex === "homme" ? "Homme" : patient.sex === "femme" ? "Femme" : "Autre"}, {patient.age} ans
                </p>
              </div>
            </div>
            <Badge variant="secondary" className="px-4 py-1.5 text-sm">
              {isProcessing ? "En cours..." : "Termine"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="p-4 rounded-xl bg-secondary/50">
            <h3 className="text-sm font-medium text-foreground mb-2">Symptomes</h3>
            <p className="text-muted-foreground text-sm leading-relaxed">{patient.symptoms}</p>
          </div>
        </CardContent>
      </Card>

      {/* Agent Results Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {results.map((result, index) => {
          const Icon = agentIcons[index]
          const colorClass = agentColors[index]

          return (
            <Card
              key={result.agent}
              className={`
                border-border shadow-sm transition-all duration-300
                ${result.status === "processing" ? "ring-2 ring-primary/50" : ""}
              `}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${colorClass}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-semibold text-foreground">{result.agent}</h3>
                  </div>
                  <StatusIndicator status={result.status} />
                </div>
              </CardHeader>
              <CardContent>
                {result.status === "pending" && (
                  <div className="h-24 flex items-center justify-center">
                    <p className="text-muted-foreground text-sm">En attente...</p>
                  </div>
                )}
                {result.status === "processing" && (
                  <div className="h-24 flex items-center justify-center">
                    <div className="flex items-center gap-3">
                      <Loader2 className="w-5 h-5 animate-spin text-primary" />
                      <p className="text-muted-foreground text-sm">Analyse en cours...</p>
                    </div>
                  </div>
                )}
                {result.status === "complete" && (
                  <div className="prose prose-sm max-w-none">
                    <div className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
                      {formatContent(result.content)}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

function StatusIndicator({ status }: { status: AgentResult["status"] }) {
  if (status === "pending") {
    return (
      <div className="w-6 h-6 rounded-full bg-secondary flex items-center justify-center">
        <div className="w-2 h-2 rounded-full bg-muted-foreground/50" />
      </div>
    )
  }
  if (status === "processing") {
    return (
      <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center">
        <Loader2 className="w-3 h-3 animate-spin text-primary" />
      </div>
    )
  }
  return (
    <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
      <Check className="w-3 h-3 text-primary-foreground" />
    </div>
  )
}

function formatContent(content: string) {
  const lines = content.split("\n")
  return lines.map((line, i) => {
    if (line.startsWith("**") && line.endsWith("**")) {
      return (
        <p key={i} className="font-semibold text-foreground mt-3 first:mt-0">
          {line.replace(/\*\*/g, "")}
        </p>
      )
    }
    if (line.startsWith("- ")) {
      return (
        <p key={i} className="pl-4 text-muted-foreground">
          {line}
        </p>
      )
    }
    if (line.match(/^\d+\./)) {
      return (
        <p key={i} className="pl-4 text-muted-foreground">
          {line}
        </p>
      )
    }
    if (line.trim() === "") {
      return <br key={i} />
    }
    return (
      <p key={i} className="text-muted-foreground">
        {line}
      </p>
    )
  })
}
