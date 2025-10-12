import { useEffect, useState } from 'react'
import Spinner from '../components/ui/Spinner'
import { Toast } from '../components/ui/Toast'
import { listImagenes, createImagen, updateImagen, deleteImagen } from '../api/imagenes'
import { parseApiError } from '../api/client'

export default function ImagesPage(){
  const [loading, setLoading] = useState(true)
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)
  const [filters, setFilters] = useState({ estudio_id: '' })

  const [form, setForm] = useState({ estudio_id:'', filename:'', url:'', mimetype:'', size_bytes:'' })
  function handle(e){ const {name,value}=e.target; setForm(s=>({...s,[name]:value})) }

  async function load(){
    setLoading(true)
    try{
      const params = {}
      if(filters.estudio_id) params.estudio_id = Number(filters.estudio_id)
      setRows(await listImagenes(params))
    } catch(e){ setError(parseApiError(e)) } finally { setLoading(false) }
  }
  useEffect(()=>{ load() },[])

  function startEdit(r){
    setEditing(r)
    setForm({
      estudio_id: r.estudio_id, filename: r.filename, url: r.url, mimetype: r.mimetype,
      size_bytes: r.size_bytes ?? ''
    })
  }

  async function save(e){
    e.preventDefault()
    try{
      if(editing){
        const saved = await updateImagen(editing.id, form)
        setRows(rs => rs.map(r => r.id===saved.id ? saved : r))
      }else{
        const saved = await createImagen(form)
        setRows(rs => [saved, ...rs])
      }
      setEditing(null)
      setForm({ estudio_id:'', filename:'', url:'', mimetype:'', size_bytes:'' })
      setError('Guardado')
    }catch(e){ setError(parseApiError(e)) }
  }

  async function remove(id){
    if(!confirm('¿Eliminar imagen?')) return
    try{ await deleteImagen(id); setRows(rs => rs.filter(r => r.id!==id)); setError('Eliminado') }catch(e){ setError(parseApiError(e)) }
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold text-sky-900">Imágenes</h1>

      <div className="card grid grid-cols-6 gap-3">
        <input className="input" placeholder="Filtrar por Estudio ID" value={filters.estudio_id} onChange={e=>setFilters(s=>({...s, estudio_id:e.target.value}))} />
        <button className="btn-secondary" onClick={load}>Buscar</button>
      </div>

      <form onSubmit={save} className="card grid grid-cols-6 gap-3">
        <input name="estudio_id" className="input" placeholder="Estudio ID" value={form.estudio_id} onChange={handle} required />
        <input name="filename" className="input col-span-2" placeholder="Filename" value={form.filename} onChange={handle} required />
        <input name="url" className="input col-span-3" placeholder="URL (opcional)" value={form.url} onChange={handle} />
        <input name="mimetype" className="input" placeholder="Mimetype (opcional)" value={form.mimetype} onChange={handle} />
        <input name="size_bytes" className="input" placeholder="Size bytes (opcional)" value={form.size_bytes} onChange={handle} />
        <div className="col-span-6 flex justify-end gap-2">
          {editing && <button type="button" className="btn-secondary" onClick={()=>{ setEditing(null); setForm({ estudio_id:'', filename:'', url:'', mimetype:'', size_bytes:'' }) }}>Cancelar</button>}
          <button className="btn-primary">{editing? 'Actualizar' : 'Crear'}</button>
        </div>
      </form>

      <div className="card">
        {loading? <Spinner/> : (
          <table className="min-w-full">
            <thead className="bg-sky-50"><tr>{['Estudio','Filename','URL','Mimetype','Bytes',''].map(h=>(<th key={h} className="px-3 py-2 text-left">{h}</th>))}</tr></thead>
            <tbody>
              {rows.map(r=> (
                <tr key={r.id} className="odd:bg-white even:bg-sky-50/30">
                  <td className="px-3 py-2">{r.estudio_id}</td>
                  <td className="px-3 py-2">{r.filename}</td>
                  <td className="px-3 py-2 truncate max-w-[360px]"><a className="text-sky-700 underline" href={r.url} target="_blank" rel="noreferrer">{r.url}</a></td>
                  <td className="px-3 py-2">{r.mimetype}</td>
                  <td className="px-3 py-2">{r.size_bytes ?? ''}</td>
                  <td className="px-3 py-2 text-right">
                    <button className="btn-ghost mr-2" onClick={()=>startEdit(r)}>Editar</button>
                    <button className="btn-danger" onClick={()=>remove(r.id)}>Borrar</button>
                  </td>
                </tr>
              ))}
              {rows.length===0 && <tr><td colSpan={6} className="text-center p-6 text-sky-900/60">Sin imágenes</td></tr>}
            </tbody>
          </table>
        )}
      </div>
      <Toast message={error} onClose={()=>setError('')} />
    </div>
  )
}
