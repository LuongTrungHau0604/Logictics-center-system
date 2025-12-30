-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
-- Host: localhost    Database: cuoiki_soa
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `areas`
--

DROP TABLE IF EXISTS `areas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `areas` (
  `area_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã khu vực',
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Tên khu vực',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT 'Mô tả chi tiết',
  `type` enum('CITY','DISTRICT','REGION','CUSTOM') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'CUSTOM',
  `status` enum('ACTIVE','INACTIVE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ACTIVE',
  `radius_km` decimal(6,2) DEFAULT NULL COMMENT 'Bán kính',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `center_latitude` decimal(10,8) DEFAULT NULL,
  `center_longitude` decimal(11,8) DEFAULT NULL,
  PRIMARY KEY (`area_id`),
  KEY `idx_area_type` (`type`),
  KEY `idx_area_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `areas` VALUES ('AREA-153C32C6','Khu Vực Quận 7','','CITY','ACTIVE',5.00,'2025-12-03 06:28:23','2025-12-05 06:59:20',10.74091093,106.70194976),('AREA-576B8E13','Khu vực TP. Thủ Đức','','CITY','ACTIVE',20.00,'2025-11-28 05:25:44','2025-11-28 05:25:44',10.85105000,106.76020000),('AREA-72077160','Khu vực quận 1',NULL,'CITY','ACTIVE',10.00,'2025-12-12 05:13:24','2025-12-12 05:13:24',10.77976153,106.69907017),('area-hcm-01','Khu vực TP.HCM','Khu vực nội thành Hồ Chí Minh','CITY','ACTIVE',30.00,'2025-11-21 03:09:30','2025-11-21 03:09:30',10.77690000,106.70090000);

--
-- Table structure for table `barcode`
--

DROP TABLE IF EXISTS `barcode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `barcode` (
  `barcode_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code_value` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `generated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`barcode_id`),
  UNIQUE KEY `code_value` (`code_value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `barcode` VALUES ('BC-071E536810E5','ORD62ABFF46964007','2025-11-24 06:00:08'),('BC-1B59D8F9DF7E','ORDF7302C2A434884','2025-12-22 20:21:24'),('BC-3DF3299DE92A','ORD9DD8ECEC435176','2025-12-22 20:26:17'),('BC-3E4CC3F23FAA','ORD55A082F9657800','2025-12-02 06:43:21'),('BC-41C8BBAB249E','ORD5BA3815D307817','2025-11-28 05:30:17'),('BC-46B9A943F329','ORDDB80AEB1435871','2025-12-22 20:37:52'),('BC-4C932262901F','ORD664D8AB6657212','2025-12-02 06:33:33'),('BC-4D1B56B40D69','ORDCF760D46435059','2025-12-22 20:24:19'),('BC-5943122F3B0A','ORDFC6931A2433800','2025-12-22 20:03:21'),('BC-5F822371E5A4','ORD471AE9A7307854','2025-11-28 05:30:55'),('BC-644C733222FE','ORD24A98C10657183','2025-12-02 06:33:04'),('BC-6754BC677990','ORD622204C8917745','2025-12-05 06:55:46'),('BC-937FCD9903B4','ORD9A77EDB3088055','2025-12-07 06:14:15'),('BC-93F46CE6EF5F','ORDB6876844375068','2025-11-29 00:11:08'),('BC-98A14A3051F9','ORDC80C535B434390','2025-12-22 20:13:11'),('BC-9989365A7367','ORD3596445E655804','2025-12-02 06:10:04'),('BC-9F520CA8D15B','ORDE0A9F4AD653964','2025-12-02 05:39:25'),('BC-A4BB98257E7A','ORDE8E3C911375585','2025-11-29 00:19:46'),('BC-A52FF7A872EC','ORDDE6F9D9B481048','2025-12-11 19:24:09'),('BC-AA0831495B58','ORD8FA96B91435711','2025-12-22 20:35:12'),('BC-B1EE69B46EDC','ORD5E29148B913790','2025-12-05 05:49:51'),('BC-C3E0F2470142','ORD991393CC434689','2025-12-22 20:18:09'),('BC-CF9E86222B04','ORD5A9F1A25520696','2025-12-12 06:24:57'),('BC-D470729CE73F','ORD294C2503363308','2025-11-28 20:55:09'),('BC-DC2154EADEFA','ORDF317E729967023','2025-11-24 06:50:24'),('BC-E4B5E39A1E80','ORDFEF782A0480042','2025-12-11 19:07:22'),('BC-EF350FAE8B62','ORD933C578B653147','2025-12-02 05:25:47'),('BC-EF4A45CFB558','ORD850277C4913745','2025-12-05 05:49:06'),('BC-F53B3DB95BAD','ORD8F760175221417','2025-11-27 05:30:18'),('BC-FA7FB4569851','ORDBBE14723969526','2025-11-24 07:32:07');

--
-- Table structure for table `sme`
--

DROP TABLE IF EXISTS `sme`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sme` (
  `sme_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `business_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tax_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE','PENDING') COLLATE utf8mb4_unicode_ci DEFAULT 'ACTIVE',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `area_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  PRIMARY KEY (`sme_id`),
  KEY `fk_sme_area` (`area_id`),
  CONSTRAINT `fk_sme_area` FOREIGN KEY (`area_id`) REFERENCES `areas` (`area_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `sme` VALUES ('0ece4642362845adbd342bfcc6ff4d','Công Ty Hoàng Sơn','56456465162','Trường Đại Học Mở TP.HCM, Ho Chi Minh City, HC, Vietnam','4544456456','hoangson@gmail.com','INACTIVE','2025-11-27 05:29:34','area-hcm-01',10.77615800,106.69036200),('6946766c25764b65a6d3dafff72334','Công Ty Trung Hậu','45646521','Gigamall Thủ Đức, Ho Chi Minh City, HC, Vietnam','0925464587','trunghau@gmail.com','ACTIVE','2025-11-24 05:58:18','area-hcm-01',10.82767200,106.72153900),('72f0045038d24b40a2c61ef9afa45c','Đại Học Tôn Đức Thắng ','5456456545','Đại học Tôn Đức Thắng, 19 Nguyễn Hữu Thọ, Tân Phong, Quận 7, Hồ Chí Minh','092564545454','tonducthang@gmail.com','ACTIVE','2025-12-05 06:42:08','AREA-153C32C6',10.73810000,106.71960000),('9f9b942e1f784ec28f10697ffd06f5','Công Ty Phần Mềm','45456465','Aeon Mall Bình Tân, Ho Chi Minh City, HC, Vietnam','654845665','phanmem@gmail.com','ACTIVE','2025-11-27 05:25:56','area-hcm-01',10.77690000,106.70090000),('a62f459e618044b88458f48a063286','công ty marketing','2312123132','AEON Mall Binh Duong, BI, Vietnam','0654162465','marketing@gmail.com','ACTIVE','2025-11-27 05:21:11','area-hcm-01',10.93244900,106.71140000),('bbd7e9fa4c9c4c46a6841ce2170ed9','Công Ty Vật Phẩm','545646512','Gigamall Thủ Đức, Ho Chi Minh City, HC, Vietnam','54564654555','vatpham@gmail.com','ACTIVE','2025-11-28 20:44:08','AREA-576B8E13',10.82767200,106.72153900);

--
-- Table structure for table `warehouses`
--

DROP TABLE IF EXISTS `warehouses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehouses` (
  `warehouse_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã kho',
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Tên kho',
  `address` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Địa chỉ chi tiết',
  `type` enum('HUB','SATELLITE','LOCAL_DEPOT') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'LOCAL_DEPOT',
  `capacity_limit` int NOT NULL DEFAULT '1000',
  `current_load` int NOT NULL DEFAULT '0',
  `area_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE','MAINTENANCE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ACTIVE',
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  PRIMARY KEY (`warehouse_id`),
  KEY `idx_warehouse_status` (`status`),
  KEY `idx_warehouse_type` (`type`),
  KEY `idx_warehouse_area` (`area_id`),
  CONSTRAINT `fk_warehouse_to_area` FOREIGN KEY (`area_id`) REFERENCES `areas` (`area_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `warehouses` VALUES ('WH-178BB075','Kho Phân Phối Nam Sài Gòn','1058 Nguyễn Văn Linh, Ho Chi Minh City, HC, Vietnam','SATELLITE',10000,0,'AREA-153C32C6','ACTIVE','0854564656','2025-11-28 05:27:58','2025-12-03 06:37:24',10.72915500,106.70430700),('WH-1B2D2177','Kho Vệ Tinh Hiệp Bình Chánh','Đại học Luật Thành phố Hồ Chí Minh, 123 Quốc Lộ 13, Phường Hiệp Bình Chánh, Quận Thủ Đức, Thành phố Hồ Chí Minh','SATELLITE',1000000,0,'AREA-576B8E13','ACTIVE','023125146545','2025-12-05 06:53:26','2025-12-05 06:53:26',10.82993064,106.71384065),('WH-29FCE9E8','Kho Phân Phối Quận 1','2 Công xã Paris, Ho Chi Minh City, HC, Vietnam','SATELLITE',10000,0,'area-hcm-01','ACTIVE','0925464587','2025-11-28 05:27:30','2025-11-28 05:27:30',10.78008700,106.69932900),('WH-99E941ED','Kho Hub Quận 1','Dinh Độc Lập, 135 Nam Kỳ Khởi Nghĩa, Phường Bến Thành, Quận 1, Thành phố Hồ Chí Minh','HUB',10000,0,'AREA-72077160','ACTIVE','02345364561','2025-12-12 05:13:53','2025-12-12 05:13:53',10.77712821,106.69540061),('WH-E672E0AC','Hub Logistics Khu Công Nghệ Cao','T2-4 Đường D1, Khu Công Nghệ Cao, Ho Chi Minh City, HC, Vietnam','HUB',1000,0,'AREA-576B8E13','ACTIVE','0925464587','2025-11-28 05:26:52','2025-11-28 05:26:52',10.84925500,106.79970300),('WH-E878545C','Kho Hub Quận 7','469 Nguyễn Hữu Thọ, Tân Hưng, Quận 7, Hồ Chí Minh','HUB',1000,0,'AREA-153C32C6','ACTIVE','0545664512','2025-12-12 05:08:38','2025-12-12 05:08:38',10.74073449,106.70156449);

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sme_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone` (`phone`),
  KEY `fk_user_sme` (`sme_id`),
  CONSTRAINT `fk_user_sme` FOREIGN KEY (`sme_id`) REFERENCES `sme` (`sme_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `user` VALUES ('0f9ddff515254b4f8dd18e5ed51962','tranvanb','$2b$12$hn2igr1hjDyMhEp3IqyW2OCanpx/1Yll.MKovyNJw09wyskwbpq2O','tranvanb@gmail.com','2312456','SHIPPER',NULL,'2025-11-28 05:33:22'),('15cdb7ce24a84d848eed323fe82a32','tonducthang','$2b$12$Q.SSVD6z2G3kG1jFkRDWDOjWAx3dgOsxfusUXLroWUgfUSxqkNG5q','tonducthang@gmail.com','092564545454','SME_OWNER','72f0045038d24b40a2c61ef9afa45c','2025-12-05 06:42:08'),('3bb4938c26cf4e93b52d9a82c77618','haudeptrai','$2b$12$32Jmj3nhMsLu9IrKcUDUlOzXEGG5nML5jiFVv1Fed6aQVgca3c4jO','haudeptrai@gmail.com','454654456','SHIPPER',NULL,'2025-11-24 06:15:12'),('7e2c73099b6e41c0806910fd94f6f3','nguyenvana','$2b$12$G2P.nKaXS4h8nQ5xGtSIFuL/Py9lcCWC0mrDpoYN.iVrKnVo2OqU.','nguyenvana@gmail.com','095465465456','SHIPPER',NULL,'2025-11-28 05:32:52'),('81325e55325f42b69c04fed00312f5','dieuphoivien01@gmail.com','$2b$12$QsAWmgoCIk636vNvbTCJBuolOXs5fCfRwHJEzdygmnDNsvAnp0Zg2','dieuphoivien01@gmail.com','09254564545112','DISPATCH',NULL,'2025-12-15 20:41:22'),('8260dbe6ca4e489295540afe37f378','trunghau','$2b$12$ZEnfKaJTFi63GzcmxVkc0enx0AQakySZE4CDAy1Z5x0okIwh0ye3u','trunghau@gmail.com','0925464587','SME_OWNER','6946766c25764b65a6d3dafff72334','2025-11-24 05:58:18'),('841ad651f2754c97a54fb90fcf583e','phanmem@gmail.com','$2b$12$jxLUee/ALvbWfvQePdcyhu4YpDx7Vi.T3wh8FttV2COlOMDjisN7G','phanmem@gmail.com','654845665','SME_OWNER','9f9b942e1f784ec28f10697ffd06f5','2025-11-27 05:25:57'),('8e63fe71c8df4b4eaaf9c784c8a9cf','minhkhang','$2b$12$LoYc4AOn0lr1T/.BQKqw0ezYOCSdPZbJddW2WVMQNKZPGe5I6vpAy','minhkhang@gmail.com','092546458711','WAREHOUSE_MANAGER',NULL,'2025-11-28 20:58:30'),('90f5d1302a784aea8acfc5f9267161','xetaiquan07','$2b$12$LhfDc3MM6A.kg.TJD1aoTO7lgxYaDkleMYJYnFjQN83Nt4gQjhivK','xetaiquan07@gmail.com','24564564654','SHIPPER',NULL,'2025-12-12 06:09:52'),('admin_2025_11_18_01','admin_moi','$2b$12$jJVD2nheInhTmjx/bZy5ZuH/T3Wt8TQKO8A//vROA8J55Ef2tUZKq','admin.moi@congty.com','0900000000','ADMIN',NULL,'2025-11-18 14:11:40'),('bfe426387ccf4080a3816bc84e9ee9','marketing','$2b$12$RZ/6qs5R1QDkVM8Ha5ek/ObyOH990.0qj3TTfjtooCfeApVDZqO/a','marketing@gmail.com','0654162465','SME_OWNER','a62f459e618044b88458f48a063286','2025-11-27 05:21:11'),('d30e706daf414bb9b5bfa514600007','vatpham','$2b$12$EU9ZdIj1NkufHKCaCTi7MONGMJE7D8b3SqQZNY5OrFjhf65ISoWkO','vatpham@gmail.com','54564654','SME_OWNER','bbd7e9fa4c9c4c46a6841ce2170ed9','2025-11-28 20:44:09'),('dea50eafa984440c9954b7d1056796','trunghau02','$2b$12$i/fQVXeQDcWkvlyMebvbGOiNEYxuQnNLb1XfiV.9XWEl99i9E28ii','trunghau02@gmail.com','0937890535','SHIPPER',NULL,'2025-11-24 06:10:23'),('e408d41b33934f70afba8dd9dd6d34','xetaiquan01','$2b$12$zztWF.2TuDscGubD4QbXlOnkdzpLdqA5jxkWm9A2yceU5U11jeni6','xetaiquan01@gmail.com','0215645645','SHIPPER',NULL,'2025-12-12 06:09:28'),('e68184da26a44bb5afe2bacd790324','hoangson','$2b$12$V/6anpGCbji6wlEwjizQWeS2fF0veDjYd7n0Rstay/TifSsEdzHL6','hoangson@gmail.com','4544456456','SME_OWNER','0ece4642362845adbd342bfcc6ff4d','2025-11-27 05:29:34'),('eb25cf6e62e7418bb5dc2af9260aa7','letuanle','$2b$12$IBve9COFEyut96trpOACmeDnGt6JRJINHpOLOADcC7qNLZbQq5RW.','le@gmail.com','55646516','WAREHOUSE_MANAGER',NULL,'2025-11-24 07:22:22'),('f6ceb3011baa489b8733f80861fbb4','testshipper','$2b$12$XcqHXgyhbAZosTtzbUsxouJLYU4y9PPzN0D2vgTz5i911d8NFjM26','testshipper@gmail.com','02456456465','SHIPPER',NULL,'2025-11-24 06:13:29'),('fd2c47b8ea644f16b4d22d02c04de3','nhanvienkho','$2b$12$xx1/tmITABnWorW6XvjTwOxDerB5fxQwerkf1FQJJh3KjOMPlJrza','nhanvienkho@gmail.com','264564651','WAREHOUSE_STAFF',NULL,'2025-11-24 07:24:17');

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `employee_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dob` date NOT NULL,
  `role` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `warehouse_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`employee_id`),
  UNIQUE KEY `phone` (`phone`),
  UNIQUE KEY `email` (`email`),
  KEY `user_id` (`user_id`),
  KEY `fk_emp_wh` (`warehouse_id`),
  CONSTRAINT `employees_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_emp_wh` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`warehouse_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `employees` VALUES ('EMP-1BAE963B','dieuphoivien01','2004-04-06','DISPATCH','09254564545112','dieuphoivien01@gmail.com','ACTIVE','81325e55325f42b69c04fed00312f5','2025-12-15 20:41:22','WH-E878545C'),('EMP-43A1DA44','Nguyễn Văn A','2004-04-06','SHIPPER','095465465456','nguyenvana@gmail.com','ACTIVE','7e2c73099b6e41c0806910fd94f6f3','2025-11-28 05:32:52','WH-E672E0AC'),('EMP-47DFD847','xetaiquan01','2004-04-06','SHIPPER','0215645645','xetaiquan01@gmail.com','ACTIVE','e408d41b33934f70afba8dd9dd6d34','2025-12-12 06:09:28','WH-99E941ED'),('EMP-637F9B1C','Lương Trung Hậu','2004-04-06','SHIPPER','0937890535','trunghau02@gmail.com','ACTIVE','dea50eafa984440c9954b7d1056796','2025-11-24 06:10:23','WH-E672E0AC'),('EMP-9D3091D6','Le Tuan Le','2004-10-12','WAREHOUSE_MANAGER','55646516','le@gmail.com','ACTIVE','eb25cf6e62e7418bb5dc2af9260aa7','2025-11-24 07:22:22','WH-E672E0AC'),('EMP-9EE0FCF2','Minh Khang','2004-08-02','WAREHOUSE_MANAGER','092546458711','minhkhang@gmail.com','ACTIVE','8e63fe71c8df4b4eaaf9c784c8a9cf','2025-11-28 20:58:30','WH-E672E0AC'),('EMP-B550974D','nhanvienkho','2002-12-11','WAREHOUSE_STAFF','264564651','nhanvienkho@gmail.com','ACTIVE','fd2c47b8ea644f16b4d22d02c04de3','2025-11-24 07:24:17','WH-E672E0AC'),('EMP-B5AB62DB','hau dep trai','2000-10-12','SHIPPER','454654456','haudeptrai@gmail.com','ACTIVE','3bb4938c26cf4e93b52d9a82c77618','2025-11-24 06:15:12','WH-E672E0AC'),('EMP-C24BC581','nguyen van a','2004-08-02','SHIPPER','02456456465','testshipper@gmail.com','ACTIVE','f6ceb3011baa489b8733f80861fbb4','2025-11-24 06:13:29','WH-E672E0AC'),('EMP-DF29B840','xetaiquan07','2004-04-06','SHIPPER','24564564654','xetaiquan07@gmail.com','ACTIVE','90f5d1302a784aea8acfc5f9267161','2025-12-12 06:09:52','WH-E878545C'),('EMP-E911C516','Trần Văn B','2004-04-06','SHIPPER','2312456','tranvanb@gmail.com','ACTIVE','0f9ddff515254b4f8dd18e5ed51962','2025-11-28 05:33:22','WH-E672E0AC');

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sme_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `receiver_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `receiver_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `receiver_address` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `receiver_latitude` decimal(10,8) DEFAULT NULL,
  `receiver_longitude` decimal(11,8) DEFAULT NULL,
  `weight` decimal(10,2) NOT NULL,
  `dimensions` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `note` text COLLATE utf8mb4_unicode_ci,
  `status` enum('PENDING','IN_TRANSIT','AT_WAREHOUSE','DELIVERING','COMPLETED','CANCELLED') COLLATE utf8mb4_unicode_ci DEFAULT 'PENDING',
  `area_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Khu vực của người nhận (tính toán trước)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `barcode_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`order_id`),
  UNIQUE KEY `order_code` (`order_code`),
  KEY `sme_id` (`sme_id`),
  KEY `barcode_id` (`barcode_id`),
  KEY `idx_order_area_status` (`area_id`,`status`),
  CONSTRAINT `fk_order_to_area` FOREIGN KEY (`area_id`) REFERENCES `areas` (`area_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`sme_id`) REFERENCES `sme` (`sme_id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `orders` VALUES ('55a082f9-f34f-4f69-99f8-ed7d37b5a3b4','ORDER-85AFDD71','bbd7e9fa4c9c4c46a6841ce2170ed9','Hậu','0879555964','Bamos Coffee Kim Sơn - Tân Phong, B68 Đ. Số 3, Khu dân cư Kim Sơn, Quận 7, Hồ Chí Minh',10.73484200,106.70073310,3.00,'10x12x20','Package Type: clothing; Instructions: cần vận chuyển','COMPLETED','AREA-576B8E13','2025-12-02 06:43:21','2025-12-22 19:00:19','BC-3E4CC3F23FAA'),('5a9f1a25-009c-490b-8554-78784a063fbc','ORDER-B9F9A641','bbd7e9fa4c9c4c46a6841ce2170ed9','Hoàng Thị Xuân Ny','0213412161','19 Nguyễn Hữu Thọ, Tân Phong, Quận 7, Hồ Chí Minh',10.73256176,106.69990214,2.00,'10x15x20','Package Type: clothing; Instructions: cần vận chuyển','COMPLETED','AREA-576B8E13','2025-12-12 06:24:57','2025-12-23 02:01:19','BC-CF9E86222B04'),('5e29148b-836a-4473-b703-5806f9a2592d','ORDER-B826E7A2','bbd7e9fa4c9c4c46a6841ce2170ed9','Hậu','0879555964','Dinh Độc Lập, 135 Nam Kỳ Khởi Nghĩa, Phường Bến Thành, Quận 1, Thành phố Hồ Chí Minh',10.77712821,106.69540061,3.00,'10x15x20','Package Type: clothing; Instructions: cần vận chuyển','IN_TRANSIT','AREA-576B8E13','2025-12-05 05:49:51','2025-12-22 18:54:51','BC-B1EE69B46EDC'),('622204c8-a764-45a4-b56c-d01a29b110b8','ORDER-A08F91C0','72f0045038d24b40a2c61ef9afa45c','Trung Hậu','0925464587','GIGAMALL THỦ ĐỨC, Phạm Văn Đồng, Hiệp Bình Chánh, Thủ Đức, Hồ Chí Minh',10.82795221,106.72168718,3.00,'10x15x20','Package Type: clothing; Instructions: cần vận chuyển','COMPLETED','AREA-153C32C6','2025-12-05 06:55:46','2025-12-23 02:05:47','BC-6754BC677990'),('850277c4-d1fc-4d52-9629-510c09b2bc42','ORDER-FF94ED1F','bbd7e9fa4c9c4c46a6841ce2170ed9','Luong Trung Hau','0879555964','Timezone - Cresent mall, Crescent Mall, Tôn Dật Tiên, Khu đô thị Phú Mỹ Hưng, Quận 7, Hồ Chí Minh',10.72876270,106.71932640,4.00,'10x15x20','Package Type: clothing; Instructions: cần vận chuyển gấp','COMPLETED','AREA-576B8E13','2025-12-05 05:49:06','2025-12-23 02:18:10','BC-EF4A45CFB558'),('9a77edb3-de2a-4028-ad16-1a5e44fbdb6c','ORDER-44C163D6','bbd7e9fa4c9c4c46a6841ce2170ed9','Hậu','0879555964','GIGAMALL THỦ ĐỨC, Phạm Văn Đồng, Hiệp Bình Chánh, Thủ Đức, Hồ Chí Minh',10.82795221,106.72168718,3.00,'15x20x20','Package Type: clothing; Instructions: cần vận chuyển','COMPLETED','AREA-576B8E13','2025-12-07 06:14:15','2025-12-23 02:03:12','BC-937FCD9903B4'),('de6f9d9b-d29b-49c4-b4ea-c6d957bd7e6a','ORDER-933139DA','bbd7e9fa4c9c4c46a6841ce2170ed9','Lương Trung Hậu','0879555964','Đại học Tôn Đức Thắng, 19 Nguyễn Hữu Thọ, Tân Phong, Quận 7, Hồ Chí Minh',10.73209138,106.69945522,3.00,'15x20x15','Package Type: clothing; Instructions: cần vận chuyển gấp','COMPLETED','AREA-576B8E13','2025-12-11 19:24:09','2025-12-23 02:09:08','BC-A52FF7A872EC'),('fef782a0-8fea-4b1a-baf0-23026ca7e19a','ORDER-333F3251','bbd7e9fa4c9c4c46a6841ce2170ed9','Lương Trung Hậu','0879555964','Timezone - Cresent mall, Crescent Mall, Tôn Dật Tiên, Khu đô thị Phú Mỹ Hưng, Quận 7, Hồ Chí Minh',10.72876270,106.71932640,3.00,'10x15x20','Package Type: clothing; Instructions: cần vận chuyển gấp','COMPLETED','AREA-576B8E13','2025-12-11 19:07:22','2025-12-23 02:10:17','BC-E4B5E39A1E80');

--
-- Table structure for table `shippers`
--

DROP TABLE IF EXISTS `shippers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shippers` (
  `shipper_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã shipper',
  `employee_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã nhân viên',
  `vehicle_type` enum('MOTORBIKE','CAR','TRUCK','BICYCLE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'MOTORBIKE',
  `status` enum('OFFLINE','ONLINE','DELIVERING') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'OFFLINE',
  `area_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Khu vực hoạt động',
  `rating` decimal(3,2) DEFAULT '5.00',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `fcm_token` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `current_latitude` decimal(10,8) DEFAULT NULL,
  `current_longitude` decimal(11,8) DEFAULT NULL,
  `last_location_update` datetime DEFAULT NULL,
  PRIMARY KEY (`shipper_id`),
  UNIQUE KEY `employee_id` (`employee_id`),
  KEY `idx_shipper_status` (`status`),
  KEY `idx_shipper_vehicle_type` (`vehicle_type`),
  KEY `idx_shipper_employee_id` (`employee_id`),
  KEY `idx_shipper_area_id` (`area_id`),
  CONSTRAINT `fk_shipper_to_area` FOREIGN KEY (`area_id`) REFERENCES `areas` (`area_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_shipper_to_employee` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `shippers` VALUES ('SHP-03DBE785','EMP-47DFD847','TRUCK','ONLINE','AREA-72077160',5.00,'2025-12-12 06:09:28','2025-12-12 13:09:28',NULL,NULL,NULL,NULL),('SHP-505552F9','EMP-E911C516','TRUCK','ONLINE','AREA-576B8E13',5.00,'2025-11-28 05:33:22','2025-12-17 02:13:25',NULL,NULL,NULL,NULL),('SHP-7E0C3376','EMP-C24BC581','MOTORBIKE','DELIVERING','AREA-576B8E13',5.00,'2025-11-24 06:13:29','2025-12-23 02:05:03','dnKBZu2GSd26dwSfkAd_LD:APA91bFO2LHr0VFQs_KAD98VbEnSocwjn1HfSCvhshynXvHGpKzX5GX4Nd2KBursJyf-22GCkDdAqejbtwe1YH1RISlQE5AAvssZ1kmx_DoWxtxVQa7vxO0',10.84904730,106.73118480,'2025-12-23 02:05:03'),('SHP-8161E565','EMP-637F9B1C','MOTORBIKE','DELIVERING','AREA-153C32C6',5.00,'2025-11-24 06:10:23','2025-12-23 02:07:10','dnKBZu2GSd26dwSfkAd_LD:APA91bFO2LHr0VFQs_KAD98VbEnSocwjn1HfSCvhshynXvHGpKzX5GX4Nd2KBursJyf-22GCkDdAqejbtwe1YH1RISlQE5AAvssZ1kmx_DoWxtxVQa7vxO0',10.84905570,106.73120880,'2025-12-23 02:07:10'),('SHP-A72D6B04','EMP-B5AB62DB','MOTORBIKE','DELIVERING','AREA-576B8E13',5.00,'2025-11-24 06:15:12','2025-12-23 02:56:46','dnKBZu2GSd26dwSfkAd_LD:APA91bFO2LHr0VFQs_KAD98VbEnSocwjn1HfSCvhshynXvHGpKzX5GX4Nd2KBursJyf-22GCkDdAqejbtwe1YH1RISlQE5AAvssZ1kmx_DoWxtxVQa7vxO0',10.84905140,106.73119370,'2025-12-23 02:56:46'),('SHP-B937D5E5','EMP-43A1DA44','MOTORBIKE','DELIVERING','AREA-576B8E13',5.00,'2025-11-28 05:32:52','2025-12-22 18:54:51',NULL,NULL,NULL,NULL),('SHP-DA7B4882','EMP-DF29B840','TRUCK','ONLINE','AREA-153C32C6',5.00,'2025-12-12 06:09:52','2025-12-12 13:09:51',NULL,NULL,NULL,NULL);

--
-- Table structure for table `order_journey_legs`
--

DROP TABLE IF EXISTS `order_journey_legs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_journey_legs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sequence` int NOT NULL DEFAULT '1',
  `leg_type` enum('PICKUP','TRANSFER','DELIVERY') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PICKUP',
  `status` enum('PENDING','IN_PROGRESS','COMPLETED') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDING',
  `origin_warehouse_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `origin_sme_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `destination_warehouse_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `destination_is_receiver` tinyint(1) NOT NULL DEFAULT '0',
  `assigned_shipper_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `estimated_distance` decimal(8,2) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `origin_warehouse_id` (`origin_warehouse_id`),
  KEY `destination_warehouse_id` (`destination_warehouse_id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_status` (`status`),
  KEY `idx_assigned_shipper_id` (`assigned_shipper_id`),
  KEY `idx_origin_sme_id` (`origin_sme_id`),
  KEY `idx_destination_is_receiver` (`destination_is_receiver`),
  CONSTRAINT `fk_leg_origin_sme` FOREIGN KEY (`origin_sme_id`) REFERENCES `sme` (`sme_id`),
  CONSTRAINT `order_journey_legs_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT `order_journey_legs_ibfk_2` FOREIGN KEY (`origin_warehouse_id`) REFERENCES `warehouses` (`warehouse_id`),
  CONSTRAINT `order_journey_legs_ibfk_3` FOREIGN KEY (`destination_warehouse_id`) REFERENCES `warehouses` (`warehouse_id`),
  CONSTRAINT `order_journey_legs_ibfk_4` FOREIGN KEY (`assigned_shipper_id`) REFERENCES `shippers` (`shipper_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

INSERT INTO `order_journey_legs` VALUES (1,'622204c8-a764-45a4-b56c-d01a29b110b8',1,'PICKUP','COMPLETED',NULL,'72f0045038d24b40a2c61ef9afa45c','WH-E878545C',0,'SHP-8161E565','2025-12-23 02:05:26','2025-12-23 02:05:30',2.56,'2025-12-23 01:54:31','2025-12-23 02:05:30'),(2,'622204c8-a764-45a4-b56c-d01a29b110b8',2,'TRANSFER','COMPLETED','WH-E878545C',NULL,'WH-1B2D2177',0,'SHP-8161E565','2025-12-23 02:05:34','2025-12-23 02:05:37',13.86,'2025-12-23 01:54:31','2025-12-23 02:05:37'),(3,'622204c8-a764-45a4-b56c-d01a29b110b8',3,'DELIVERY','COMPLETED','WH-1B2D2177',NULL,NULL,1,'SHP-8161E565','2025-12-23 02:05:42',NULL,1.79,'2025-12-23 01:54:31','2025-12-23 09:05:47'),(4,'5a9f1a25-009c-490b-8554-78784a063fbc',1,'PICKUP','COMPLETED',NULL,'bbd7e9fa4c9c4c46a6841ce2170ed9','WH-99E941ED',0,'SHP-7E0C3376','2025-12-23 02:01:04','2025-12-23 02:01:06',7.82,'2025-12-23 01:54:51','2025-12-23 02:01:06'),(5,'5a9f1a25-009c-490b-8554-78784a063fbc',2,'TRANSFER','COMPLETED','WH-99E941ED',NULL,'WH-178BB075',0,'SHP-7E0C3376','2025-12-23 02:01:08','2025-12-23 02:01:11',8.99,'2025-12-23 01:54:51','2025-12-23 02:01:11'),(6,'5a9f1a25-009c-490b-8554-78784a063fbc',3,'DELIVERY','COMPLETED','WH-178BB075',NULL,NULL,1,'SHP-7E0C3376','2025-12-23 02:01:13',NULL,4.12,'2025-12-23 01:54:51','2025-12-23 09:01:19'),(7,'55a082f9-f34f-4f69-99f8-ed7d37b5a3b4',1,'PICKUP','COMPLETED',NULL,'bbd7e9fa4c9c4c46a6841ce2170ed9','WH-99E941ED',0,'SHP-7E0C3376','2025-12-23 02:00:02','2025-12-23 02:00:05',7.82,'2025-12-23 01:54:51','2025-12-23 02:00:05'),(8,'55a082f9-f34f-4f69-99f8-ed7d37b5a3b4',2,'TRANSFER','COMPLETED','WH-99E941ED',NULL,'WH-178BB075',0,'SHP-7E0C3376','2025-12-23 02:00:09','2025-12-23 02:00:13',8.99,'2025-12-23 01:54:51','2025-12-23 02:00:13'),(9,'55a082f9-f34f-4f69-99f8-ed7d37b5a3b4',3,'DELIVERY','COMPLETED','WH-178BB075',NULL,NULL,1,'SHP-7E0C3376','2025-12-23 02:00:16','2025-12-23 02:00:19',4.51,'2025-12-23 01:54:51','2025-12-23 02:00:19'),(10,'9a77edb3-de2a-4028-ad16-1a5e44fbdb6c',1,'PICKUP','COMPLETED',NULL,'bbd7e9fa4c9c4c46a6841ce2170ed9','WH-99E941ED',0,'SHP-7E0C3376','2025-12-23 02:02:58','2025-12-23 02:03:01',7.82,'2025-12-23 01:54:51','2025-12-23 02:03:01'),(11,'9a77edb3-de2a-4028-ad16-1a5e44fbdb6c',2,'TRANSFER','COMPLETED','WH-99E941ED',NULL,'WH-1B2D2177',0,'SHP-7E0C3376','2025-12-23 02:03:03','2025-12-23 02:03:05',9.23,'2025-12-23 01:54:51','2025-12-23 02:03:05'),(12,'9a77edb3-de2a-4028-ad16-1a5e44fbdb6c',3,'DELIVERY','COMPLETED','WH-1B2D2177',NULL,NULL,1,'SHP-7E0C3376','2025-12-23 02:03:08',NULL,1.79,'2025-12-23 01:54:51','2025-12-23 09:03:12'),(13,'de6f9d9b-d29b-49c4-b4ea-c6d957bd7e6a',1,'PICKUP','COMPLETED',NULL,'bbd7e9fa4c9c4c46a6841ce2170ed9','WH-99E941ED',0,'SHP-A72D6B04','2025-12-23 02:08:52','2025-12-23 02:08:54',7.82,'2025-12-23 01:54:51','2025-12-23 02:08:54'),(14,'de6f9d9b-d29b-49c4-b4ea-c6d957bd7e6a',2,'TRANSFER','COMPLETED','WH-99E941ED',NULL,'WH-178BB075',0,'SHP-A72D6B04','2025-12-23 02:08:56','2025-12-23 02:08:59',8.99,'2025-12-23 01:54:51','2025-12-23 02:08:59'),(15,'de6f9d9b-d29b-49c4-b4ea-c6d957bd7e6a',3,'DELIVERY','COMPLETED','WH-178BB075',NULL,NULL,1,'SHP-A72D6B04','2025-12-23 02:09:02',NULL,4.21,'2025-12-23 01:54:51','2025-12-23 09:09:08'),(16,'fef782a0-8fea-4b1a-baf0-23026ca7e19a',1,'PICKUP','COMPLETED',NULL,'bbd7e9fa4c9c4c46a6841ce2170ed9','WH-99E941ED',0,'SHP-A72D6B04','2025-12-23 02:10:00','2025-12-23 02:10:04',7.82,'2025-12-23 01:54:51','2025-12-23 02:10:04'),(17,'fef782a0-8fea-4b1a-baf0-23026ca7e19a',2,'TRANSFER','COMPLETED','WH-99E941ED',NULL,'WH-178BB075',0,'SHP-A72D6B04','2025-12-23 02:10:07','2025-12-23 02:10:10',8.99,'2025-12-23 01:54:51','2025-12-23 02:10:10'),(18,'fef782a0-8fea-4b1a-baf0-23026ca7e19a',3,'DELIVERY','COMPLETED','WH-178BB075',NULL,NULL,1,'SHP-A72D6B04','2025-12-23 02:10:12',NULL,2.12,'2025-12-23 01:54:51','2025-12-23 09:10:17'),(19,'850277c4-d1fc-4d52-9629-510c09b2bc42',1,'PICKUP','COMPLETED',NULL,'bbd7e9fa4c9c4c46a6841ce2170ed9','WH-99E941ED',0,'SHP-A72D6B04','2025-12-23 02:17:58','2025-12-23 02:18:00',7.82,'2025-12-23 01:54:51','2025-12-23 02:18:00'),(20,'850277c4-d1fc-4d52-9629-510c09b2bc42',2,'TRANSFER','COMPLETED','WH-99E941ED',NULL,'WH-178BB075',0,'SHP-A72D6B04','2025-12-23 02:18:02','2025-12-23 02:18:04',8.99,'2025-12-23 01:54:51','2025-12-23 02:18:04'),(21,'850277c4-d1fc-4d52-9629-510c09b2bc42',3,'DELIVERY','COMPLETED','WH-178BB075',NULL,NULL,1,'SHP-A72D6B04','2025-12-23 02:18:06',NULL,2.12,'2025-12-23 01:54:51','2025-12-23 09:18:10'),(22,'5e29148b-836a-4473-b703-5806f9a2592d',1,'PICKUP','PENDING',NULL,'bbd7e9fa4c9c4c46a6841ce2170ed9','WH-99E941ED',0,'SHP-B937D5E5',NULL,NULL,7.82,'2025-12-23 01:54:51','2025-12-23 01:54:51'),(23,'5e29148b-836a-4473-b703-5806f9a2592d',2,'TRANSFER','PENDING','WH-99E941ED',NULL,'WH-29FCE9E8',0,NULL,NULL,NULL,0.90,'2025-12-23 01:54:51','2025-12-23 01:54:51'),(24,'5e29148b-836a-4473-b703-5806f9a2592d',3,'DELIVERY','PENDING','WH-29FCE9E8',NULL,NULL,1,NULL,NULL,NULL,0.90,'2025-12-23 01:54:51','2025-12-23 01:54:51');

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;