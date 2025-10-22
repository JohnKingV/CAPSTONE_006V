import { useEffect, useMemo, useState } from 'react'
import { api, parseApiError } from '../../api/client'

const empty = { paciente_id:'', titulo:'', descripcion:'', fecha_estudio:'', medico_id:'' }

export default function StudyForm({ initial = empty, onSubmit }) {
  const [form, setForm] = useState({ ...empty, ...initial })
  useEffect(() => { setForm({ ...empty, ...initial }) }, [initial]) // ✅ sync al editar

  // === PACIENTES (lista + búsqueda local) ===
  const [pacientes, setPacientes] = useState([])
  const [pacLoading, setPacLoading] = useState(false)
  const [pacError, setPacError] = useState('')
  const [qPac, setQPac] = useState('')

  useEffect(() => {
    let abort = false
    ;(async () => {
      try {
        setPacLoading(true)
        const { data } = await api.get('/pacientes')
        const items = Array.isArray(data) ? data : (data?.items || [])
        const mapped = items.map(p => ({
          id: p.id ?? p.paciente_id ?? p.ID,
          nombre: [p.nombres ?? p.nombre, p.apellidos].filter(Boolean).join(' ') || `Paciente ${p.id}`,
          rut: p.rut ?? p.documento ?? '',
          email: p.email ?? '',
        })).sort((a, b) => a.nombre.localeCompare(b.nombre))
        if (!abort) setPacientes(mapped)
      } catch (err) {
        if (!abort) setPacError(parseApiError(err))
      } finally {
        if (!abort) setPacLoading(false)
      }
    })()
    return () => { abort = true }
  }, [])

  const pacFiltrados = useMemo(() => {
    const t = qPac.trim().toLowerCase()
    if (!t) return pacientes
    return pacientes.filter(p =>
      p.nombre.toLowerCase().includes(t) ||
      (p.rut || '').toLowerCase().includes(t) ||
      (p.email || '').toLowerCase().includes(t)
    )
  }, [qPac, pacientes])

  // === MÉDICOS (lista) ===
  const [medicos, setMedicos] = useState([])
  const [medicosLoading, setMedicosLoading] = useState(false)
  const [medicosError, setMedicosError] = useState('')

  useEffect(() => {
    let abort = false
    ;(async () => {
      try {
        setMedicosLoading(true)
        const { data } = await api.get('/medicos')
        const items = Array.isArray(data) ? data : (data?.items || [])
        const mapped = items.map(m => ({
          id: m.id ?? m.medico_id ?? m.ID,
          nombre: [m.nombres, m.apellidos].filter(Boolean).join(' ') || m.nombre || `Médico ${m.id}`,
        })).sort((a, b) => a.nombre.localeCompare(b.nombre))
        if (!abort) setMedicos(mapped)
      } catch (err) {
        if (!abort) setMedicosError(parseApiError(err))
      } finally {
        if (!abort) setMedicosLoading(false)
      }
    })()
    return () => { abort = true }
  }, [])

  function handle(e) {
    const { name, value } = e.target
    setForm(s => ({ ...s, [name]: value }))
  }

  function submit(e) {
    e.preventDefault()
    const payload = { ...form }

    // ✅ paciente_id obligatorio y numérico
    payload.paciente_id = Number(payload.paciente_id)
    if (!payload.paciente_id || Number.isNaN(payload.paciente_id)) {
      alert('Selecciona un paciente válido'); return
    }

    // ✅ médico opcional
    if (payload.medico_id === '' || payload.medico_id == null) {
      delete payload.medico_id
    } else {
      payload.medico_id = Number(payload.medico_id)
    }

    onSubmit?.(payload)
  }

  return (
    <form onSubmit={submit} className='grid grid-cols-6 gap-3'>
      {/* === PACIENTE: buscador + select === */}
      <div className='col-span-2 flex flex-col gap-2'>
        <label className='text-sm text-slate-600'>Paciente</label>
        <input
          className='input'
          placeholder='Buscar por nombre, RUT o email…'
          value={qPac}
          onChange={(e) => setQPac(e.target.value)}
          disabled={pacLoading}
          aria-label='Buscar paciente'
        />
        <select
          name='paciente_id'
          className='input'
          value={form.paciente_id ?? ''}
          onChange={handle}
          disabled={pacLoading || !!pacError}
          aria-label='Seleccionar paciente'
          required
        >
          <option value=''>{pacLoading ? 'Cargando…' : '— Selecciona paciente —'}</option>
          {pacFiltrados.map(p => (
            <option key={p.id} value={String(p.id)}>
              {p.nombre}{p.rut ? ` — ${p.rut}` : ''}
            </option>
          ))}
        </select>
        {pacError && <div className='text-xs text-red-600'>No se pudieron cargar los pacientes: {pacError}</div>}
      </div>

      {/* Título */}
      <input
        name='titulo'
        placeholder='Título'
        className='input col-span-2'
        value={form.titulo}
        onChange={handle}
        required
      />

      {/* Fecha */}
      <input
        name='fecha_estudio'
        type='date'
        className='input'
        value={form.fecha_estudio}
        onChange={handle}
      />

      {/* === MÉDICO: select (opcional) === */}
      <select
        name='medico_id'
        className='input'
        value={form.medico_id ?? ''}           // '' = sin médico
        onChange={handle}
        disabled={medicosLoading || !!medicosError}
        aria-label='Seleccionar médico (opcional)'
      >
        <option value=''>{medicosLoading ? 'Cargando…' : '— Sin médico —'}</option>
        {medicos.map(m => (
          <option key={m.id} value={String(m.id)}>{m.nombre}</option>
        ))}
      </select>
      {medicosError && (
        <div className='col-span-6 text-xs text-red-600'>
          No se pudieron cargar los médicos: {medicosError}
        </div>
      )}

      {/* Descripción */}
      <input
        name='descripcion'
        placeholder='Descripción'
        className='input col-span-6'
        value={form.descripcion}
        onChange={handle}
      />

      {/* Guardar */}
      <div className='col-span-6 flex justify-end'>
        <button className='btn-primary'>Guardar</button>
      </div>
    </form>
  )
}
