import random
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()  

def send_otp_email(to_email, subject, message, from_email, password):
    """
    Sends an email with the given subject and message to the specified email address.

    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        message (str): The body of the email.
        from_email (str): The sender's email address.
        password (str): The sender's email password.
    """
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        msg.set_content(message)

        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        if 'server' in locals():  # Check if server was defined
            server.quit()

if __name__ == "__main__":
    # Generate OTP
    otp = "".join(str(random.randint(0, 9)) for _ in range(6))
    print(f"Generated OTP: {otp}")

    # Email details (retrieve from environment variables)
    from_email = os.environ.get('EMAIL_ADDRESS')
    password = os.environ.get('EMAIL_PASSWORD')

    if not from_email or not password:
        print("Error: EMAIL_ADDRESS and EMAIL_PASSWORD environment variables not set.")
        exit()

    to_email = input("Enter recipient email address: ")
    subject = 'OTP Verification'
    message = f'Your OTP is: {otp}'

    # Send the email
    send_otp_email(to_email, subject, message, from_email, password)