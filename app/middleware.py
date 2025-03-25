from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.users.routes import redis_client

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_token = request.cookies.get('session_token')
        if session_token:
            user_id = await redis_client.get(f'session:{session_token}')
            if user_id:
                request.state.user_id = user_id.decode()
            else:
                raise HTTPException(status_code=401, detail='Invalid session')
            
        return await call_next(request)