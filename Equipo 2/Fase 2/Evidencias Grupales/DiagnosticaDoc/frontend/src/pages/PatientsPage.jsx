import { useEffect, useState } from 'react'
import Spinner from '../components/ui/Spinner'
import { Toast } from '../components/ui/Toast'
import PatientsTable from '../components/pacientes/PatientsTable'
import PatientForm from '../components/pacientes/PatientForm'
import { listPacientes, createPaciente, updatePaciente, deletePaciente } from '../api/pacientes'
import { parseApiError } from '../api/client'

export default function PatientsPage(){
  const [loading, setLoading] = useState(true)
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [modal, setModal] = useState(false)
  const [editing, setEditing] = useState(null)
  async function load(){ setLoading(true); try{ setRows(await listPacientes()) }catch(e){ setError(parseApiError(e)) } finally { setLoading(false) } }
  useEffect(()=>{ load() },[])
  async function handleSave(payload){
    try{
      if(editing){ const saved = await updatePaciente(editing.id, payload); setRows(rs => rs.map(r => r.id===saved.id ? saved : r)); setError('Paciente actualizado') }
      else { const saved = await createPaciente(payload); setRows(rs => [saved, ...rs]); setError('Paciente creado') }
      setModal(false); setEditing(null)
    }catch(e){ setError(parseApiError(e)) }
  }
  async function handleDelete(row){ if(!confirm(`Eliminar paciente ${row.nombres} ${row.apellidos}?`)) return
    try{ await deletePaciente(row.id); setRows(rs => rs.filter(r => r.id!==row.id)); setError('Paciente eliminado') } catch(e){ setError(parseApiError(e)) } }
  return (<div className='p-6 space-y-4'>
    <header className='flex items-center justify-between'><h1 className='text-2xl font-semibold text-sky-900'>Pacientes</h1>
      <button className='btn-primary' onClick={()=>{ setEditing(null); setModal(true) }}>Nuevo</button></header>
    <div className='card'>{loading ? <Spinner/> : <PatientsTable rows={rows} onEdit={(r)=>{ setEditing(r); setModal(true) }} onDelete={handleDelete}/>}</div>
    {modal && (<div className='fixed inset-0 bg-black/40 flex items-center justify-center p-4' onClick={()=>setModal(false)}>
      <div className='bg-white rounded-2xl shadow-xl p-6 w-full max-w-2xl' onClick={e=>e.stopPropagation()}>
        <h2 className='text-xl font-medium text-sky-900 mb-4'>{editing? 'Editar Paciente' : 'Nuevo Paciente'}</h2>
        <PatientForm initial={editing||undefined} onSubmit={handleSave} onCancel={()=>setModal(false)} /></div></div>)}
    <Toast message={error} onClose={()=>setError('')} /></div>) }