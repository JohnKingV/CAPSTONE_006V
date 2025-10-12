import { api } from './client'

const fromApi = i => ({
  id: i.id,
  estudio_id: i.estudio_id,
  filename: i.filename,
  url: i.url ?? '',
  mimetype: i.mimetype ?? '',
  size_bytes: i.size_bytes ?? null,
  creado_en: i.creado_en
})
const toApiCreate = i => ({
  estudio_id: Number(i.estudio_id),
  filename: i.filename?.trim(),
  url: i.url?.trim() || null,
  mimetype: i.mimetype?.trim() || null,
  size_bytes: i.size_bytes !== undefined && i.size_bytes !== '' ? Number(i.size_bytes) : null
})
const toApiUpdate = i => ({
  estudio_id: i.estudio_id !== undefined ? Number(i.estudio_id) : null,
  filename: i.filename ?? null,
  url: i.url ?? null,
  mimetype: i.mimetype ?? null,
  size_bytes: i.size_bytes !== undefined ? (i.size_bytes !== '' ? Number(i.size_bytes) : null) : null
})

export const listImagenes = async(params={})=> (await api.get('/imagenes', { params })).data.map(fromApi)
export const getImagen = async(id)=> fromApi((await api.get(`/imagenes/${id}`)).data)
export const createImagen = async(p)=> fromApi((await api.post('/imagenes', toApiCreate(p))).data)
export const updateImagen = async(id,p)=> fromApi((await api.patch(`/imagenes/${id}`, toApiUpdate(p))).data)
export const deleteImagen = async(id)=> { await api.delete(`/imagenes/${id}`); return true }
