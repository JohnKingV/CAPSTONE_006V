import { api } from './client'
const fromApi = e => ({ id:e.id, paciente_id:e.paciente_id, titulo:e.titulo, descripcion:e.descripcion??'', fecha_estudio:e.fecha_estudio??'', medico_id:e.medico_id??'', creado_en:e.creado_en })
const toApiCreate = e => ({ paciente_id:Number(e.paciente_id), titulo:e.titulo?.trim(), descripcion:e.descripcion?.trim()||null, fecha_estudio:e.fecha_estudio||null, medico_id:e.medico_id?Number(e.medico_id):null })
const toApiUpdate = e => ({ paciente_id: e.paciente_id!==undefined ? Number(e.paciente_id) : null, titulo:e.titulo??null, descripcion:e.descripcion??null, fecha_estudio:e.fecha_estudio??null, medico_id: e.medico_id!==undefined ? (e.medico_id?Number(e.medico_id):null) : null })
export const listEstudios = async()=> (await api.get('/estudios')).data.map(fromApi)
export const getEstudio = async(id)=> fromApi((await api.get(`/estudios/${id}`)).data)
export const createEstudio = async(p)=> fromApi((await api.post('/estudios', toApiCreate(p))).data)
export const updateEstudio = async(id,p)=> fromApi((await api.patch(`/estudios/${id}`, toApiUpdate(p))).data)
export const deleteEstudio = async(id)=> { await api.delete(`/estudios/${id}`); return true }