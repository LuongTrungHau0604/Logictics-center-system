# services/order-service/app/core/logging_config.py

import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Setup detailed logging configuration
    """
    # Root logger configuration
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG for detailed logs
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            RotatingFileHandler(
                'order_service.log', 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=3
            )
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('app.api.v1.deps').setLevel(logging.DEBUG)
    logging.getLogger('app.services.auth_client').setLevel(logging.DEBUG)
    logging.getLogger('httpx').setLevel(logging.INFO)  # HTTPX logs
    
    # Suppress some noisy logs
    logging.getLogger('aiomysql').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("🔧 Logging configuration completed")