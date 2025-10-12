import { useState } from 'react'
const empty = { paciente_id:'', titulo:'', descripcion:'', fecha_estudio:'', medico_id:'' }
export default function StudyForm({ initial=empty, onSubmit }){
  const [form, setForm] = useState({ ...empty, ...initial })
  function handle(e){ const {name,value}=e.target; setForm(s=>({...s,[name]:value})) }
  function submit(e){ e.preventDefault(); onSubmit?.(form) }
  return (<form onSubmit={submit} className='grid grid-cols-6 gap-3'>
    <input name='paciente_id' placeholder='Paciente ID' className='input' value={form.paciente_id} onChange={handle} required />
    <input name='titulo' placeholder='Título' className='input col-span-2' value={form.titulo} onChange={handle} required />
    <input name='fecha_estudio' type='date' className='input' value={form.fecha_estudio} onChange={handle} />
    <input name='medico_id' placeholder='Médico ID (opcional)' className='input' value={form.medico_id} onChange={handle} />
    <input name='descripcion' placeholder='Descripción' className='input col-span-6' value={form.descripcion} onChange={handle} />
    <div className='col-span-6 flex justify-end'><button className='btn-primary'>Guardar</button></div></form>) }