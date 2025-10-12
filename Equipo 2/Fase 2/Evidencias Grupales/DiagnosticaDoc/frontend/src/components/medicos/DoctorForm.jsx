import { useState } from 'react'
const empty = { nombre:'', email:'', especialidad:'', registro_colegio:'' }
export default function DoctorForm({ initial=empty, onSubmit }){
  const [form, setForm] = useState({ ...empty, ...initial })
  function handle(e){ const {name,value}=e.target; setForm(s=>({...s,[name]:value})) }
  function submit(e){ e.preventDefault(); onSubmit?.(form) }
  return (<form onSubmit={submit} className='grid grid-cols-4 gap-3'>
    <input name='nombre' placeholder='Nombre' className='input' value={form.nombre} onChange={handle} required />
    <input name='email' placeholder='Email' className='input' value={form.email} onChange={handle} type='email' />
    <input name='especialidad' placeholder='Especialidad' className='input' value={form.especialidad} onChange={handle} />
    <input name='registro_colegio' placeholder='Registro colegio' className='input' value={form.registro_colegio} onChange={handle} />
    <div className='col-span-4 flex justify-end'><button className='btn-primary'>Guardar</button></div></form>) }