import os
import smtplib
from email.message import EmailMessage

SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = os.environ.get('SMTP_PORT', 587)
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
DEFAULT_SENDER = os.environ.get('DEFAULT_SENDER', 'noreply@mealconnect.com')

def send_email(to_email, subject, body):
    if not SMTP_SERVER or not SMTP_USER or not SMTP_PASSWORD:
        print(f"\n{'='*50}\n[MOCK EMAIL SENT]")
        print(f"To: {to_email}\nSubject: {subject}\n\n{body}\n{'='*50}\n")
        return True
        
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = DEFAULT_SENDER
        msg['To'] = to_email

        with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

def create_notification(conn, user_type, user_id, message, email=None, email_subject=None):
    # Insert DB notification
    cur = conn.cursor()
    cur.execute("INSERT INTO notifications (user_type, user_id, message) VALUES (?, ?, ?)", (user_type, user_id, message))
    conn.commit()
    
    # Send email if provided
    if email and email_subject:
        send_email(email, email_subject, message)
