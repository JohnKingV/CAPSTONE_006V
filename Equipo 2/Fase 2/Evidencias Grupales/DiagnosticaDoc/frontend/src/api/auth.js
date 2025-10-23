// src/api/auth.js
import { apiPost, apiGet } from './client'

// POST /auth/login
export async function login({ email, password }) {
  return apiPost('/auth/login', { email, password })
}

// POST /auth/register  (si lo usas)
export async function register(payload) {
  return apiPost('/auth/register', payload)
}

// GET /auth/me
export async function me() {
  return apiGet('/auth/me')
}
