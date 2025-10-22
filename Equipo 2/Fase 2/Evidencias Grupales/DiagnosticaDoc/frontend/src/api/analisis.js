// frontend/src/api/analisis.js
import { api } from './client'

function resolvePredictPath(){
  try{
    const base = api?.defaults?.baseURL || ''
    // Si el usuario guardó en /config una URL que ya termina en /predict,
    // no volvemos a agregarlo para evitar /predict/predict
    return /\/predict$/.test(base) ? '' : '/predict'
  }catch{ return '/predict' }
}

// Sube imagen y obtiene predicciones del backend (POST /predict)
export async function predictXRay(file) {
  const form = new FormData()
  form.append('file', file, file.name)
  form.append('image', file, file.name)
  try{
    const path = resolvePredictPath()
    const res = await api.post(path, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000,
      validateStatus: () => true, // dejamos pasar para inspeccionar status
    })
    if (res.status >= 200 && res.status < 300) return res.data
    const detail = (res.data && (res.data.detail || res.data.error)) || ''
    throw new Error(`HTTP ${res.status} ${detail}`.trim())
  }catch(err){
    // Propagamos con mensaje legible
    throw new Error(err?.message || 'Fallo en /predict')
  }
}
