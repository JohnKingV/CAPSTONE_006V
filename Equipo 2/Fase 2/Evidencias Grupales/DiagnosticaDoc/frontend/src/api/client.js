// frontend/src/api/client.js
import axios from 'axios'

// 🔹 Normaliza la base (sin barra final) y con fallback local
export const API_BASE =
  (import.meta.env.VITE_API_URL?.replace(/\/+$/, '') || 'http://127.0.0.1:8080')

// 🔹 Instancia Axios con defaults seguros
export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10s
})

// 🔹 Parseo de errores (mantiene tu lógica, con 2 casos extra)
export function parseApiError(err) {
  if (!err) return 'Error desconocido'

  // Timeout de Axios
  if (err.code === 'ECONNABORTED') return 'Tiempo de espera agotado (timeout)'

  // Respuesta del servidor con status
  if (err.response) {
    const { status, data } = err.response

    // 422 con detalle de validación (tu formato)
    if (status === 422 && Array.isArray(data?.detail)) {
      const parts = data.detail.map(d => `${d.loc?.join('.')}: ${d.msg}`)
      return `Validación: ${parts.join(' | ')}`
    }

    if (typeof data === 'string') return `${status}: ${data}`
    if (data?.detail) {
      return `${status}: ${
        typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      }`
    }
    return `${status}: Error en la solicitud`
  }

  // Petición enviada pero sin respuesta (CORS, DNS, server caído)
  if (err.request) {
    return 'Sin respuesta del servidor (¿URL correcta / servidor arriba?)'
  }

  // Otros errores (setup, cancelación, etc.)
  return err.message || 'Error desconocido'
}

// 🔹 Helpers opcionales (uso idéntico de datos; lanzan Error con mensaje parseado)
export async function apiGet(path, config) {
  try {
    const { data } = await api.get(path, config)
    return data
  } catch (err) {
    throw new Error(parseApiError(err))
  }
}

export async function apiPost(path, body, config) {
  try {
    const { data } = await api.post(path, body, config)
    return data
  } catch (err) {
    throw new Error(parseApiError(err))
  }
}

export async function apiPut(path, body, config) {
  try {
    const { data } = await api.put(path, body, config)
    return data
  } catch (err) {
    throw new Error(parseApiError(err))
  }
}

export async function apiDelete(path, config) {
  try {
    const { data } = await api.delete(path, config)
    return data
  } catch (err) {
    throw new Error(parseApiError(err))
  }
}

// ==== Runtime baseURL override via localStorage ====
import { getEndpoint, setEndpoint as _setStore, clearEndpoint as _clearStore, normalizeBase } from '../lib/storage'

function _initialBase(){
  const saved = getEndpoint()
  return saved || API_BASE
}

export function getApiBase(){
  try{ return api?.defaults?.baseURL || _initialBase() }catch{ return _initialBase() }
}

export function setApiBase(url){
  const clean = normalizeBase(url)
  if (clean) _setStore(clean); else _clearStore()
  if (api && api.defaults) api.defaults.baseURL = clean || API_BASE
  return getApiBase()
}

export function clearApiBase(){
  _clearStore()
  if (api && api.defaults) api.defaults.baseURL = API_BASE
  return getApiBase()
}
// ==== end override ====
