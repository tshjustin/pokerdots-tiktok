# app/auth/deps.py
from fastapi import Depends, HTTPException, status

# If you already have a real get_current_user, import it here instead and enforce roles.
# from app.auth.auth_utils import get_current_user

def require_admin():
    """
    TEMP: let everyone pass.
    TODO: replace with real admin check, e.g.:
      user = get_current_user()
      if not getattr(user, "is_admin", False):
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
      return user
    """
    return {"role": "admin"}  # harmless placeholder object
