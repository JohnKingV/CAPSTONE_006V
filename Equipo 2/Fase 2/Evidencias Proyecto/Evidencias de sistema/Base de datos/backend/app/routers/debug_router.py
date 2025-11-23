# app/routers/debug_router.py
from fastapi import APIRouter, HTTPException, Query
from app.core.mailer import build_email_confirmacion, send_email

router = APIRouter(prefix="/debug", tags=["debug"])

@router.post("/send-test-email")
def send_test_email(to: str = Query(..., description="Destino")):
    data = {
        "paciente_nombre": "Prueba",
        "fecha": "2025-12-01",
        "hora": "10:00",
        "doctor": "Dr. Prueba",
        "especialidad": "Test",
        "modalidad": "presencial",
        "motivo": "Probar SMTP",
        "nro_reserva": "DX-TEST",
    }
    try:
        msg = build_email_confirmacion(to, data)
        send_email(msg)  # directo: si falla, responde 500 con el error real
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
