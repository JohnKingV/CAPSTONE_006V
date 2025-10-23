// frontend/src/pages/AnalisisRxPage.jsx
import React, { useMemo, useState } from 'react'
import { predictXRay } from '../api/analisis'
import Spinner from '../components/ui/Spinner'
import { Toast } from '../components/ui/Toast'

export default function AnalisisRxPage(){
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [lastStatus, setLastStatus] = useState('')
  const [raw, setRaw] = useState(null)

  const [normalPct, setNormalPct] = useState('–')
  const [tbPct, setTbPct] = useState('–')

  function onPick(e){
    const f = e.target.files?.[0]
    if (!f) return
    setFile(f)
    setRaw(null); setError('')
    setNormalPct('–'); setTbPct('–')
    if (preview) URL.revokeObjectURL(preview)
    setPreview(URL.createObjectURL(f))
  }

  function clamp01(x){ return Math.max(0, Math.min(1, x)) }
  function asPct(x){ return `${Math.round(clamp01(x)*100)}%` }

  function mapPreds(resp){
    let normal = null, tb = null
    if (typeof resp?.normal === 'number') normal = resp.normal
    if (typeof resp?.tuberculosis === 'number') tb = resp.tuberculosis
    const list = resp?.predictions || resp?.top || resp?.result || resp?.classes
    if (Array.isArray(list)){
      for (const p of list){
        const label = String(p.label || p.class || p.name || '').toLowerCase()
        const score = Number(p.score ?? p.prob ?? p.confidence ?? p.value)
        if (!isFinite(score)) continue
        if (label.includes('normal')) normal = score
        if (label.includes('tb') || label.includes('tuberculosis')) tb = score
      }
    }
    if (!normal && !tb && resp && typeof resp === 'object'){
      for (const [k,v] of Object.entries(resp)){
        const label = k.toLowerCase()
        const score = Number(v)
        if (!isFinite(score)) continue
        if (label.includes('normal')) normal = score
        if (label.includes('tb') || label.includes('tuberculosis')) tb = score
      }
    }
    return { normal, tb }
  }

  async function onAnalyze(){
    if (!file) { setError('Primero selecciona una imagen.'); return }
    setBusy(true); setError(''); setRaw(null)
    try{
      const resp = await predictXRay(file)
      setLastStatus('200 OK')
      setRaw(resp)
      const { normal, tb } = mapPreds(resp)
      if (typeof normal === 'number') setNormalPct(asPct(normal))
      if (typeof tb === 'number') setTbPct(asPct(tb))
      if (typeof normal !== 'number' && typeof tb !== 'number'){
        setError('Análisis completado, pero no se reconoció el formato de salida del backend.')
      }
    } catch (e){
      setError(e?.message || 'Error procesando la imagen'); setLastStatus('')
    } finally {
      setBusy(false)
    }
  }

  const nStyle = useMemo(() => ({ width: normalPct.endsWith('%') ? normalPct : '0%' }), [normalPct])
  const tStyle = useMemo(() => ({ width: tbPct.endsWith('%') ? tbPct : '0%' }), [tbPct])

  return (
    <div className="max-w-5xl mx-auto">
      <h2 className="text-2xl font-semibold mb-4">Análisis de rayos X de tórax</h2>

      {error && <Toast type="error" onClose={()=>setError('')}>{error}</Toast>}

      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-3">
          <label className="block">
            <span className="text-sm text-slate-600">Imagen (JPG/PNG)</span>
            <input type="file" accept="image/*" className="mt-1 block w-full"
                   onChange={onPick} disabled={busy}/>
          </label>

          <div className="rounded-xl border bg-white overflow-hidden min-h-[220px] flex items-center justify-center">
            {preview
              ? <img src={preview} alt="preview" className="max-h-[380px] object-contain" />
              : <div className="text-slate-400 text-sm p-6 text-center">Aún no seleccionas imagen</div>}
          </div>

          <button
            onClick={onAnalyze}
            disabled={!file || busy}
            className="px-4 py-2 rounded-xl bg-sky-600 text-white disabled:opacity-50"
          >
            {busy ? <div className="flex items-center gap-2"><Spinner/> Analizando…</div> : 'Analizar'}
          </button>
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border bg-white p-4">
            <h3 className="font-medium mb-2">Resultado</h3>
            <div className="text-xs text-slate-500 mb-2">{lastStatus ? `Estado: ${lastStatus}` : null}</div>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-slate-600 mb-1">Normal</div>
                <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
                  <div className="h-3 bg-emerald-500" style={nStyle} />
                </div>
                <div className="text-right text-sm text-slate-700 mt-1">{normalPct}</div>
              </div>
              <div>
                <div className="text-sm text-slate-600 mb-1">Tuberculosis</div>
                <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
                  <div className="h-3 bg-rose-500" style={tStyle} />
                </div>
                <div className="text-right text-sm text-slate-700 mt-1">{tbPct}</div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-4">
            <h3 className="font-medium mb-2">Respuesta cruda</h3>
            <pre className="text-xs bg-slate-50 p-3 rounded-lg overflow-auto max-h-72">
{JSON.stringify(raw, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  )
}
