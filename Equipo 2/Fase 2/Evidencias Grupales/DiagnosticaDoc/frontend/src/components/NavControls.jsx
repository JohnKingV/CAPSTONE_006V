import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function NavControls(){
  const navigate = useNavigate()
  const canGoBack = typeof window !== 'undefined' && window.history.length > 1

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={()=> navigate(-1)}
        disabled={!canGoBack}
        className="px-3 py-1.5 rounded-xl border border-sky-200 text-sky-900/80 hover:bg-sky-50 disabled:opacity-50 disabled:cursor-not-allowed"
        title="Volver a la página anterior"
      >
        ← Atrás
      </button>
      <button
        onClick={()=> navigate(1)}
        className="px-3 py-1.5 rounded-xl border border-sky-200 text-sky-900/80 hover:bg-sky-50"
        title="Avanzar (si hay historial)"
      >
        Adelante →
      </button>
    </div>
  )
}
