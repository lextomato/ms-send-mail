from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os, smtplib
from email.message import EmailMessage

app = FastAPI()

### ——— variables de entorno ———
TOKEN      = os.getenv("MAIL_TOKEN")      # debe coincidir con VITE_TOKEN_CLOUD_FUNCTION
SMTP_HOST  = os.getenv("SMTP_HOST")       # p.e. mail.mollitiam.cl
SMTP_PORT  = int(os.getenv("SMTP_PORT", 587))
SMTP_USER  = os.getenv("SMTP_USER")       # cuenta remitente
SMTP_PASS  = os.getenv("SMTP_PASS")
MAIL_TO    = os.getenv("MAIL_TO", SMTP_USER)     # destino

class Payload(BaseModel):
    name: str
    email: str
    message: str

@app.post("/send-mail")
async def send_mail(data: Payload, authorization: str = Header("")):
    # 1️⃣ Bearer token
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="invalid token")

    # 2️⃣ Construir el correo
    msg = EmailMessage()
    msg["Subject"] = f"Contacto desde portfolio — {data.name}"
    msg["From"]    = SMTP_USER
    msg["To"]      = MAIL_TO
    msg.set_content(
        f"Nombre  : {data.name}\n"
        f"Email   : {data.email}\n\n"
        f"{data.message}"
    )

    # 3️⃣ Enviar por SMTP (STARTTLS)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)

    return {"result": True}
