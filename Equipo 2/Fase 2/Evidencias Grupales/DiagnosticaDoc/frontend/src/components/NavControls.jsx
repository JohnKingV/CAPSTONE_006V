// src/components/NavControls.jsx
import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function NavControls(){
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const canGoBack = typeof window !== 'undefined' && window.history.length > 1

  const btn =
    'px-3 py-1.5 rounded-xl border border-sky-200 text-sky-900/80 hover:bg-sky-50 disabled:opacity-50 disabled:cursor-not-allowed transition'

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => navigate(-1)}
        disabled={!canGoBack}
        className={btn}
        title="Volver a la página anterior"
      >
        ← Atrás
      </button>

      <button
        onClick={() => navigate(1)}
        className={btn}
        title="Avanzar (si hay historial)"
      >
        Adelante →
      </button>

      <span className="mx-2 opacity-40 select-none">|</span>

      {!user ? (
        <>
          <button onClick={() => navigate('/login')} className={btn}>Entrar</button>
          <button onClick={() => navigate('/register')} className={btn}>Crear cuenta</button>
        </>
      ) : (
        <>
          <span className="text-sm text-sky-900/70">
            Sesión: <strong>{user.email}</strong> ({user.role})
          </span>
          <button onClick={logout} className={btn} title="Cerrar sesión">Salir</button>
        </>
      )}
    </div>
  )
}
