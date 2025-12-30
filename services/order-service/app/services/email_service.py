# app/services/email_service.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.core.config import settings

# Cấu hình SMTP (Nên lấy từ file .env)
# Nếu dùng Gmail: smtp.gmail.com, port 587
SMTP_SERVER = getattr(settings, "SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = getattr(settings, "SMTP_PORT", 587)
SENDER_EMAIL = getattr(settings, "SENDER_EMAIL", "email_cua_ban@gmail.com")
SENDER_PASSWORD = getattr(settings, "SENDER_PASSWORD", "mat_khau_ung_dung_16_ky_tu")

logger = logging.getLogger(__name__)

def send_sme_notification_email(sme_email: str, sme_name: str, order_code: str):
    """
    Gửi email thông báo cho SME (Sử dụng Mailtrap để Test).
    Lưu ý: Mail sẽ KHÔNG gửi tới hộp thư thật của SME, mà sẽ chui vào Inbox trên Mailtrap.io.
    """
    try:
        subject = f"✅ [TEST] Đơn hàng {order_code} đã giao thành công"
        
        # Nội dung Email HTML (Giữ nguyên như cũ hoặc tùy chỉnh)
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                <h2 style="color: #E11D48; text-align: center;">[MAILTRAP TEST] Thông Báo Hoàn Tất</h2>
                <p>Kính gửi đối tác <strong>{sme_name}</strong>,</p>
                
                <p>Đây là email kiểm thử từ hệ thống AI Transport.</p>
                <p>Đơn hàng <b>{order_code}</b> đã được Shipper giao thành công.</p>
                
                <hr>
                <p style="font-size: 12px; color: gray;">Sent via Mailtrap</p>
            </div>
          </body>
        </html>
        """

        # Cấu hình Message
        msg = MIMEMultipart()
        msg['From'] = "AI Transport System <system@aitransport.test>" # Mail gửi ảo
        msg['To'] = sme_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        # Kết nối và gửi
        print(f"DEBUG: Connecting to Mailtrap: {SMTP_SERVER}:{SMTP_PORT}")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() # Mailtrap cũng hỗ trợ TLS
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(msg['From'], sme_email, msg.as_string())
        server.quit()

        logger.info(f"📧 Mailtrap sent successfully to Virtual Inbox for: {sme_email}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email via Mailtrap: {e}")
        return False