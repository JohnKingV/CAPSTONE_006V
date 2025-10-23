export default function PatientsTable({ rows=[], onEdit, onDelete }){
  return (<div className='overflow-x-auto'><table className='table'>
    <thead className='bg-sky-50'><tr className='text-left text-sky-900'>{['Nombre','Documento','Teléfono','Email','Nacimiento',''].map(h=>(<th key={h} className='px-3 py-2 border-b'>{h}</th>))}</tr></thead>
    <tbody>{rows.map(r=>(<tr key={r.id} className='odd:bg-white even:bg-sky-50/30 hover:bg-sky-50'>
      <td className='px-3 py-2 border-b'>{r.nombres} {r.apellidos}</td>
      <td className='px-3 py-2 border-b'>{r.documento}</td>
      <td className='px-3 py-2 border-b'>{r.telefono}</td>
      <td className='px-3 py-2 border-b'>{r.email}</td>
      <td className='px-3 py-2 border-b'>{r.fecha_nacimiento}</td>
      <td className='px-3 py-2 border-b text-right'>
        <button onClick={()=>onEdit(r)} className='btn-ghost mr-2'>Editar</button>
        <button onClick={()=>onDelete(r)} className='btn-danger'>Borrar</button></td>
    </tr>))}
    {rows.length===0 && (<tr><td colSpan={6} className='text-center p-6 text-sky-900/60'>Sin pacientes</td></tr>)}
    </tbody></table></div>) }