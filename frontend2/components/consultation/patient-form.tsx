"use client"

import { useState } from "react"
import { User, Calendar, Users, FileText, ArrowRight } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { PatientData } from "@/app/page"

interface PatientFormProps {
  onSubmit: (data: PatientData) => void
}

export function PatientForm({ onSubmit }: PatientFormProps) {
  const [formData, setFormData] = useState<PatientData>({
    name: "",
    age: "",
    sex: "",
    symptoms: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.name && formData.age && formData.sex && formData.symptoms) {
      onSubmit(formData)
    }
  }

  const isValid = formData.name && formData.age && formData.sex && formData.symptoms

  return (
    <Card className="border-border shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-3 text-xl">
          <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
            <User className="w-5 h-5 text-primary" />
          </div>
          Informations du Patient
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="name" className="flex items-center gap-2 text-sm font-medium">
                <User className="w-4 h-4 text-muted-foreground" />
                Nom complet
              </Label>
              <Input
                id="name"
                placeholder="Jean Dupont"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-input border-border focus:ring-primary"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="age" className="flex items-center gap-2 text-sm font-medium">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                Age
              </Label>
              <Input
                id="age"
                type="number"
                placeholder="45"
                min="0"
                max="150"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                className="bg-input border-border focus:ring-primary"
              />
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="sex" className="flex items-center gap-2 text-sm font-medium">
                <Users className="w-4 h-4 text-muted-foreground" />
                Sexe
              </Label>
              <Select
                value={formData.sex}
                onValueChange={(value) => setFormData({ ...formData, sex: value })}
              >
                <SelectTrigger className="bg-input border-border">
                  <SelectValue placeholder="Selectionnez" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="homme">Homme</SelectItem>
                  <SelectItem value="femme">Femme</SelectItem>
                  <SelectItem value="autre">Autre</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="symptoms" className="flex items-center gap-2 text-sm font-medium">
                <FileText className="w-4 h-4 text-muted-foreground" />
                Description des symptomes
              </Label>
              <Textarea
                id="symptoms"
                placeholder="Decrivez vos symptomes en detail..."
                rows={5}
                value={formData.symptoms}
                onChange={(e) => setFormData({ ...formData, symptoms: e.target.value })}
                className="bg-input border-border focus:ring-primary resize-none"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <Button
              type="submit"
              disabled={!isValid}
              className="bg-primary hover:bg-primary/90 text-primary-foreground px-8"
            >
              Demarrer la consultation
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
