from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

# Email Configuration - UPDATE THESE
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hgoyal_be23@thapar.edu'  # Change this
app.config['MAIL_PASSWORD'] = 'pxfb dwyn zagt hjxx'      # Change this
app.config['MAIL_DEFAULT_SENDER'] = 'hgoyal_be23@thapar.edu'

mail = Mail(app)

def send_test_email():
    with app.app_context():
        try:
            msg = Message(
                subject='Test Email from Mashup App',
                recipients=['your-email@gmail.com']  # Send to yourself
            )
            msg.body = 'If you receive this, email configuration is working!'
            
            print("Attempting to send email...")
            mail.send(msg)
            print("✓ Email sent successfully!")
            
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            print(f"Error type: {type(e).__name__}")

if __name__ == '__main__':
    send_test_email()