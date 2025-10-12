import { api } from './client'
const fromApi = m => ({ id:m.id, nombre:m.nombre, email:m.email??'', especialidad:m.especialidad??'', registro_colegio:m.registro_colegio??'', creado_en:m.creado_en })
const toApiCreate = m => ({ nombre:m.nombre?.trim(), email:m.email?.trim()||null, especialidad:m.especialidad?.trim()||null, registro_colegio:m.registro_colegio?.trim()||null })
const toApiUpdate = m => ({ nombre:m.nombre??null, email:m.email??null, especialidad:m.especialidad??null, registro_colegio:m.registro_colegio??null })
export const listMedicos = async()=> (await api.get('/medicos')).data.map(fromApi)
export const getMedico = async(id)=> fromApi((await api.get(`/medicos/${id}`)).data)
export const createMedico = async(p)=> fromApi((await api.post('/medicos', toApiCreate(p))).data)
export const updateMedico = async(id,p)=> fromApi((await api.patch(`/medicos/${id}`, toApiUpdate(p))).data)
export const deleteMedico = async(id)=> { await api.delete(`/medicos/${id}`); return true }