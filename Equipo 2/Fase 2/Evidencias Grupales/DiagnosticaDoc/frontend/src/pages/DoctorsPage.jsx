import { useEffect, useState } from 'react'
import Spinner from '../components/ui/Spinner'
import { Toast } from '../components/ui/Toast'
import DoctorForm from '../components/medicos/DoctorForm'
import { listMedicos, createMedico, updateMedico, deleteMedico } from '../api/medicos'
import { parseApiError } from '../api/client'

export default function DoctorsPage(){
  const [loading, setLoading] = useState(true)
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)
  async function load(){ setLoading(true); try{ setRows(await listMedicos()) } catch(e){ setError(parseApiError(e)) } finally { setLoading(false) } }
  useEffect(()=>{ load() },[])
  async function save(form){ try{
    if(editing){ const saved = await updateMedico(editing.id, form); setRows(rs=>rs.map(r=>r.id===saved.id?saved:r)); setEditing(null) }
    else { const saved = await createMedico(form); setRows(rs=>[saved, ...rs]) }
    setError('Guardado')
  }catch(e){ setError(parseApiError(e)) } }
  async function remove(id){ if(!confirm('¿Eliminar médico?')) return; try{ await deleteMedico(id); setRows(rs=>rs.filter(r=>r.id!==id)); setError('Eliminado') }catch(e){ setError(parseApiError(e)) } }
  return (<div className='p-6 space-y-4'>
    <h1 className='text-2xl font-semibold text-sky-900'>Médicos</h1>
    <div className='card'><DoctorForm initial={editing||undefined} onSubmit={save}/></div>
    <div className='card'>{loading? <Spinner/> : (<table className='min-w-full'>
      <thead className='bg-sky-50'><tr>{['Nombre','Email','Especialidad','Registro',''].map(h=>(<th key={h} className='px-3 py-2 text-left'>{h}</th>))}</tr></thead>
      <tbody>{rows.map(r=>(<tr key={r.id} className='odd:bg-white even:bg-sky-50/30'>
        <td className='px-3 py-2'>{r.nombre}</td>
        <td className='px-3 py-2'>{r.email}</td>
        <td className='px-3 py-2'>{r.especialidad}</td>
        <td className='px-3 py-2'>{r.registro_colegio}</td>
        <td className='px-3 py-2 text-right'><button className='btn-ghost mr-2' onClick={()=>setEditing(r)}>Editar</button><button className='btn-danger' onClick={()=>remove(r.id)}>Borrar</button></td>
      </tr>))}{rows.length===0 && <tr><td colSpan={5} className='text-center p-6 text-sky-900/60'>Sin médicos</td></tr>}</tbody>
    </table>)}</div>
    <Toast message={error} onClose={()=>setError('')} /></div>) }