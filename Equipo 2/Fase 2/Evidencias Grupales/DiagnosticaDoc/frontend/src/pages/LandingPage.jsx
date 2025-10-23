// frontend/src/pages/LandingPage.jsx
import React from 'react'
import { Link, useNavigate } from 'react-router-dom'

function Section({ title, children }){
  return (
    <section className="py-12">
      <h3 className="text-xl font-semibold mb-3">{title}</h3>
      <div className="text-slate-600">{children}</div>
    </section>
  )
}

export default function LandingPage(){
  const navigate = useNavigate()
  return (
    <div className="min-h-[70vh]">
      {/* Hero */}
      <div className="rounded-3xl bg-gradient-to-br from-sky-50 to-white border p-8 md:p-12 mb-8">
        <h1 className="text-4xl md:text-5xl font-extrabold text-sky-900">DiagnósticaDoc</h1>
        <p className="mt-3 text-slate-600 max-w-2xl">
          Plataforma clínica con análisis de imágenes por IA. Gestiona pacientes, médicos y estudios mientras
          ejecutas predicciones de rayos X de tórax de forma simple y segura.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <button
            onClick={()=> navigate('/inicio')}
            className="px-6 py-3 rounded-2xl bg-sky-600 text-white hover:bg-sky-700 transition"
          >
            Entrar a la plataforma
          </button>
          <Link to="/analisis" className="px-6 py-3 rounded-2xl border hover:bg-white transition">
            Probar análisis RX
          </Link>
        </div>
      </div>

      {/* Quiénes somos */}
      <Section title="Quiénes somos">
        Somos un equipo universitario enfocado en soluciones de salud digital.
        Combinamos desarrollo web moderno (FastAPI + React) con modelos de visión por computadora
        para apoyar la toma de decisiones clínicas.
      </Section>

      {/* Misión y visión */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="rounded-2xl border bg-white p-5">
          <h4 className="font-semibold mb-2">Misión</h4>
          <p className="text-slate-600">
            Impulsar una atención médica más rápida y precisa en Chile mediante inteligencia artificial aplicada al diagnóstico clínico, 
            facilitando el acceso a tecnología avanzada para profesionales de la salud y centros médicos.
          </p>
        </div>
        <div className="rounded-2xl border bg-white p-5">
          <h4 className="font-semibold mb-2">Visión</h4>
          <p className="text-slate-600">
            Convertirnos en una plataforma integral para imágenes médicas con trazabilidad, auditoría
            y modelos de IA especializados.
          </p>
        </div>
      </div>

      {/* Qué ofrecemos */}
      <Section title="Qué ofrecemos">
        <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <li className="rounded-xl border bg-white p-4">
            <div className="font-medium">Gestión clínica</div>
            <div className="text-sm text-slate-500">Pacientes, médicos, estudios e informes.</div>
          </li>
          <li className="rounded-xl border bg-white p-4">
            <div className="font-medium">Análisis de RX por IA</div>
            <div className="text-sm text-slate-500">Clasificación Normal / Tuberculosis (demo).</div>
          </li>
          <li className="rounded-xl border bg-white p-4">
            <div className="font-medium">Conexión flexible</div>
            <div className="text-sm text-slate-500">Configura Colab o EC2 desde <Link to="/config" className="underline">/config</Link>.</div>
          </li>
        </ul>
      </Section>

      {/* CTA */}
      <div className="mt-10 rounded-2xl border p-6 bg-white flex items-center justify-between gap-4 flex-wrap">
        <div>
          <div className="font-semibold">¿Listo para comenzar?</div>
          <div className="text-slate-600 text-sm">Ingresa y explora el tablero con todas las secciones.</div>
        </div>
        <button
          onClick={()=> window.scrollTo({ top: 0, behavior:'smooth' }) || navigate('/inicio')}
          className="px-5 py-2.5 rounded-xl bg-sky-600 text-white hover:bg-sky-700"
        >
          Ir a Inicio
        </button>
      </div>
    </div>
  )
}