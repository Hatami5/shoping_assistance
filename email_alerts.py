# AI-Shopping-Assistant/app/services/email_alerts.py

import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any
from ..utils.logger import setup_logging

logger = setup_logging(__name__)

# --- Configuration (Normally loaded from environment variables) ---
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = "alerts@ai-shopping-assistant.com"
SMTP_PASSWORD = "YOUR_SMTP_PASSWORD"
SENDER_EMAIL = "no-reply@ai-shopping-assistant.com"

class EmailService:
    """
    Handles sending emails for price drop alerts and other notifications.
    Uses a simulated SMTP connection for this example.
    """
    
    def __init__(self):
        # We don't initialize the connection here, but on demand for robustness
        pass
        
    def create_alert_body(self, alert_data: Dict[str, Any]) -> str:
        """Generates the HTML/Plain text body for the price drop alert."""
        
        product_name = alert_data.get('product_name', 'Unknown Product')
        target_price = alert_data.get('target_price', 0.0)
        current_price = alert_data.get('current_price', 0.0)
        product_url = alert_data.get('product_url', '#')
        
        body = f"""
        <html>
            <body>
                <h2>🚨 Price Drop Alert! 🚨</h2>
                <p>Great news! The price for <strong>{product_name}</strong> has dropped!</p>
                <p>
                    <ul>
                        <li>Your Target Price: <b>${target_price:.2f}</b></li>
                        <li>Current Price: <b style="color: green;">${current_price:.2f}</b></li>
                        <li>You save: <b>${target_price - current_price:.2f}</b>!</li>
                    </ul>
                </p>
                <p>
                    <a href="{product_url}" style="padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">
                        View Deal Now
                    </a>
                </p>
                <p><i>This alert was triggered because the price is now below your set target.</i></p>
            </body>
        </html>
        """
        return body

    def send_price_alert(self, recipient_email: str, alert_data: Dict[str, Any]) -> bool:
        """Sends the price drop email."""
        
        subject = f"Price Alert: {alert_data.get('product_name', 'Product')} dropped to ${alert_data.get('current_price', 0.0):.2f}!"
        body = self.create_alert_body(alert_data)
        
        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email

        try:
            # --- SIMULATED EMAIL SENDING ---
            logger.info(f"SIMULATING: Sending price alert for {alert_data['product_name']} to {recipient_email}")
            # In a real setup, uncomment the following block:
            # with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            #     server.starttls()  # Secure the connection
            #     server.login(SMTP_USER, SMTP_PASSWORD)
            #     server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            # logger.info(f"SUCCESS: Price alert email sent to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"FAILURE: Could not send email to {recipient_email}. Error: {e}")
            return False

email_service = EmailService()