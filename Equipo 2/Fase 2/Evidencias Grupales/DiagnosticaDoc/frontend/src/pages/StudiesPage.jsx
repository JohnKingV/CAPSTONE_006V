import { useEffect, useState } from 'react'
import Spinner from '../components/ui/Spinner'
import { Toast } from '../components/ui/Toast'
import StudyForm from '../components/estudios/StudyForm'
import { listEstudios, createEstudio, updateEstudio, deleteEstudio } from '../api/estudios'
import { parseApiError } from '../api/client'
export default function StudiesPage(){
  const [loading, setLoading] = useState(true)
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)
  async function load(){ setLoading(true); try{ setRows(await listEstudios()) } catch(e){ setError(parseApiError(e)) } finally { setLoading(false) } }
  useEffect(()=>{ load() },[])
  async function save(form){ try{
    if(editing){ const saved = await updateEstudio(editing.id, form); setRows(rs=>rs.map(r=>r.id===saved.id?saved:r)); setEditing(null) }
    else { const saved = await createEstudio(form); setRows(rs=>[saved, ...rs]) }
    setError('Guardado')
  }catch(e){ setError(parseApiError(e)) } }
  async function remove(id){ if(!confirm('¿Eliminar estudio?')) return; try{ await deleteEstudio(id); setRows(rs=>rs.filter(r=>r.id!==id)); setError('Eliminado') }catch(e){ setError(parseApiError(e)) } }
  return (<div className='p-6 space-y-4'>
    <h1 className='text-2xl font-semibold text-sky-900'>Estudios</h1>
    <div className='card'><StudyForm initial={editing||undefined} onSubmit={save}/></div>
    <div className='card'>{loading? <Spinner/> : (<table className='min-w-full'>
      <thead className='bg-sky-50'><tr>{['Paciente','Título','Fecha','Médico',''].map(h=>(<th key={h} className='px-3 py-2 text-left'>{h}</th>))}</tr></thead>
      <tbody>{rows.map(r=>(<tr key={r.id} className='odd:bg-white even:bg-sky-50/30'>
        <td className='px-3 py-2'>{r.paciente_id}</td>
        <td className='px-3 py-2'>{r.titulo}</td>
        <td className='px-3 py-2'>{r.fecha_estudio}</td>
        <td className='px-3 py-2'>{r.medico_id ?? ''}</td>
        <td className='px-3 py-2 text-right'><button className='btn-ghost mr-2' onClick={()=>setEditing(r)}>Editar</button><button className='btn-danger' onClick={()=>remove(r.id)}>Borrar</button></td>
      </tr>))}{rows.length===0 && <tr><td colSpan={5} className='text-center p-6 text-sky-900/60'>Sin estudios</td></tr>}</tbody>
    </table>)}</div>
    <Toast message={error} onClose={()=>setError('')} /></div>) }