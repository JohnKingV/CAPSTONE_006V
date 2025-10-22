// src/components/NavControls.jsx
import { Link, NavLink } from "react-router-dom"
import { useAuth } from "../auth/AuthContext"

const chipBase =
  // 👉 usa FLEX (no inline-flex), centra y fija altura
  "flex items-center justify-center h-10 px-4 rounded-full " +
  "border text-sm font-medium leading-none select-none " + // leading-none = cero salto vertical
  "whitespace-nowrap transition";

const chipOff = "bg-white text-slate-700 border-slate-300 hover:bg-slate-50";
const chipOn  = "bg-sky-600 text-white border-sky-600 hover:bg-sky-700";

function NavItem({ to, children }) {
  return (
    <li>
      <NavLink
        to={to}
        className={({ isActive }) => `${chipBase} ${isActive ? chipOn : chipOff}`}
      >
        {children}
      </NavLink>
    </li>
  );
}

function NavButton({ onClick, children }) {
  return (
    <li>
      <button type="button" onClick={onClick} className={`${chipBase} ${chipOff}`}>
        {children}
      </button>
    </li>
  );
}

export default function NavControls() {
  const { user, logout } = useAuth?.() ?? { user: null, logout: () => {} };

  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur border-b">
      {/* h-14 + items-center = todo centrado en el header */}
      <div className="max-w-6xl mx-auto h-14 px-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-semibold tracking-tight">
          <span className="text-sky-700">Diagnóstica</span> Doc
        </Link>

        {/* 👉 lista única con flex + items-center para igualar baseline */}
        <ul className="flex items-center gap-2">
          <NavItem to="/">Inicio</NavItem>
          <NavItem to="/config">Config</NavItem>
          <NavItem to="/about">Quiénes somos</NavItem>

          {!user ? (
            <>
              <NavItem to="/login">Entrar</NavItem>
              <NavItem to="/register">Crear cuenta</NavItem>
            </>
          ) : (
            <>
              <NavItem to="/analisis">Mi cuenta</NavItem>
              <NavButton onClick={logout}>Salir</NavButton>
            </>
          )}
        </ul>
      </div>
    </header>
  );
}
