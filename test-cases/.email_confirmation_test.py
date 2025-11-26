import smtplib
from email.message import EmailMessage
customer_email = 'yjedfre@gmail.com'
# Log into gmail for this, click security then click app passwords, then generate one
#This will allow smt to sign in and send emails
app_password = 'zcoldyzahdqfojmk'
#


#in check out form make the email they give global, so this can use that variable

def send_confirmation_email():
    msg = EmailMessage()
    msg.set_content("Thanks for backing the ones who never back down. You're part of the Dawg house now - and remember: Hungry Dawgs Run Faster.")
    msg['From'] = "delvawilson116@gmail.com"
    msg['To'] = customer_email
    msg['Subject'] = "Order Confirmation"

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login("delvawilson116@gmail.com", app_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send confirmation email!", e)

send_confirmation_email()