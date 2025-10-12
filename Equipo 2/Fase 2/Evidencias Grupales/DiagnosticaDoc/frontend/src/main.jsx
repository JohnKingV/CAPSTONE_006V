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

const router = createBrowserRouter([{ path: '/', element: <App/>, children: [
  { path: '/', element: <PatientsPage/> },
  { path: '/pacientes', element: <PatientsPage/> },
  { path: '/medicos', element: <DoctorsPage/> },
  { path: '/estudios', element: <StudiesPage/> },
  { path: '/informes', element: <ReportsPage/> },
  { path: '/imagenes', element: <ImagesPage/> },

]}])

createRoot(document.getElementById('root')).render(<React.StrictMode><RouterProvider router={router} /></React.StrictMode>)