// frontend/src/pages/AnalisisRxPage.jsx
import React, { useEffect, useMemo, useState } from 'react'
import { predictXRay } from '../api/analisis'
import Spinner from '../components/ui/Spinner'
import { Toast } from '../components/ui/Toast'
import { listEstudios } from '../api/estudios'
import { createInforme } from '../api/informes'
import { parseApiError } from '../api/client'

const ACCEPTED = ['image/jpeg','image/png']
const MAX_MB = 25

export default function AnalisisRxPage(){
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [busyPredict, setBusyPredict] = useState(false)
  const [busySave, setBusySave] = useState(false)
  const [error, setError] = useState('')
  const [okMsg, setOkMsg] = useState('')
  const [raw, setRaw] = useState(null)

  const [normalPct, setNormalPct] = useState('–')
  const [tbPct, setTbPct] = useState('–')
  const [progress, setProgress] = useState(0)

  // Guardado de informe
  const [estudios, setEstudios] = useState([])
  const [estudioId, setEstudioId] = useState('')
  const [estadoId, setEstadoId] = useState(1) // 1 = Borrador (ajústalo si tu catálogo usa otro id)
  const [observaciones, setObservaciones] = useState('')

  useEffect(() => {
    // Cargar estudios para el select
    (async () => {
      try {
        const data = await listEstudios()
        setEstudios(data)
      } catch (e) {
        setError(parseApiError(e))
      }
    })()
  }, [])

  useEffect(() => {
    // Limpiar preview al cambiar file
    if (!file) { setPreview(null); return }
    const url = URL.createObjectURL(file)
    setPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  const canPredict = useMemo(() => !!file && !busyPredict, [file, busyPredict])
  const canSave = useMemo(() => {
    return !!raw && !!estudioId && !busySave
  }, [raw, estudioId, busySave])

  function onPick(e){
    const f = e.target.files?.[0]
    if (!f) return
    if (!ACCEPTED.includes(f.type)) return setError('Formato no soportado. Usa JPG o PNG.')
    if (f.size > MAX_MB*1024*1024) return setError(`El archivo supera ${MAX_MB}MB`)
    setError('')
    setOkMsg('')
    setFile(f)
  }

  async function onPredict(){
    if (!file) return setError('Selecciona una imagen')
    setBusyPredict(true)
    setError('')
    setOkMsg('')
    setProgress(0)
    try{
      const data = await predictXRay(file, (p)=>setProgress(p))
      setRaw(data?.raw || data)
      const n = Math.round((data.normal || 0)*100)
      const t = Math.round((data.tuberculosis || 0)*100)
      setNormalPct(`${n}%`)
      setTbPct(`${t}%`)
      // Sugiere observaciones
      setObservaciones(`Informe IA (auto): Normal=${n}%, Tuberculosis=${t}%`)
    }catch(e){
      setError(e?.message || 'Error al procesar')
    }finally{
      setBusyPredict(false)
    }
  }

  async function onSaveInforme(){
    if (!raw) return setError('Primero ejecuta el análisis IA')
    if (!estudioId) return setError('Selecciona un estudio')
    setBusySave(true)
    setError('')
    setOkMsg('')

    // Construye contenido del informe con los datos de IA
    const contenido = JSON.stringify({
      fuente: 'IA',
      resultado: {
        normal: raw?.normal ?? null,
        tuberculosis: raw?.tuberculosis ?? null,
        predictions: raw?.predictions ?? null
      }
    }, null, 2)

    try{
      await createInforme({
        estudio_id: Number(estudioId),
        contenido,                   // requerido por backend
        estado_id: Number(estadoId), // requerido por backend
        observaciones: observaciones?.trim() || null
      })
      setOkMsg('Informe IA guardado ✅')
    }catch(e){
      setError(parseApiError(e))
    }finally{
      setBusySave(false)
    }
  }

  return (
    <div className="page">
      <div className="flex items-center justify-between mb-4">
        <h2 className="title-page">Análisis de Rayos X (IA)</h2>
      </div>

      {/* Picker de imagen */}
      <div className="rounded-xl border bg-white p-4 mb-4">
        <div className="flex items-center gap-3">
          <input type="file" accept={ACCEPTED.join(',')} onChange={onPick}/>
          <button className="btn-primary" disabled={!canPredict} onClick={onPredict}>
            {busyPredict ? <Spinner/> : 'Analizar'}
          </button>
          {busyPredict && <div className="text-sm text-slate-600">Subiendo… {progress}%</div>}
        </div>
        {preview && (
          <div className="mt-3">
            <img src={preview} alt="preview" className="max-h-72 rounded-lg border"/>
          </div>
        )}
      </div>

      {/* Resultados */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="rounded-xl border bg-white p-4">
          <h3 className="font-medium mb-3">Resultados</h3>
          <div className="flex gap-6 text-lg">
            <div><span className="text-slate-500">Normal:</span> <b>{normalPct}</b></div>
            <div><span className="text-slate-500">Tuberculosis:</span> <b>{tbPct}</b></div>
          </div>
        </div>

        {/* Guardar informe IA */}
        <div className="rounded-xl border bg-white p-4">
          <h3 className="font-medium mb-3">Guardar informe IA</h3>
          <div className="grid md:grid-cols-2 gap-3">
            <label className="text-sm text-slate-600">Estudio</label>
            <select
              className="input"
              value={estudioId}
              onChange={e=>setEstudioId(e.target.value)}
            >
              <option value="">— Selecciona —</option>
              {estudios.map(e=>(
                <option key={e.id} value={e.id}>
                  #{e.id} • {e.titulo_estudio || 'Estudio'}
                </option>
              ))}
            </select>

            <label className="text-sm text-slate-600">Estado informe (id)</label>
            <input
              className="input"
              type="number"
              value={estadoId}
              onChange={e=>setEstadoId(e.target.value)}
              placeholder="1 = Borrador (ajusta según tu catálogo)"
            />

            <label className="text-sm text-slate-600 col-span-full">Observaciones</label>
            <textarea
              className="input col-span-full min-h-24"
              value={observaciones}
              onChange={e=>setObservaciones(e.target.value)}
              placeholder="Notas adicionales…"
            />

            <div className="col-span-full flex justify-end">
              <button className="btn-primary" disabled={!canSave} onClick={onSaveInforme}>
                {busySave ? <Spinner/> : 'Guardar informe IA'}
              </button>
            </div>
          </div>
        </div>

        {/* Respuesta cruda */}
        <div className="rounded-xl border bg-white p-4 md:col-span-2">
          <h3 className="font-medium mb-2">Respuesta cruda</h3>
          <pre className="text-xs bg-slate-50 p-3 rounded-lg overflow-auto max-h-72">
{JSON.stringify(raw, null, 2)}
          </pre>
        </div>
      </div>

      {error && <Toast type="error" onClose={()=>setError('')}>{error}</Toast>}
      {okMsg && <Toast type="success" onClose={()=>setOkMsg('')}>{okMsg}</Toast>}
    </div>
  )
}
