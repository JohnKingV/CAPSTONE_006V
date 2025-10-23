// frontend/src/pages/ConfigPage.jsx
import React, { useEffect, useState } from 'react'
import { api, getApiBase, setApiBase, clearApiBase } from '../api/client'
import { Toast } from '../components/ui/Toast'
import Spinner from '../components/ui/Spinner'

export default function ConfigPage(){
  const [value, setValue] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')
  const [warn, setWarn] = useState('')
  const [err, setErr] = useState('')

  useEffect(()=>{
    const v = getApiBase(); setValue(v); setWarn(v.endsWith('/predict') ? 'Tu URL termina en /predict. Guardaremos la base sin la ruta; el cliente agregará /predict automáticamente.' : '')
  }, [])

  function stripPredict(u){ try{ return u.replace(/\/+$/,'').replace(/\/predict$/,'') }catch{return u} }

  async function onSave(e){
    e?.preventDefault()
    setBusy(true); setErr(''); setMsg('')
    try{
      const base = setApiBase(stripPredict(value))
      setValue(base)
      setMsg('Guardado.')
    }catch(e){
      setErr(e?.message || 'Error guardando')
    }finally{ setBusy(false) }
  }

  function onReset(){
    setBusy(true); setErr(''); setMsg('')
    try{
      const base = clearApiBase()
      setValue(base)
      setMsg('Reiniciado al valor de .env')
    }catch(e){
      setErr(e?.message || 'Error reiniciando')
    }finally{ setBusy(false) }
  }

  async function onTest(){
    setBusy(true); setErr(''); setMsg('')
    try{
      // Primero intentamos /_ping
      try {
        const { data } = await api.get('/_ping', { validateStatus: ()=>true })
        if (data?.ok) { setMsg('Conexión OK'); setBusy(false); return }
      } catch {}
      // Fallback: GET a la raíz para verificar que responde algo
      const res = await api.get('/', { validateStatus: ()=>true })
      setMsg(`Respuesta HTTP ${res.status} desde la base (OK = 2xx/4xx con CORS permitido)`)
    }catch(e){
      setErr(e?.message || 'No se pudo conectar')
    }finally{ setBusy(false) }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <h2 className="text-2xl font-semibold">Configuración</h2>
      {warn && <Toast type="warning" onClose={()=>setWarn('')}>{warn}</Toast>}
      {msg && <Toast type="success" onClose={()=>setMsg('')}>{msg}</Toast>}
      {err && <Toast type="error" onClose={()=>setErr('')}>{err}</Toast>}

      <form onSubmit={onSave} className="rounded-xl border bg-white p-4 space-y-3">
        <label className="block">
          <span className="text-sm text-slate-600">URL de la API (por ejemplo, tu Colab o EC2)</span>
          <input
            type="text"
            className="mt-1 w-full rounded-lg border px-3 py-2"
            placeholder="http://3.18.219.26:8000"
            value={value}
            onChange={(e)=> setValue(e.target.value)}
            disabled={busy}
          />
        </label>
        <div className="flex gap-2">
          <button type="submit" disabled={busy} className="px-4 py-2 rounded-lg bg-sky-600 text-white disabled:opacity-50">
            {busy ? <span className="inline-flex items-center gap-2"><Spinner/> Guardando…</span> : 'Guardar'}
          </button>
          <button type="button" onClick={onReset} disabled={busy} className="px-4 py-2 rounded-lg border">
            Usar .env (reset)
          </button>
          <button type="button" onClick={onTest} disabled={busy} className="px-4 py-2 rounded-lg border">
            Probar conexión
          </button>
        </div>
        <p className="text-xs text-slate-500">
          Consejo: no incluyas una barra final. Ej: <code>http://3.18.219.26:8000</code>
        </p>
      </form>
    </div>
  )
}
