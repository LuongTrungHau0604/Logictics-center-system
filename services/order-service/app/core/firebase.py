import firebase_admin
from firebase_admin import credentials, db
import logging
import os

logger = logging.getLogger(__name__)

SERVICE_ACCOUNT_PATH = "app/core/serviceAccountKey.json" 

def init_firebase():
    try:
        if not firebase_admin._apps:
            if os.path.exists(SERVICE_ACCOUNT_PATH):
                cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://cuoiki-34b92-default-rtdb.firebaseio.com/' # <--- Thay đúng URL của bạn
                })
                logger.info("🔥 [FIREBASE] Khởi tạo thành công!")
            else:
                logger.warning(f"⚠️ [FIREBASE] Không tìm thấy file key tại: {os.path.abspath(SERVICE_ACCOUNT_PATH)}")
    except Exception as e:
        logger.error(f"❌ [FIREBASE] Lỗi Init: {e}")

def push_notification_to_firebase(user_id: str, title: str, message: str, type: str = "INFO"):
    # --- LOG DEBUG QUAN TRỌNG ---
    logger.info(f"🔥 [FIREBASE DEBUG] Đang gọi hàm gửi tin cho: {user_id}") 
    
    try:
        if not firebase_admin._apps:
            logger.error("❌ [FIREBASE DEBUG] Firebase APP chưa được Init! (Kiểm tra lại serviceAccountKey.json)")
            return
            
        ref = db.reference(f'notifications/{user_id}')
        
        ref.push({
            'title': title,
            'message': message,
            'type': type,
            'timestamp': {'.sv': 'timestamp'}
        })
        logger.info(f"✅ [FIREBASE DEBUG] Đã đẩy tin lên server thành công: {title}")
        
    except Exception as e:
        logger.error(f"❌ [FIREBASE DEBUG] Lỗi khi đẩy tin: {e}")