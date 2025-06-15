from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
import boto3
from helper.auth_helper import get_secret_hash
from db.db import get_db
from db.middleware.auth_middleware import get_current_user
from db.models.user import User
from models.auth_models import (
    ConfirmSignupRequest,
    LoginRequest,
    SignupRequest,
)
from secret_keys import SecretKeys
from sqlalchemy.orm import Session

router = APIRouter()
secret_keys = SecretKeys()

CLIENT_ID = secret_keys.COGNITO_CLIENT_ID
CLIENT_SECRET = secret_keys.COGNITO_CLIENT_SECRET

cognito_client = boto3.client(
    "cognito-idp",
    region_name=secret_keys.REGION_NAME,
)


@router.post("/register")
async def register(
    data: SignupRequest,
    db: Session = Depends(get_db),
):
    try:
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

        secret_hash = get_secret_hash(
            data.email,
            CLIENT_ID,
            CLIENT_SECRET,
        )

        cognito_res = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=data.email,
            Password=data.password,
            SecretHash=secret_hash,
            UserAttributes=[
                {"Name": "email", "Value": data.email},
                {"Name": "name", "Value": data.name},
            ],
        )

        cognito_sub = cognito_res.get("UserSub")

        if not cognito_sub:
            raise HTTPException(400, "Cognito did not return a valid user sub")

        new_user = User(
            name=data.name,
            email=data.email,
            cognito_sub=cognito_sub,
            email_verified=False,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "Signup successful. Please verify your email."}

    except cognito_client.exceptions.UsernameExistsException:
        raise HTTPException(
            status_code=409,
            detail="Username already exists. Please choose a different email.",
        )
    except cognito_client.exceptions.InvalidPasswordException:
        raise HTTPException(
            status_code=400,
            detail="Invalid password. Please ensure it meets the requirements.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup exception: {e}")


@router.post("/confirm-signup")
def confirm_signup(data: ConfirmSignupRequest, db: Session = Depends(get_db)):
    try:
        secret_hash = get_secret_hash(
            data.email,
            CLIENT_ID,
            CLIENT_SECRET,
        )

        cognito_res = cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=data.email,
            ConfirmationCode=data.otp,
            SecretHash=secret_hash,
        )

        # Update user verification status
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.email_verified = True
        db.commit()

        return {"message": "User confirmed successfully!"}
    except cognito_client.exceptions.CodeMismatchException:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Signup confirmation exception: {e}"
        )


@router.post("/login")
async def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    try:
        # Check if user exists and is verified
        user = db.query(User).filter(User.email == data.email).first()
        if user and not user.email_verified:
            raise HTTPException(
                status_code=403,
                detail="Email not verified. Please verify your email first",
            )

        secret_hash = get_secret_hash(
            data.email,
            CLIENT_ID,
            CLIENT_SECRET,
        )

        cognito_res = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": data.email,
                "PASSWORD": data.password,
                "SECRET_HASH": secret_hash,
            },
        )

        auth_result = cognito_res.get("AuthenticationResult")

        if not auth_result:
            raise HTTPException(400, "Incorrect cognito response")

        access_token = auth_result.get("AccessToken")
        refresh_token = auth_result.get("RefreshToken")

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
        )

        return {"message": "User logged in successfully!"}
    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(
            status_code=404, detail="User not found. Please register first."
        )
    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    except cognito_client.exceptions.UserNotConfirmedException:
        raise HTTPException(
            status_code=403, detail="User not confirmed. Please confirm your signup."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login exception: {e}")


@router.post("/refresh")
def refresh_token(
    refresh_token: str = Cookie(None),
    user_cognito_sub: str = Cookie(None),
    response: Response = None,
):
    try:
        if not refresh_token or not user_cognito_sub:
            raise HTTPException(400, "cookies cannot be null!")
        secret_hash = get_secret_hash(
            user_cognito_sub,
            CLIENT_ID,
            CLIENT_SECRET,
        )

        cognito_response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": refresh_token,
                "SECRET_HASH": secret_hash,
            },
        )
        auth_result = cognito_response.get("AuthenticationResult")

        if not auth_result:
            raise HTTPException(400, "Incorrect cognito response")

        access_token = auth_result.get("AccessToken")

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
        )

        return {"message": "Access token refreshed!"}
    except Exception as e:
        raise HTTPException(400, f"Token refresh exception: {e}")


@router.get("/me")
def protected_route(user=Depends(get_current_user)):
    return {"message": "You are authenticated!", "user": user}
