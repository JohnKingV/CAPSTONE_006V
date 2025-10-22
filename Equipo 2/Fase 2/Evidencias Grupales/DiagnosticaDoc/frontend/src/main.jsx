import React from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App.jsx'
import './index.css'
import PatientsPage from './pages/PatientsPage.jsx'
import DoctorsPage from './pages/DoctorsPage.jsx'
import StudiesPage from './pages/StudiesPage.jsx'
import ImagesPage from './pages/ImagesPage.jsx'
import ReportsPage from './pages/ReportsPage.jsx'
import WelcomePage from './pages/WelcomePage.jsx'
import LandingPage from './pages/LandingPage.jsx'
import AnalisisRxPage from './pages/AnalisisRxPage.jsx'
import ConfigPage from './pages/ConfigPage.jsx'
import InicioPage from './pages/InicioPage.jsx'
import AboutPage from './pages/AboutPage.jsx'

const router = createBrowserRouter([{ path: '/', element: <App/>, children: [
  { path: '/', element: <LandingPage/> },
  { path: '/pacientes', element: <PatientsPage/> },
  { path: '/inicio', element: <InicioPage/> },
  { path: '/sobre', element: <AboutPage/> },
  { path: '/medicos', element: <DoctorsPage/> },
  { path: '/estudios', element: <StudiesPage/> },
  { path: '/informes', element: <ReportsPage/> },
  { path: '/imagenes', element: <ImagesPage/> },
  { path: '/analisis', element: <AnalisisRxPage/> },
  { path: '/config', element: <ConfigPage/> },

]}])

createRoot(document.getElementById('root')).render(<React.StrictMode><RouterProvider router={router} /></React.StrictMode>)