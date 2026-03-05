import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

def send_reset_email(to_email: str, token: str, name: str):
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; background: #09090f; color: #ffffff; border-radius: 12px; overflow: hidden;">
      <div style="background: #a3e635; padding: 24px; text-align: center;">
        <h1 style="color: #09090f; margin: 0; font-size: 1.4rem;">🔑 Reset your password</h1>
      </div>
      <div style="padding: 32px;">
        <p style="color: #a1a1aa;">Hi <strong style="color: #fff">{name}</strong>,</p>
        <p style="color: #a1a1aa;">Click the button below to reset your password.</p>
        <div style="text-align: center; margin: 32px 0;">
          <a href="{reset_link}"
             style="background: #a3e635; color: #09090f; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 1rem;">
            Reset Password →
          </a>
        </div>
        <p style="color: #52525b; font-size: 0.8rem;">This link expires in 1 hour. If you didn't request this, ignore this email.</p>
      </div>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset your DocuGuard password"
    msg["From"] = MAIL_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(MAIL_USER, MAIL_PASSWORD)
            server.sendmail(MAIL_USER, to_email, msg.as_string())
        print(f"✅ Reset email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send reset email: {e}")
        raise

        
def send_verification_email(to_email: str, token: str, name: str):
    verify_link = f"{FRONTEND_URL}/verify-email?token={token}"

    html = f"""
    <div style="font-family: 'DM Sans', Arial, sans-serif; max-width: 480px; margin: 0 auto; background: #09090f; color: #ffffff; border-radius: 12px; overflow: hidden;">
      <div style="background: #a3e635; padding: 24px; text-align: center;">
        <h1 style="color: #09090f; margin: 0; font-size: 1.4rem;">✅ Verify your DocuGuard account</h1>
      </div>
      <div style="padding: 32px;">
        <p style="color: #a1a1aa;">Hi <strong style="color: #fff">{name}</strong>,</p>
        <p style="color: #a1a1aa;">Click the button below to verify your email address and activate your account.</p>
        <div style="text-align: center; margin: 32px 0;">
          <a href="{verify_link}"
             style="background: #a3e635; color: #09090f; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 1rem;">
            Verify Email →
          </a>
        </div>
        <p style="color: #52525b; font-size: 0.8rem;">This link expires in 24 hours. If you didn't create an account, ignore this email.</p>
      </div>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your DocuGuard account"
    msg["From"] = MAIL_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(MAIL_USER, MAIL_PASSWORD)
            server.sendmail(MAIL_USER, to_email, msg.as_string())
        print(f"✅ Verification email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise