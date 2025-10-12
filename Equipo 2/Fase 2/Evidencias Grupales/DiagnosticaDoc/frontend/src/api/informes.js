import { api } from './client'

const fromApi = r => ({
  id: r.id,
  estudio_id: r.estudio_id,
  contenido: r.contenido,
  estado_id: r.estado_id,
  observaciones: r.observaciones ?? '',
  creado_en: r.creado_en
})
const toApiCreate = r => ({
  estudio_id: Number(r.estudio_id),
  contenido: r.contenido?.trim(),
  estado_id: Number(r.estado_id),
  observaciones: r.observaciones?.trim() || null
})
const toApiUpdate = r => ({
  contenido: r.contenido ?? null,
  estado_id: r.estado_id !== undefined ? Number(r.estado_id) : null,
  observaciones: r.observaciones ?? null
})

export const listInformes = async()=> (await api.get('/informes')).data.map(fromApi)
export const getInforme = async(id)=> fromApi((await api.get(`/informes/${id}`)).data)
export const createInforme = async(p)=> fromApi((await api.post('/informes', toApiCreate(p))).data)
export const updateInforme = async(id,p)=> fromApi((await api.patch(`/informes/${id}`, toApiUpdate(p))).data)
export const deleteInforme = async(id)=> { await api.delete(`/informes/${id}`); return true }
