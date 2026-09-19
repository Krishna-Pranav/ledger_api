from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from security import decode_token
from exceptions import UnauthorizedError
import models

bearer_scheme = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_token(creds.credentials)
    if payload.get('type') != 'access':
        raise UnauthorizedError('Token is not access type.')
    user = db.get(models.User, int(payload['sub']))
    if not user:
        raise UnauthorizedError('User no longer exists.')
    return user