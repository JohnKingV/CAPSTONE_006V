// frontend/src/pages/InicioPage.jsx
import React from 'react'
import { Link } from 'react-router-dom'
const Tile = ({ to, title, desc, icon }) => (
  <Link to={to} className="group block rounded-2xl border bg-white p-5 hover:shadow-md transition">
    <div className="flex items-center gap-3">
      <div className="rounded-xl border w-10 h-10 grid place-items-center text-sky-700">{icon || '•'}</div>
      <div>
        <div className="font-semibold">{title}</div>
        <div className="text-sm text-slate-500">{desc}</div>
      </div>
    </div>
  </Link>
)
export default function InicioPage(){
  return (
    <div className="max-w-6xl mx-auto">
      <h2 className="text-2xl font-semibold mb-4">Inicio</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Tile to="/pacientes" title="Pacientes" desc="Gestión de pacientes" icon="👤" />
        <Tile to="/medicos" title="Médicos" desc="Directorio de médicos" icon="🩺" />
        <Tile to="/estudios" title="Estudios" desc="Solicitudes y estudios" icon="🧪" />
        <Tile to="/imagenes" title="Imágenes" desc="Carga y revisión de imágenes" icon="🖼️" />
        <Tile to="/informes" title="Informes" desc="Elaboración y control de informes" icon="📄" />
        <Tile to="/analisis" title="Análisis RX" desc="Clasificación asistida por IA" icon="🤖" />
        <Tile to="/config" title="Config" desc="Endpoint Colab/EC2 y pruebas" icon="⚙️" />
      </div>
    </div>
  )
}
