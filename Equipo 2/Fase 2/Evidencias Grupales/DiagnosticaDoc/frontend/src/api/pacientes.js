// frontend/src/api/pacientes.js
import { api } from './client'


const asNum = v => (v === '' || v == null ? null : Number(v))
const asDateOrNull = v => (v ? String(v).slice(0, 10) : null) 

const fromApi = p => ({
  id: p.id,
  nombres: p.nombres,
  apellidos: p.apellidos,
  documento: p.documento ?? '',
  telefono: p.telefono ?? '',
  email: p.email ?? '',
  fecha_nacimiento: p.fecha_nacimiento ?? '',
  creado_en: p.creado_en,
})

const toApiCreate = p => ({
  nombres: p.nombres?.trim(),
  apellidos: p.apellidos?.trim(),
  documento: p.documento?.trim() || null,
  telefono: p.telefono?.trim() || null,
  email: p.email?.trim() || null,
  fecha_nacimiento: asDateOrNull(p.fecha_nacimiento),
})

const toApiUpdate = p => ({
  nombres: p.nombres ?? null,
  apellidos: p.apellidos ?? null,
  documento: p.documento ?? null,
  telefono: p.telefono ?? null,
  email: p.email ?? null,
  fecha_nacimiento: p.fecha_nacimiento === '' ? null : asDateOrNull(p.fecha_nacimiento),
})

export async function listPacientes() {
  const { data } = await api.get('/pacientes')
  const rows = Array.isArray(data) ? data : (data?.items || [])
  return rows.map(fromApi)
}

export async function getPaciente(id) {
  const { data } = await api.get(`/pacientes/${id}`)
  return fromApi(data)
}

export async function createPaciente(payload) {
  const { data } = await api.post('/pacientes', toApiCreate(payload))
  return fromApi(data)
}

export async function updatePaciente(id, payload) {
  const { data } = await api.patch(`/pacientes/${id}`, toApiUpdate(payload))
  return fromApi(data)
}

export async function deletePaciente(id) {
  await api.delete(`/pacientes/${id}`)
  return true
}
