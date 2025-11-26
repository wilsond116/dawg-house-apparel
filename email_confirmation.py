import smtplib
import os
import dotenv
from email.message import EmailMessage
store_email = "dawghouseapparel.co@gmail.com"
# Log into gmail for this, click security then click app passwords, then generate one
#This will allow smt to sign in and send emails
app_password = os.environ.get("EMAIL_APP_PASSWORD")

#in check out form make the email they give global, so this can use that variable

def send_confirmation_email(customer_email, line_items, shipping):
    first_name = shipping.get("first_name", "Customer").title()

    # Generate item list HTML
    items_html = ""
    for item in line_items["data"]:
        items_html += f"""
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{item['description']}</td>
                <td style="text-align: center; border-bottom: 1px solid #eee;">x{item['quantity']}</td>
            </tr>
        """

    # Replace this path with your hosted logo URL
    logo_url = "https://dawg.s3.us-east-1.amazonaws.com/dawg_house_logo.png"

    html_body = f"""
    <html>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f5f5f5; color: #333; margin: 0; padding: 20px;">
        <div style="max-width: 650px; background: #ffffff; margin: auto; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">

            <!-- Header with Logo -->
            <div style="background-color: #000; text-align: center; padding: 25px;">
                <img src="{logo_url}" alt="Dawg House Apparel" style="width: 180px; border-radius: 8px;">
            </div>

            <!-- Email Content -->
            <div style="padding: 30px;">
                <h2 style="color: #111;">Order Confirmation 🧾</h2>
                <p>Hi <strong>{first_name}</strong>,</p>
                <p>Thank you for your purchase from <strong>Dawg House Apparel</strong>! Below are your order details:</p>

                <table width="100%" style="border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr style="background-color: #f0f0f0;">
                            <th align="left" style="padding: 10px;">Item</th>
                            <th align="center" style="padding: 10px;">Qty</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>

                <h3 style="margin-top: 30px; color: #111;">📦 Shipping Address</h3>
                <p style="line-height: 1.6;">
                    {shipping.get('address', 'N/A')}<br>
                    {shipping.get('city', '')}, {shipping.get('state', '')} {shipping.get('zip', '')}
                </p>

                <p style="margin-top: 25px;">We’ll send another email when your order ships.</p>
                <p style="margin-bottom: 40px;">Thank you for shopping with <strong>Dawg House Apparel</strong> 🐾</p>

                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://dawghouseapparel.co" style="background-color: #A30000; color: #fff; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                        Visit Our Store
                    </a>
                </div>
            </div>

            <!-- Footer -->
            <div style="background-color: #111; color: #ccc; text-align: center; padding: 20px;">
                <p style="margin: 0; font-size: 13px;">© 2025 Dawg House Apparel • All Rights Reserved</p>
                <p style="margin: 5px 0 0 0;"><em>Stay Fresh. Stay Dawg. 🐾</em></p>
            </div>
        </div>
    </body>
    </html>
    """

    # Build the email
    msg = EmailMessage()
    msg["From"] = store_email
    msg["To"] = customer_email
    msg["Subject"] = "🐾 Your Dawg House Apparel Order Confirmation"
    msg.set_content("Please view this email in HTML format.")
    msg.add_alternative(html_body, subtype="html")

    # Send via Gmail SMTP
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(store_email, app_password)
            server.send_message(msg)
        print(f"✅ Sent confirmation email to {customer_email}")
    except Exception as e:
        print(f"🚨 Failed to send confirmation email: {e}")
