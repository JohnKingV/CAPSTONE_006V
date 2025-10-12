import { useEffect, useState } from 'react'
import Spinner from '../components/ui/Spinner'
import { Toast } from '../components/ui/Toast'
import { listInformes, createInforme, updateInforme, deleteInforme } from '../api/informes'
import { parseApiError } from '../api/client'

export default function ReportsPage(){
  const [loading, setLoading] = useState(true)
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)

  const [form, setForm] = useState({ estudio_id:'', contenido:'', estado_id:'', observaciones:'' })
  function handle(e){ const {name,value}=e.target; setForm(s=>({...s,[name]:value})) }

  async function load(){
    setLoading(true)
    try{ setRows(await listInformes()) } catch(e){ setError(parseApiError(e)) } finally { setLoading(false) }
  }
  useEffect(()=>{ load() },[])

  function startEdit(r){
    setEditing(r)
    setForm({ estudio_id:r.estudio_id, contenido:r.contenido, estado_id:r.estado_id, observaciones:r.observaciones })
  }

  async function save(e){
    e.preventDefault()
    try{
      if(editing){
        const saved = await updateInforme(editing.id, form)
        setRows(rs => rs.map(r => r.id===saved.id ? saved : r))
      }else{
        const saved = await createInforme(form)
        setRows(rs => [saved, ...rs])
      }
      setEditing(null)
      setForm({ estudio_id:'', contenido:'', estado_id:'', observaciones:'' })
      setError('Guardado')
    }catch(e){ setError(parseApiError(e)) }
  }

  async function remove(id){
    if(!confirm('¿Eliminar informe?')) return
    try{ await deleteInforme(id); setRows(rs => rs.filter(r => r.id!==id)); setError('Eliminado') }catch(e){ setError(parseApiError(e)) }
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold text-sky-900">Informes</h1>
      <form onSubmit={save} className="card grid grid-cols-6 gap-3">
        <input name="estudio_id" className="input" placeholder="Estudio ID" value={form.estudio_id} onChange={handle} required />
        <input name="estado_id" className="input" placeholder="Estado ID" value={form.estado_id} onChange={handle} required />
        <textarea name="contenido" className="input col-span-6" placeholder="Contenido" value={form.contenido} onChange={handle} required />
        <input name="observaciones" className="input col-span-6" placeholder="Observaciones (opcional)" value={form.observaciones} onChange={handle} />
        <div className="col-span-6 flex justify-end gap-2">
          {editing && <button type="button" className="btn-secondary" onClick={()=>{ setEditing(null); setForm({ estudio_id:'', contenido:'', estado_id:'', observaciones:'' }) }}>Cancelar</button>}
          <button className="btn-primary">{editing? 'Actualizar' : 'Crear'}</button>
        </div>
      </form>
      <div className="card">
        {loading? <Spinner/> : (
          <table className="min-w-full">
            <thead className="bg-sky-50"><tr>{['Estudio','Estado','Contenido','Observaciones',''].map(h=>(<th key={h} className="px-3 py-2 text-left">{h}</th>))}</tr></thead>
            <tbody>
              {rows.map(r=> (
                <tr key={r.id} className="odd:bg-white even:bg-sky-50/30">
                  <td className="px-3 py-2">{r.estudio_id}</td>
                  <td className="px-3 py-2">{r.estado_id}</td>
                  <td className="px-3 py-2 max-w-[420px] truncate" title={r.contenido}>{r.contenido}</td>
                  <td className="px-3 py-2 max-w-[260px] truncate" title={r.observaciones}>{r.observaciones}</td>
                  <td className="px-3 py-2 text-right">
                    <button className="btn-ghost mr-2" onClick={()=>startEdit(r)}>Editar</button>
                    <button className="btn-danger" onClick={()=>remove(r.id)}>Borrar</button>
                  </td>
                </tr>
              ))}
              {rows.length===0 && <tr><td colSpan={5} className="text-center p-6 text-sky-900/60">Sin informes</td></tr>}
            </tbody>
          </table>
        )}
      </div>
      <Toast message={error} onClose={()=>setError('')} />
    </div>
  )
}
