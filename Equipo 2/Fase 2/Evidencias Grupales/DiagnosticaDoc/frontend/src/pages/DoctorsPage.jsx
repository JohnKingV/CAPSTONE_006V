import { useEffect, useMemo, useState } from 'react'
import Spinner from '../components/ui/Spinner'
import { Toast } from '../components/ui/Toast'
import DoctorForm from '../components/medicos/DoctorForm'
import { listMedicos, createMedico, updateMedico, deleteMedico } from '../api/medicos'
import { parseApiError } from '../api/client'

export default function DoctorsPage(){
  const [loading, setLoading] = useState(true)
  const [rows, setRows] = useState([])
  const [toast, setToast] = useState({ msg: '', type: 'info' }) // ← separado
  const [editing, setEditing] = useState(null)
  const [saving, setSaving] = useState(false)
  const [deletingId, setDeletingId] = useState(null)
  const [q, setQ] = useState('')

  async function load(){
    setLoading(true)
    try {
      const data = await listMedicos()
      setRows(data)
    } catch (e) {
      setToast({ msg: parseApiError(e), type: 'error' })
    } finally {
      setLoading(false)
    }
  }
  useEffect(()=>{ load() },[])

  const filtered = useMemo(() => {
    const t = q.trim().toLowerCase()
    if (!t) return rows
    return rows.filter(r =>
      (r.nombre || '').toLowerCase().includes(t) ||
      (r.email || '').toLowerCase().includes(t) ||
      (r.especialidad || '').toLowerCase().includes(t) ||
      String(r.registro_colegio || '').includes(t)
    )
  }, [rows, q])

  async function save(form){
    try {
      setSaving(true)
      if (editing) {
        const saved = await updateMedico(editing.id, form)
        setRows(rs => rs.map(r => r.id === saved.id ? saved : r))
        setEditing(null)
        setToast({ msg: 'Médico actualizado', type: 'success' })
      } else {
        const saved = await createMedico(form)
        setRows(rs => [saved, ...rs])
        setToast({ msg: 'Médico creado', type: 'success' })
      }
    } catch (e) {
      setToast({ msg: parseApiError(e), type: 'error' })
    } finally {
      setSaving(false)
    }
  }

  async function remove(id){
    if (!confirm('¿Eliminar médico?')) return
    try {
      setDeletingId(id)
      await deleteMedico(id)
      setRows(rs => rs.filter(r => r.id !== id))
      setToast({ msg: 'Médico eliminado', type: 'success' })
    } catch (e) {
      setToast({ msg: parseApiError(e), type: 'error' })
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className='p-6 space-y-4'>
      <h1 className='text-2xl font-semibold text-sky-900'>Médicos</h1>

      {/* Buscador local pequeño */}
      <div className='flex items-center gap-3'>
        <input
          className='input max-w-sm'
          placeholder='Buscar por nombre, email, especialidad o registro…'
          value={q}
          onChange={e=>setQ(e.target.value)}
        />
        {q && (
          <button className='btn-ghost text-sm' onClick={()=>setQ('')}>Limpiar</button>
        )}
      </div>

      {/* Formulario (remontar al cambiar modo) */}
      <div className='card'>
        <DoctorForm
          key={editing?.id ?? 'new'}         // ← fuerza reset al salir de edición
          initial={editing || undefined}
          onSubmit={save}
          saving={saving}                    // si tu DoctorForm soporta deshabilitar botón
          onCancel={()=>setEditing(null)}    // si tu DoctorForm tiene botón Cancelar
        />
      </div>

      <div className='card'>
        {loading ? <Spinner/> : (
          <table className='min-w-full'>
            <thead className='bg-sky-50'>
              <tr>
                {['Nombre','Email','Especialidad','Registro',''].map(h=>(
                  <th key={h} className='px-3 py-2 text-left'>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map(r => (
                <tr key={r.id} className='odd:bg-white even:bg-sky-50/30'>
                  <td className='px-3 py-2'>{r.nombre || '—'}</td>
                  <td className='px-3 py-2'>
                    {r.email ? <a className='link' href={`mailto:${r.email}`}>{r.email}</a> : '—'}
                  </td>
                  <td className='px-3 py-2'>{r.especialidad || '—'}</td>
                  <td className='px-3 py-2'>{r.registro_colegio || '—'}</td>
                  <td className='px-3 py-2 text-right'>
                    <button
                      className='btn-ghost mr-2'
                      onClick={()=>setEditing(r)}
                      disabled={saving || deletingId === r.id}
                    >
                      Editar
                    </button>
                    <button
                      className='btn-danger'
                      onClick={()=>remove(r.id)}
                      disabled={saving || deletingId === r.id}
                      title={deletingId === r.id ? 'Eliminando…' : 'Borrar'}
                    >
                      {deletingId === r.id ? 'Borrando…' : 'Borrar'}
                    </button>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={5} className='text-center p-6 text-sky-900/60'>Sin médicos</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      <Toast
        message={toast.msg}
        type={toast.type}               // si tu Toast acepta variant/tipo
        onClose={()=>setToast({ msg:'', type:'info' })}
      />
    </div>
  )
}
