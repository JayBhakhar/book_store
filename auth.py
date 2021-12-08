import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext


class AuthHandler:
    security = HTTPBearer()
    SECRET_KEY = "ourLittleSecret!"
    ALGORITHM = "HS256"
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, payload):
        return jwt.encode(
            {
                '_id': payload['_id'],
                # 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            self.SECRET_KEY,
            self.ALGORITHM
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token,
                                 self.SECRET_KEY,
                                 self.ALGORITHM)
            return payload
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)
