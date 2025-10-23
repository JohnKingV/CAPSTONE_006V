// frontend/src/pages/AboutPage.jsx
import React from 'react'

export default function AboutPage(){
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h2 className="text-3xl font-semibold">Quiénes somos</h2>
      <p className="text-slate-600">
        DiagnósticaDoc nace como proyecto universitario orientado a crear una plataforma clínica
        con soporte de inteligencia artificial para análisis de imágenes médicas.
      </p>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="rounded-2xl border bg-white p-5">
          <h4 className="font-semibold mb-2">Valores</h4>
          <ul className="list-disc list-inside text-slate-600 space-y-1">
            <li>Rigor técnico y buenas prácticas.</li>
            <li>Privacidad y seguridad de los datos.</li>
            <li>Usabilidad y accesibilidad.</li>
          </ul>
        </div>
        <div className="rounded-2xl border bg-white p-5">
          <h4 className="font-semibold mb-2">Tecnologías</h4>
          <ul className="list-disc list-inside text-slate-600 space-y-1">
            <li>Backend: FastAPI + PostgreSQL.</li>
            <li>Frontend: React + Vite + Tailwind.</li>
            <li>IA: Keras / TensorFlow (demo de RX).</li>
          </ul>
        </div>
      </div>
      <p className="text-slate-600">
        Este sitio incluye una demo de clasificación de rayos X de tórax con fines académicos.
        No sustituye el juicio clínico profesional.
      </p>
    </div>
  )
}
