from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
import random, string

from app.database import get_db
from app.models import Cita
from app.schemas import CitaCreate, CitaRead
from app.core.mailer import build_email_confirmacion, send_email


router = APIRouter(prefix="/citas", tags=["citas"])

def _nro_reserva():
    return "DX-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

@router.post("", response_model=CitaRead)
def crear_cita(
    payload: CitaCreate,
    tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    choque = (
        db.query(Cita)
        .filter(
            Cita.fecha == payload.fecha,
            Cita.hora == payload.hora,
            Cita.doctor == payload.doctor,
        )
        .first()
    )
    if choque:
        raise HTTPException(409, detail="Horario ya reservado para ese doctor")

    cita = Cita(
        paciente_nombre=payload.paciente_nombre,
        paciente_dni=payload.paciente_dni,
        paciente_email=str(payload.paciente_email),
        paciente_telefono=payload.paciente_telefono,
        especialidad=payload.especialidad,
        doctor=payload.doctor,
        modalidad=payload.modalidad,
        motivo=payload.motivo,
        fecha=payload.fecha,
        hora=payload.hora,
        nro_reserva=_nro_reserva(),
    )
    db.add(cita)
    db.commit()
    db.refresh(cita)

    data = {
        "paciente_nombre": cita.paciente_nombre,
        "fecha": cita.fecha.isoformat(),
        "hora": cita.hora,
        "doctor": cita.doctor,
        "especialidad": cita.especialidad,
        "modalidad": cita.modalidad,
        "motivo": cita.motivo or "",
        "nro_reserva": cita.nro_reserva,
    }
    msg = build_email_confirmacion(cita.paciente_email, data)
    tasks.add_task(send_email, msg)

    return cita
