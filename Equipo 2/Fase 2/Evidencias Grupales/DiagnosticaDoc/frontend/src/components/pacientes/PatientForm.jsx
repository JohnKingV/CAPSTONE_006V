import { useState } from 'react'
const empty = { nombres:'', apellidos:'', documento:'', telefono:'', email:'', fecha_nacimiento:'' }
export default function PatientForm({ initial=empty, onSubmit, onCancel }){
  const [form, setForm] = useState({ ...empty, ...initial })
  function handle(e){ const {name,value}=e.target; setForm(s=>({...s,[name]:value})) }
  function submit(e){ e.preventDefault(); onSubmit?.(form) }
  return (<form onSubmit={submit} className='space-y-3'>
    <div className='grid grid-cols-2 gap-3'>
      <input name='nombres' placeholder='Nombres' className='input' value={form.nombres} onChange={handle} required />
      <input name='apellidos' placeholder='Apellidos' className='input' value={form.apellidos} onChange={handle} required />
      <input name='documento' placeholder='Documento (opcional)' className='input' value={form.documento} onChange={handle} />
      <input name='telefono' placeholder='Teléfono (opcional)' className='input' value={form.telefono} onChange={handle} />
      <input name='email' placeholder='Email (opcional)' className='input' value={form.email} onChange={handle} type='email' />
      <input name='fecha_nacimiento' placeholder='Fecha nacimiento' className='input' type='date' value={form.fecha_nacimiento} onChange={handle} />
    </div>
    <div className='flex gap-2 justify-end pt-2'>
      <button type='button' onClick={onCancel} className='btn-secondary'>Cancelar</button>
      <button className='btn-primary'>Guardar</button>
    </div>
  </form>) }