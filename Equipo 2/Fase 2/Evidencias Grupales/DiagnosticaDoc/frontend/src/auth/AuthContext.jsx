// src/auth/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from 'react'
import api from '../api/client' // usa el cliente axios central (export default)

const AuthCtx = createContext(null)
export const useAuth = () => useContext(AuthCtx)

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null)     // { id, email, full_name, role, ... }
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Cargar sesión si hay token guardado
  useEffect(() => {
    (async () => {
      const token = localStorage.getItem('token')
      if (!token) { setLoading(false); return }
      // primar el header para esta sesión
      api.defaults.headers.Authorization = `Bearer ${token}`
      try {
        const { data } = await api.get('/auth/me')
        setUser(data)
      } catch {
        // token inválido/expirado
        localStorage.removeItem('token')
        delete api.defaults.headers.Authorization
        setUser(null)
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const login = async (email, password) => {
    setError(null)
    try {
      const { data } = await api.post('/auth/login', { email, password })
      const token = data?.access_token || data?.token
      if (!token) throw new Error('El servidor no devolvió un token')

      localStorage.setItem('token', token)
      api.defaults.headers.Authorization = `Bearer ${token}`

      const me = await api.get('/auth/me')
      setUser(me.data)
      return true
    } catch (e) {
      localStorage.removeItem('token')
      delete api.defaults.headers.Authorization
      setUser(null)
      setError(e?.message || 'Error al iniciar sesión')
      throw e
    }
  }

  const register = async ({ email, full_name, password, role }) => {
    await api.post('/auth/register', { email, full_name, password, role })
    // auto-login
    return login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('token')
    delete api.defaults.headers.Authorization
    setUser(null)
  }

  return (
    <AuthCtx.Provider value={{ user, loading, error, login, register, logout }}>
      {children}
    </AuthCtx.Provider>
  )
}
