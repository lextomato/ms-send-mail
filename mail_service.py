from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, smtplib, ssl, logging
from email.message import EmailMessage
from dotenv import load_dotenv; load_dotenv()

app = FastAPI()

# ── dominios que pueden llamar a la API ──
origins = [
    "https://mollitiam.cl",
    "https://www.mollitiam.cl",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

### ——— variables de entorno ———
TOKEN      = os.getenv("MAIL_TOKEN")      # debe coincidir con VITE_TOKEN_CLOUD_FUNCTION
SMTP_HOST  = os.getenv("SMTP_HOST")       # p.e. mail.mollitiam.cl
SMTP_PORT  = int(os.getenv("SMTP_PORT", 587))
SMTP_USER  = os.getenv("SMTP_USER")       # cuenta remitente
SMTP_PASS  = os.getenv("SMTP_PASS")
MAIL_TO    = os.getenv("MAIL_TO", SMTP_USER)     # destino

if not all([SMTP_USER, SMTP_PASS]):
    raise RuntimeError("SMTP_USER / SMTP_PASS no definidos")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)

class Payload(BaseModel):
    name: str
    email: str
    message: str

@app.post("/send-mail")
async def send_mail(data: Payload, authorization: str = Header("")):
    # ① Verificar token
    if authorization != f"Bearer {TOKEN}":
        logging.warning("Token inválido")
        raise HTTPException(status_code=401, detail="invalid token")

    # ② Construir el mensaje
    msg = EmailMessage()
    msg["Subject"] = f"Contacto desde portfolio — {data.name}"
    msg["From"]    = SMTP_USER
    msg["To"]      = MAIL_TO
    msg.set_content(
        f"Nombre : {data.name}\n"
        f"Email  : {data.email}\n\n"
        f"{data.message}"
    )

    # ③ Enviar
    try:
        if SMTP_PORT == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as smtp:
                smtp.login(SMTP_USER, SMTP_PASS)
                smtp.send_message(msg)
        else:  # 587 (STARTTLS)
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASS)
                smtp.send_message(msg)

        logging.info("Correo enviado a %s", MAIL_TO)
        return {"result": True}

    except smtplib.SMTPAuthenticationError:
        logging.exception("Credenciales SMTP inválidas")
        raise HTTPException(500, "SMTP auth failed")

    except smtplib.SMTPException as e:
        logging.exception("Error SMTP")
        raise HTTPException(500, f"SMTP error: {e}")

@app.get("/__health")
async def health_check():
    """
    Endpoint de salud para verificar que el servicio está activo.
    """
    return {"status": "ok", "message": "Mail service is running."}
