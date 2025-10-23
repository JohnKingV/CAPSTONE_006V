// frontend/src/api/analisis.js
import api, { parseApiError } from './client'

const ACCEPTED_TYPES = ['image/jpeg', 'image/png']
const MAX_MB = 25

function assertFileOk(file) {
  if (!file) throw new Error('Selecciona un archivo de imagen')
  if (!ACCEPTED_TYPES.includes(file.type)) {
    throw new Error('Formato no soportado. Sube JPG o PNG')
  }
  if (file.size > MAX_MB * 1024 * 1024) {
    throw new Error(`El archivo supera ${MAX_MB}MB`)
  }
}

/**
 * Analiza una radiografía con IA.
 * @param {File} file - archivo imagen (JPG/PNG)
 * @param {(pct:number)=>void} onProgress - callback opcional de progreso 0..100
 * @returns {Promise<{normal:number,tuberculosis:number,predictions?:Array}>}
 */
export async function predictXRay(file, onProgress) {
  assertFileOk(file)

  const form = new FormData()
  // El backend acepta 'file' o 'image'; usamos 'file'
  form.append('file', file, file.name)

  // Config común (dejamos que axios ponga el boundary)
  const cfg = {
    timeout: 90000,
    onUploadProgress: (evt) => {
      if (onProgress && evt.total) {
        const pct = Math.round((evt.loaded / evt.total) * 100)
        onProgress(pct)
      }
    },
  }

  try {
    // 1) Ruta principal
    const { data } = await api.post('/predict', form, cfg)
    return normalizeResult(data)
  } catch (err) {
    // 422 típico si Swagger/cliente manda campos raros → probamos la flexible
    const status = err?.response?.status
    if (status === 422) {
      try {
        const { data } = await api.post('/predict_flex', form, cfg)
        return normalizeResult(data)
      } catch (err2) {
        throw new Error(parseApiError(err2))
      }
    }
    throw new Error(parseApiError(err))
  }
}

/** Normaliza la respuesta para que el front no reviente si cambian campos */
function normalizeResult(data) {
  const normal = typeof data?.normal === 'number' ? data.normal : 0
  const tuberculosis = typeof data?.tuberculosis === 'number' ? data.tuberculosis : 0
  const predictions =
    Array.isArray(data?.predictions)
      ? data.predictions
      : [
          { label: 'Normal', score: normal },
          { label: 'Tuberculosis', score: tuberculosis },
        ]
  return { normal, tuberculosis, predictions, raw: data }
}

export default { predictXRay }
