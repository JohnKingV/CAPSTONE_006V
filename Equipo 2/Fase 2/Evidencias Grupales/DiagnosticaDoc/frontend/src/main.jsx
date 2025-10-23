// src/main.jsx
import React from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'

import App from './App.jsx'

// Páginas
import LandingPage from './pages/LandingPage.jsx'
import InicioPage from './pages/InicioPage.jsx'
import AboutPage from './pages/AboutPage.jsx'
import ConfigPage from './pages/ConfigPage.jsx'

import PatientsPage from './pages/PatientsPage.jsx'
import DoctorsPage from './pages/DoctorsPage.jsx'
import StudiesPage from './pages/StudiesPage.jsx'
import ImagesPage from './pages/ImagesPage.jsx'
import ReportsPage from './pages/ReportsPage.jsx'
import AnalisisRxPage from './pages/AnalisisRxPage.jsx'

// Auth
import AuthProvider from './auth/AuthContext.jsx'
import ProtectedRoute from './auth/ProtectedRoute.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,         // tu layout con Navbar + <Outlet/>
    children: [
      // Públicas
      { index: true, element: <LandingPage /> }, // "/" equivale a tu Landing
      { path: 'inicio', element: <InicioPage /> },
      { path: 'sobre', element: <AboutPage /> },
      { path: 'config', element: <ConfigPage /> },

      // Auth pages
      { path: 'login', element: <Login /> },
      { path: 'register', element: <Register /> },

      // Protegidas (solo logeado)
      { path: 'pacientes', element: (
          <ProtectedRoute><PatientsPage /></ProtectedRoute>
        )
      },
      { path: 'analisis', element: (
          <ProtectedRoute><AnalisisRxPage /></ProtectedRoute>
        )
      },
      { path: 'estudios', element: (
          <ProtectedRoute><StudiesPage /></ProtectedRoute>
        )
      },
      { path: 'imagenes', element: (
          <ProtectedRoute><ImagesPage /></ProtectedRoute>
        )
      },
      { path: 'informes', element: (
          <ProtectedRoute><ReportsPage /></ProtectedRoute>
        )
      },

      // Por rol (admin/medico)
      { path: 'medicos', element: (
          <ProtectedRoute roles={['admin','medico']}><DoctorsPage /></ProtectedRoute>
        )
      },
    ],
  },
])

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </React.StrictMode>
)
