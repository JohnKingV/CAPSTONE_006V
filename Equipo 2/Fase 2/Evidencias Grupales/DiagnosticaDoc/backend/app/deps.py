# app/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.core.security import SECRET_KEY, ALGORITHM  # asegura que existen

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("uid")
        email = payload.get("sub")
        if uid is None or email is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user = db.query(User).filter(User.id == uid, User.email == email).first()
    if not user or not user.is_active:
        raise cred_exc
    return user


def require_roles(*allowed_roles):
    """
    Úsalo como dependencia para proteger por rol:
      @router.get("/...", dependencies=[Depends(require_roles("admin","medico"))])
    o en firma de endpoint:
      def endpoint(user: User = Depends(require_roles("admin"))): ...
    """
    def _dep(user: User = Depends(get_current_user)) -> User:
        if allowed_roles and user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="No tienes permisos")
        return user
    return _dep
