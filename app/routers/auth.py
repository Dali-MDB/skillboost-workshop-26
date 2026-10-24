from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.user import UserCreate, UserDisplay, TokenDisplay
from app.services.user import UserService
from app.services.email import EmailService
from app.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserDisplay, status_code=201)
def register(
    data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Sign up for a new account."""
    user = UserService(db).register(data)
    background_tasks.add_task(EmailService.send_welcome_email, user.email, user.username)
    return user


@router.post("/login", response_model=TokenDisplay)
@limiter.limit("20/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Log in using email (passed in the username field) and password to receive a JWT access token."""
    token = UserService(db).login(email=form_data.username, password=form_data.password)
    return TokenDisplay(access_token=token)
