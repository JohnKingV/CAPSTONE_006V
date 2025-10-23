// src/pages/Register.jsx
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { parseApiError } from '../api/client'

export default function Register() {
  const { register } = useAuth()
  const nav = useNavigate()

  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'paciente', // admin | medico | paciente
  })
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setErr('')

    // Validaciones rápidas
    const email = form.email.trim()
    const full_name = form.full_name.trim()
    const password = (form.password || '').slice(0, 72) // bcrypt <= 72 bytes

    if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
      return setErr('Ingresa un email válido.')
    }
    if (password.length < 6) {
      return setErr('La contraseña debe tener al menos 6 caracteres.')
    }
    if (!full_name) {
      return setErr('Ingresa tu nombre completo.')
    }

    setLoading(true)
    try {
      await register({ ...form, email, full_name, password })
      nav('/analisis')
    } catch (e) {
      setErr(parseApiError(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-2xl border shadow-sm">
      <h1 className="text-2xl font-bold mb-4">Crear cuenta</h1>

      {err && (
        <div className="p-2 bg-red-50 text-red-700 rounded mb-3">
          {err}
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-3">
        <input
          className="w-full border p-2 rounded"
          placeholder="Nombre completo"
          value={form.full_name}
          onChange={(e) => setForm({ ...form, full_name: e.target.value })}
          autoComplete="name"
          required
        />

        <input
          className="w-full border p-2 rounded"
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          autoComplete="email"
          required
        />

        <input
          className="w-full border p-2 rounded"
          placeholder="Contraseña (6–72)"
          type="password"
          value={form.password}
          onChange={(e) =>
            setForm({ ...form, password: e.target.value.slice(0, 72) })
          }
          autoComplete="new-password"
          minLength={6}
          maxLength={72}
          required
        />

        <select
          className="w-full border p-2 rounded"
          value={form.role}
          onChange={(e) => setForm({ ...form, role: e.target.value })}
        >
          <option value="paciente">Paciente</option>
          <option value="medico">Médico</option>
          <option value="admin">Admin</option>
        </select>

        <button
          className="w-full p-2 rounded bg-sky-600 text-white hover:bg-sky-700 transition disabled:opacity-60"
          disabled={loading}
        >
          {loading ? 'Creando cuenta…' : 'Registrarme'}
        </button>
      </form>

      <p className="mt-3 text-sm">
        ¿Ya tienes cuenta?{' '}
        <Link className="underline" to="/login">
          Entrar
        </Link>
      </p>
    </div>
  )
}
