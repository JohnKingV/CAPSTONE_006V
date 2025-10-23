import { useEffect, useState } from 'react'
import { pingApi } from '../../api/client'

export default function ApiStatus(){
  const [ok, setOk] = useState(true)
  useEffect(() => { 
    let mounted = true
    const run = async () => {
      const isOk = await pingApi()
      if(mounted) setOk(isOk)
    }
    run()
    const id = setInterval(run, 15000)
    return () => { mounted = false; clearInterval(id) }
  }, [])

  if(ok) return null
  return (
    <div className="bg-red-50 text-red-800 text-sm px-4 py-2 text-center border-y">
      No se puede contactar la API. Verifica <code className="font-mono">VITE_API_URL</code> o el servidor.
    </div>
  )
}