import { NavLink, Outlet } from 'react-router-dom'

export default function App(){
  const link = ({ isActive }) => `px-3 py-1.5 rounded-xl ${isActive? 'bg-sky-600 text-white' : 'hover:bg-sky-100'}`
  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 to-white text-sky-900">
      <header className="px-6 py-4 border-b bg-white/80 backdrop-blur">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold">DiagnosticaDoc</h1>
          <nav className="flex gap-2 flex-wrap">
            <NavLink to="/pacientes" className={link}>Pacientes</NavLink>
            <NavLink to="/medicos" className={link}>Médicos</NavLink>
            <NavLink to="/estudios" className={link}>Estudios</NavLink>
            <NavLink to="/imagenes" className={link}>Imágenes</NavLink>
            <NavLink to="/informes" className={link}>Informes</NavLink>
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto p-6">
        <Outlet />
      </main>
    </div>
  )
}
