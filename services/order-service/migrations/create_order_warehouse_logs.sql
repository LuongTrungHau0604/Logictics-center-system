-- Migration script: Tạo bảng order_warehouse_logs
-- File: migrations/create_order_warehouse_logs.sql

CREATE TABLE IF NOT EXISTS `order_warehouse_logs` (
  `log_id` VARCHAR(50) PRIMARY KEY,
  `order_id` VARCHAR(50) NOT NULL,
  `warehouse_id` VARCHAR(50) NOT NULL,
  `scanned_by` VARCHAR(50) DEFAULT NULL COMMENT 'User ID của nhân viên quét',
  `scanned_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `action` VARCHAR(50) NOT NULL COMMENT 'CHECK_IN, CHECK_OUT, PROCESSING',
  `note` TEXT DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  -- Indexes
  INDEX `idx_order_id` (`order_id`),
  INDEX `idx_warehouse_id` (`warehouse_id`),
  INDEX `idx_scanned_at` (`scanned_at`),
  
  -- Foreign Keys
  CONSTRAINT `fk_log_order` 
    FOREIGN KEY (`order_id`) 
    REFERENCES `orders` (`order_id`) 
    ON DELETE CASCADE,
    
  CONSTRAINT `fk_log_warehouse` 
    FOREIGN KEY (`warehouse_id`) 
    REFERENCES `warehouses` (`warehouse_id`) 
    ON DELETE RESTRICT
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Lưu lịch sử quét barcode và di chuyển của đơn hàng qua các kho';
