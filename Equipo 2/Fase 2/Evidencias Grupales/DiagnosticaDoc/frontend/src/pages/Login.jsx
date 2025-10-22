// src/pages/Login.jsx
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { parseApiError } from '../api/client'

export default function Login() {
  const { login } = useAuth()
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState('')

  const onSubmit = async (e) => {
    e.preventDefault()
    setErr('')
    try {
      await login(email, password)
      nav('/analisis') // o donde quieras aterrizar después
    } catch (e) {
      setErr(parseApiError(e))
    }
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-2xl border shadow-sm">
      <h1 className="text-2xl font-bold mb-4">Iniciar sesión</h1>
      {err && <div className="p-2 bg-red-50 text-red-700 rounded mb-3">{err}</div>}
      <form onSubmit={onSubmit} className="space-y-3">
        <input
          className="w-full border p-2 rounded"
          placeholder="Email"
          value={email}
          onChange={e=>setEmail(e.target.value)}
        />
        <input
          className="w-full border p-2 rounded"
          placeholder="Contraseña"
          type="password"
          value={password}
          onChange={e=>setPassword(e.target.value)}
        />
        <button className="w-full p-2 rounded bg-sky-600 text-white hover:bg-sky-700 transition">
          Entrar
        </button>
      </form>
      <p className="mt-3 text-sm">
        ¿No tienes cuenta? <Link className="underline" to="/register">Crear cuenta</Link>
      </p>
    </div>
  )
}
