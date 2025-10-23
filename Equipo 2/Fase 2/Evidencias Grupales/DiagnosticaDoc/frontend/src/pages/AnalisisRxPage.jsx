// src/pages/AnalisisRxPage.jsx
import { useEffect, useState } from 'react'
import { predictXRay } from '../api/analisis'        // ya lo tienes
import { getEstudios } from '../api/estudios'        // lista estudios
import { createInforme } from '../api/informes'      // crea informe
import Spinner from "../components/ui/Spinner.jsx";
import Toast from "../components/ui/Toast.jsx";

export default function AnalisisRxPage() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState(null)

  // Estudios para vincular informe
  const [estudios, setEstudios] = useState([])
  const [estudioId, setEstudioId] = useState('')

  useEffect(() => {
    // carga estudios recientes (ajusta la paginación si aplica)
    (async () => {
      try {
        const data = await getEstudios()
        setEstudios(data || [])
      } catch (e) {
        console.error(e)
      }
    })()
  }, [])

  const onAnalyze = async (e) => {
    e.preventDefault()
    if (!file) {
      setToast({ type: 'error', message: 'Selecciona una imagen' })
      return
    }
    try {
      setLoading(true)
      const data = await predictXRay(file) // POST /predict
      setResult(data)
      setToast({ type: 'success', message: 'Análisis completado' })
    } catch (err) {
      console.error(err)
      setToast({ type: 'error', message: 'Error al analizar la imagen' })
    } finally {
      setLoading(false)
    }
  }

  const onSaveReport = async () => {
    if (!result) {
      setToast({ type: 'error', message: 'Primero realiza el análisis' })
      return
    }
    if (!estudioId) {
      setToast({ type: 'error', message: 'Selecciona un Estudio' })
      return
    }
    const pct = (v) => `${(v * 100).toFixed(2)}%`
    const contenido =
      `Resultado IA (DiagnosticaDoc)\n` +
      `- Normal: ${pct(result.normal ?? 0)}\n` +
      `- Tuberculosis: ${pct(result.tuberculosis ?? 0)}\n` +
      `Detalles: ${JSON.stringify(result.predictions || [], null, 2)}\n`

    try {
      await createInforme({
        estudio_id: Number(estudioId),
        contenido,
        estado_id: 1, // "borrador"
        observaciones: 'Generado automáticamente por IA'
      })
      setToast({ type: 'success', message: 'Informe guardado' })
      // opcional: limpiar result/file
      // setResult(null); setFile(null)
    } catch (err) {
      console.error(err)
      setToast({ type: 'error', message: 'No se pudo guardar el informe' })
    }
  }

  return (
    <div className="section">
      <h2 className="title-page">Análisis de Rayos X (IA)</h2>

      <form onSubmit={onAnalyze} className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="label">Archivo RX</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="input"
            />
          </div>
          <div>
            <label className="label">Vincular al Estudio</label>
            <select
              className="input"
              value={estudioId}
              onChange={(e) => setEstudioId(e.target.value)}
            >
              <option value="">— Selecciona Estudio —</option>
              {estudios.map((es) => (
                <option key={es.id} value={es.id}>
                  #{es.id} — Paciente: {es.paciente?.nombre ?? es.paciente_id} — Médico: {es.medico?.nombre ?? es.medico_id}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button className="btn-primary" disabled={loading}>
          {loading ? 'Analizando…' : 'Analizar Imagen'}
        </button>
      </form>

      {loading && <Spinner className="mt-4" />}

      {result && (
        <div className="card mt-6">
          <h3 className="text-lg font-semibold">Resultado</h3>
          <div className="mt-2 text-sm">
            <div>Normal: {(result.normal * 100).toFixed(2)}%</div>
            <div>Tuberculosis: {(result.tuberculosis * 100).toFixed(2)}%</div>
          </div>

          <pre className="mt-3 bg-sky-50 p-3 rounded-lg overflow-x-auto text-xs">
            {JSON.stringify(result, null, 2)}
          </pre>

          <div className="mt-4 flex gap-2">
            <button className="btn-secondary" onClick={onSaveReport} disabled={!estudioId}>
              Guardar informe IA
            </button>
          </div>
        </div>
      )}

      {toast && <Toast type={toast.type} onClose={() => setToast(null)}>{toast.message}</Toast>}
    </div>
  )
}
