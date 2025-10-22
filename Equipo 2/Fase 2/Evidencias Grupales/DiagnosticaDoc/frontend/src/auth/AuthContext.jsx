// src/auth/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../api/client' // usa tu cliente axios

const AuthCtx = createContext(null)
export const useAuth = () => useContext(AuthCtx)

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null) // {id,email,full_name,role}
  const [loading, setLoading] = useState(true)

  // Cargar sesión si hay token guardado
  useEffect(() => {
    const t = localStorage.getItem('token')
    if (!t) { setLoading(false); return }
    api.get('/auth/me')
      .then(({ data }) => setUser(data))
      .catch(() => { localStorage.removeItem('token') })
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('token', data.access_token)
    const me = await api.get('/auth/me')
    setUser(me.data)
  }

  const register = async ({ email, full_name, password, role }) => {
    await api.post('/auth/register', { email, full_name, password, role })
    // auto-login
    await login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthCtx.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthCtx.Provider>
  )
}
