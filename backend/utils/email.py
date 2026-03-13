import os
import requests
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
MAIL_FROM_EMAIL = os.getenv("MAIL_FROM_EMAIL", "noamkadosh4444@gmail.com")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "DocuGuard")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def _send(to_email: str, subject: str, html: str) -> bool:
    payload = {
        "sender": {"name": MAIL_FROM_NAME, "email": MAIL_FROM_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html,
    }
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    try:
        res = requests.post(BREVO_URL, json=payload, headers=headers, timeout=10)
        res.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


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

    ok = _send(to_email, "Reset your DocuGuard password", html)
    if ok:
        print(f"✅ Reset email sent to {to_email}")
    return ok


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

    ok = _send(to_email, "Verify your DocuGuard account", html)
    if ok:
        print(f"✅ Verification email sent to {to_email}")
    return ok
