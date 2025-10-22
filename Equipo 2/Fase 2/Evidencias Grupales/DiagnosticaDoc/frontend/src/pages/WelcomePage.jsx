// frontend/src/pages/WelcomePage.jsx
import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function WelcomePage(){
  const navigate = useNavigate()
  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <div className="max-w-3xl text-center space-y-6">
        <h1 className="text-4xl font-bold text-sky-900">DiagnósticaDoc</h1>
        <p className="text-slate-600">
          Plataforma para gestión clínica y análisis asistido por IA.
        </p>
        <button
          onClick={()=> navigate('/inicio')}
          className="px-6 py-3 rounded-2xl bg-sky-600 text-white hover:bg-sky-700 transition"
        >
          Entrar
        </button>
        <div className="text-xs text-slate-400">vista de bienvenida</div>
      </div>
    </div>
  )
}
