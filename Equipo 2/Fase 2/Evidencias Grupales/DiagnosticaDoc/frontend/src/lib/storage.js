// frontend/src/lib/storage.js
const KEY = 'dd.api.endpoint'

export function getEndpoint(){
  try{
    const v = localStorage.getItem(KEY)
    return v && v.trim() ? v.trim() : null
  }catch{ return null }
}

export function setEndpoint(url){
  try{
    if (!url) return clearEndpoint()
    const clean = String(url).replace(/\s+/g,'').replace(/\/+$/,'')
    localStorage.setItem(KEY, clean)
    return clean
  }catch{ return null }
}

export function clearEndpoint(){
  try{ localStorage.removeItem(KEY) }catch{}
}

export function normalizeBase(url){
  if (!url) return ''
  return String(url).replace(/\s+/g,'').replace(/\/+$/,'')
}

export const STORAGE_KEY = KEY
