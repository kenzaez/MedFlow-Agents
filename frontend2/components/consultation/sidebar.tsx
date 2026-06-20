"use client"

import { Plus, Clock, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { ConsultationHistory } from "@/app/page"

interface SidebarProps {
  history: ConsultationHistory[]
  onLoadHistory: (entry: ConsultationHistory) => void
  onNewConsultation: () => void
}

export function Sidebar({ history, onLoadHistory, onNewConsultation }: SidebarProps) {
  return (
    <aside className="hidden lg:flex flex-col w-72 border-r border-border bg-card min-h-screen">
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-lg">M</span>
          </div>
          <div>
            <h2 className="font-semibold text-foreground">MedConsult</h2>
            <p className="text-xs text-muted-foreground">IA Multi-Agents</p>
          </div>
        </div>
      </div>

      <div className="p-4">
        <Button
          onClick={onNewConsultation}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle consultation
        </Button>
      </div>

      <div className="px-4 py-2">
        <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Historique
        </h3>
      </div>

      <ScrollArea className="flex-1 px-2">
        {history.length === 0 ? (
          <div className="px-4 py-8 text-center">
            <Clock className="w-8 h-8 mx-auto text-muted-foreground/50 mb-2" />
            <p className="text-sm text-muted-foreground">
              Aucune consultation
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            {history.map((entry) => (
              <button
                key={entry.id}
                onClick={() => onLoadHistory(entry)}
                className="w-full p-3 rounded-xl text-left hover:bg-secondary transition-colors group"
              >
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center group-hover:bg-primary/20">
                    <User className="w-4 h-4 text-muted-foreground group-hover:text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm text-foreground truncate">
                      {entry.patient.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {entry.date}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </ScrollArea>

      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-accent/50">
          <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          <span className="text-xs text-muted-foreground">Systeme actif</span>
        </div>
      </div>
    </aside>
  )
}
