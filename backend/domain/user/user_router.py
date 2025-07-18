from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.user import user_crud, user_schema
from domain.user.user_crud import pwd_context

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = '06d68d83f6626544880ee044d8acfdf434278c2150024a9cd5e14131a341a274'
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

router = APIRouter(
    prefix="/api/user",
)


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = user_crud.get_existing_user(db,user_create=_user_create)
    if user:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT,
                            detail = "이미 존재하는 사용자입니다.")
    user_crud.create_user(db=db, user_create=_user_create)



@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(form_data:OAuth2PasswordRequestForm = Depends(), #전달해주는 데이터 : form데이터 형식으로 전달.
                           db: Session = Depends(get_db)):
    
    user = user_crud.get_user(db,form_data.username) #여기서 db를 조회.
    if not user or not pwd_context.verify(form_data.password,user.password):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate" : "Bearer"}
        )
    
    data = {
        "sub" : user.username,
        "exp" : datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    access_token = jwt.encode(data,SECRET_KEY,algorithm=ALGORITHM)

    return {
        "access_token" :access_token,
        "token_type" : "bearer",
        "username" : user.username
    }

def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = user_crud.get_user(db, username=username)
        if user is None:
            raise credentials_exception
        return user