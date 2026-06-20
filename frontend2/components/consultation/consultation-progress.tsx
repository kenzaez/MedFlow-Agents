"use client"

import { Check, Loader2 } from "lucide-react"

interface ConsultationProgressProps {
  currentStep: number
  isProcessing: boolean
}

const steps = [
  { id: 0, label: "Triage" },
  { id: 1, label: "Questions" },
  { id: 2, label: "Revue" },
  { id: 3, label: "Rapport" },
]

export function ConsultationProgress({ currentStep, isProcessing }: ConsultationProgressProps) {
  return (
    <div className="hidden md:flex items-center gap-2">
      {steps.map((step, index) => {
        const isComplete = currentStep > step.id
        const isCurrent = currentStep === step.id && isProcessing
        const isPending = currentStep < step.id || (!isProcessing && currentStep === step.id && currentStep !== 4)

        return (
          <div key={step.id} className="flex items-center">
            <div className="flex items-center gap-2">
              <div
                className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium transition-all
                  ${isComplete ? "bg-primary text-primary-foreground" : ""}
                  ${isCurrent ? "bg-primary/20 text-primary border-2 border-primary" : ""}
                  ${isPending ? "bg-secondary text-muted-foreground" : ""}
                  ${currentStep === 4 ? "bg-primary text-primary-foreground" : ""}
                `}
              >
                {isComplete || currentStep === 4 ? (
                  <Check className="w-4 h-4" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  step.id + 1
                )}
              </div>
              <span
                className={`
                  text-xs font-medium hidden lg:block
                  ${isComplete || currentStep === 4 ? "text-foreground" : ""}
                  ${isCurrent ? "text-primary" : ""}
                  ${isPending ? "text-muted-foreground" : ""}
                `}
              >
                {step.label}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`
                  w-8 h-0.5 mx-2 transition-colors
                  ${currentStep > step.id || currentStep === 4 ? "bg-primary" : "bg-border"}
                `}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
