// src/App.jsx
import { NavLink, Outlet, Link } from 'react-router-dom'
import AuthProvider, { useAuth } from './auth/AuthContext'

function Navbar() {
  const { user, logout } = useAuth()
  const link = ({ isActive }) =>
    `px-3 py-1.5 rounded-xl border transition shadow-sm ${
      isActive ? 'bg-sky-600 text-white border-sky-600'
               : 'bg-white hover:bg-sky-50 border-sky-200'
    }`

  return (
    <header className="px-6 py-4 border-b bg-white/80 backdrop-blur shadow-sm sticky top-0 z-30">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <h1 className="text-xl font-bold">
          <Link to="/" className="flex items-center gap-1 hover:opacity-90 transition">
            <span className="text-sky-600">Diagnóstica</span><span className="text-sky-900">Doc</span>
          </Link>
        </h1>

        <nav className="flex gap-2 flex-wrap">
          <NavLink to="/" className={link}>Inicio</NavLink>

          {/* 🔒 Menú protegido: solo visible con sesión */}
          {user && (
            <>
              <NavLink to="/analisis" className={link}>Análisis RX</NavLink>
              <NavLink to="/pacientes" className={link}>Pacientes</NavLink>
              {(user.role === 'admin' || user.role === 'medico') &&
                <NavLink to="/medicos" className={link}>Médicos</NavLink>}
              <NavLink to="/estudios" className={link}>Estudios</NavLink>
              <NavLink to="/imagenes" className={link}>Imágenes</NavLink>
              <NavLink to="/informes" className={link}>Informes</NavLink>
            </>
          )}

          {/* Públicos */}
          <NavLink to="/config" className={link}>Config</NavLink>
          <NavLink to="/sobre" className={link}>Quiénes somos</NavLink>

          {/* 🔐 Acciones de sesión (derecha) */}
          <div className="ml-2">
            {!user ? (
              <>
                <NavLink to="/login" className={link}>Entrar</NavLink>
                <NavLink to="/register" className={link}>Crear cuenta</NavLink>
              </>
            ) : (
              <button onClick={logout} className="px-3 py-1.5 rounded-xl border bg-white hover:bg-sky-50 border-sky-200">
                Salir ({user.email})
              </button>
            )}
          </div>
        </nav>
      </div>
    </header>
  )
}

export default function App(){
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gradient-to-b from-sky-50 to-white text-sky-900">
        <Navbar />
        <main className="container-desktop p-6">
          <Outlet />
        </main>
      </div>
    </AuthProvider>
  )
}
