import logging
import firebase_admin
from firebase_admin import credentials, messaging
from app.core.config import settings  # Giả sử bạn lưu đường dẫn file JSON ở đây

logger = logging.getLogger(__name__)

class NotificationService:
    _instance = None

    def __new__(cls):
        """
        Singleton Pattern: Đảm bảo chỉ có 1 instance của NotificationService
        được tạo ra trong suốt vòng đời ứng dụng.
        """
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
            cls._instance._initialize_firebase()
        return cls._instance

    def _initialize_firebase(self):
        """Khởi tạo Firebase App nếu chưa có."""
        try:
            # Kiểm tra xem Firebase đã được init chưa để tránh lỗi
            if not firebase_admin._apps:
                # Đường dẫn đến file json private key tải từ Firebase Console
                # Bạn có thể hardcode đường dẫn tạm thời nếu chưa có settings
                cred_path = getattr(settings, "FIREBASE_CREDENTIALS_PATH", "firebase-adminsdk.json")
                
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("🔥 Firebase Admin Initialized Successfully!")
            else:
                logger.info("🔥 Firebase Admin already initialized.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")

    def send_push_notification(self, fcm_token: str, title: str, body: str, data: dict = None):
        """
        Gửi thông báo Push đến thiết bị Android qua FCM.
        
        Args:
            fcm_token (str): Token của thiết bị Shipper.
            title (str): Tiêu đề thông báo.
            body (str): Nội dung thông báo.
            data (dict): Dữ liệu đi kèm (ví dụ: order_id, action_type). 
                         LƯU Ý: Tất cả value trong dict phải là STRING.
        """
        if not fcm_token:
            logger.warning("⚠️ Cannot send notification: No FCM Token provided.")
            return False

        try:
            # 1. Chuẩn hóa dữ liệu data (Firebase yêu cầu value phải là string)
            clean_data = {}
            if data:
                for k, v in data.items():
                    clean_data[k] = str(v)

            # 2. Cấu hình riêng cho Android (Quan trọng cho App tài xế)
            android_config = messaging.AndroidConfig(
                priority='high',  # Ưu tiên cao (đánh thức máy ngay lập tức)
                ttl=3600,         # Thời gian sống của tin (1 giờ)
                notification=messaging.AndroidNotification(
                    icon='ic_notification',  # Tên icon trong folder android/app/src/main/res/drawable
                    color='#FF5722',         # Màu chủ đạo (ví dụ màu cam)
                    sound='default',         # Âm thanh mặc định
                    click_action='FLUTTER_NOTIFICATION_CLICK', # Hoặc string tùy chỉnh để App bắt sự kiện
                    channel_id='default'     # Phải khớp với channel ID tạo trong React Native
                ),
            )

            # 3. Tạo Message
            message = messaging.Message(
                token=fcm_token,
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=clean_data,
                android=android_config, # Chỉ định config Android
            )

            # 4. Gửi
            response = messaging.send(message)
            logger.info(f"✅ Notification sent successfully to token ending in ...{fcm_token[-6:]}")
            return True

        except firebase_admin.messaging.QuotaExceededError:
            logger.error("❌ Firebase Quota Exceeded.")
            return False
        except firebase_admin.messaging.SenderIdMismatchError:
            logger.error("❌ Sender ID Mismatch (Sai key JSON).")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
            return False

# Tạo một instance dùng chung
notification_service = NotificationService()