// frontend/src/api/client.js
import axios from 'axios'
import {
  getEndpoint,
  setEndpoint as _setStore,
  clearEndpoint as _clearStore,
  normalizeBase,
} from '../lib/storage'

// 🔹 Base preferida: .env primero, y si no hay, usa lo guardado
const ENV_BASE = (import.meta.env.VITE_API_URL?.replace(/\/+$/, '') || 'http://127.0.0.1:8000')
const SAVED_BASE = getEndpoint()
export const API_BASE = ENV_BASE || SAVED_BASE || 'http://127.0.0.1:8000'

// 🔹 Instancia Axios
export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// === Request: agrega Authorization si hay token ===
api.interceptors.request.use((config) => {
  try {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  } catch {}
  return config
})

// === Response: normaliza mensajes frecuentes ===
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.code === 'ECONNABORTED') {
      err.parsedMessage = 'Tiempo de espera agotado (timeout)'
    } else if (err.response?.status === 401) {
      err.parsedMessage = '401: No autorizado'
    }
    return Promise.reject(err)
  }
)

// 🔹 Parseo de errores uniforme
export function parseApiError(err) {
  if (!err) return 'Error desconocido'
  if (err.parsedMessage) return err.parsedMessage
  if (err.code === 'ECONNABORTED') return 'Tiempo de espera agotado (timeout)'

  if (err.response) {
    const { status, data } = err.response
    if (status === 422 && Array.isArray(data?.detail)) {
      const parts = data.detail.map(d => `${d.loc?.join('.')}: ${d.msg}`)
      return `Validación: ${parts.join(' | ')}`
    }
    if (typeof data === 'string') return `${status}: ${data}`
    if (data?.detail) {
      return `${status}: ${typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)}`
    }
    return `${status}: Error en la solicitud`
  }

  if (err.request) return 'Sin respuesta del servidor (¿URL correcta / servidor arriba?)'
  return err.message || 'Error desconocido'
}

// 🔹 Helpers HTTP
export async function apiGet(path, config) {
  try { const { data } = await api.get(path, config); return data }
  catch (err) { throw new Error(parseApiError(err)) }
}
export async function apiPost(path, body, config) {
  try { const { data } = await api.post(path, body, config); return data }
  catch (err) { throw new Error(parseApiError(err)) }
}
export async function apiPut(path, body, config) {
  try { const { data } = await api.put(path, body, config); return data }
  catch (err) { throw new Error(parseApiError(err)) }
}
export async function apiDelete(path, config) {
  try { const { data } = await api.delete(path, config); return data }
  catch (err) { throw new Error(parseApiError(err)) }
}

// ==== Overrides de baseURL (runtime) ====
function _initialBase() { return ENV_BASE || getEndpoint() || 'http://127.0.0.1:8000' }

export function getApiBase() {
  try { return api?.defaults?.baseURL || _initialBase() }
  catch { return _initialBase() }
}

export function setApiBase(url) {
  const clean = normalizeBase(url)
  if (clean) _setStore(clean); else _clearStore()
  if (api?.defaults) api.defaults.baseURL = clean || ENV_BASE
  return getApiBase()
}

export function clearApiBase() {
  _clearStore()
  if (api?.defaults) api.defaults.baseURL = ENV_BASE
  return getApiBase()
}

// 🔧 Helpers de debugging en ventana (opcional)
if (typeof window !== 'undefined') {
  window.__api = { getApiBase, setApiBase, clearApiBase, ENV_BASE }
}
