import axios from 'axios'
export const api = axios.create({ baseURL: (import.meta.env.VITE_API_URL?.replace(/\/$/, '') || 'http://127.0.0.1:8080'), headers: { 'Content-Type': 'application/json' }, timeout: 10000 })
export function parseApiError(err){ if(!err) return 'Error desconocido'
  if(err.response){ const { status, data } = err.response; if(status===422 && Array.isArray(data?.detail)){ const parts=data.detail.map(d=>`${d.loc?.join('.')}: ${d.msg}`); return `Validación: ${parts.join(' | ')}` }
    if(typeof data==='string') return `${status}: ${data}`; if(data?.detail) return `${status}: ${typeof data.detail==='string'?data.detail:JSON.stringify(data.detail)}`; return `${status}: Error en la solicitud` }
  if(err.request) return 'Sin respuesta del servidor (¿URL correcta / servidor arriba?)'; return err.message||'Error desconocido' }