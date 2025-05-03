import smtplib
import random
import os



def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(recipient_email):
    """Send an OTP email"""
    otp = generate_otp()
    subject = "Your OTP Code"
    message = f"Subject: {subject}\n\nYour OTP is: {otp}"

    

    try:
        SMTP_SERVER = "smtp.office365.com"  # GoDaddy/Outlook SMTP
        SMTP_PORT = 587
        EMAIL_ADDRESS = "support@skill-study.com"
        EMAIL_PASSWORD = ""  # ⚠️ Use an environment variable for security
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipient_email, message)
        server.quit()
        return otp  # Return OTP to store in session or database
    
    except Exception as e:
        print(f"Email sending failed: {e}")
        return None
    

