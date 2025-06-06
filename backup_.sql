-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: agricommerce
-- ------------------------------------------------------
-- Server version	8.0.42

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
-- Table structure for table `ac_escrowtransaction`
--

DROP TABLE IF EXISTS `ac_escrowtransaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ac_escrowtransaction` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity` int unsigned NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(20) NOT NULL,
  `telebirr_reference` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `auto_release_date` datetime(6) NOT NULL,
  `buyer_id` bigint NOT NULL,
  `seller_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `telebirr_reference` (`telebirr_reference`),
  KEY `ac_escrowtransaction_buyer_id_4707cfb2_fk_ac_user_id` (`buyer_id`),
  KEY `ac_escrowtransaction_seller_id_59b467b2_fk_ac_user_id` (`seller_id`),
  KEY `ac_escrowtransaction_product_id_8612c7c3_fk_ac_product_id` (`product_id`),
  CONSTRAINT `ac_escrowtransaction_buyer_id_4707cfb2_fk_ac_user_id` FOREIGN KEY (`buyer_id`) REFERENCES `ac_user` (`id`),
  CONSTRAINT `ac_escrowtransaction_product_id_8612c7c3_fk_ac_product_id` FOREIGN KEY (`product_id`) REFERENCES `ac_product` (`id`),
  CONSTRAINT `ac_escrowtransaction_seller_id_59b467b2_fk_ac_user_id` FOREIGN KEY (`seller_id`) REFERENCES `ac_user` (`id`),
  CONSTRAINT `ac_escrowtransaction_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ac_escrowtransaction`
--

LOCK TABLES `ac_escrowtransaction` WRITE;
/*!40000 ALTER TABLE `ac_escrowtransaction` DISABLE KEYS */;
INSERT INTO `ac_escrowtransaction` VALUES (1,1,150.00,'completed',NULL,'2025-05-03 01:48:26.480661','2025-05-10 01:48:26.479879',1,2,1);
/*!40000 ALTER TABLE `ac_escrowtransaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ac_farmerprofile`
--

DROP TABLE IF EXISTS `ac_farmerprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ac_farmerprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `farm_name` varchar(100) NOT NULL,
  `location` varchar(100) NOT NULL,
  `certification` varchar(100) DEFAULT NULL,
  `rating` double NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `ac_farmerprofile_user_id_789647f2_fk_ac_user_id` FOREIGN KEY (`user_id`) REFERENCES `ac_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ac_farmerprofile`
--

LOCK TABLES `ac_farmerprofile` WRITE;
/*!40000 ALTER TABLE `ac_farmerprofile` DISABLE KEYS */;
/*!40000 ALTER TABLE `ac_farmerprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ac_product`
--

DROP TABLE IF EXISTS `ac_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ac_product` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `category` varchar(20) NOT NULL,
  `stock_quantity` int unsigned NOT NULL,
  `harvest_date` date DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `seller_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ac_product_seller_id_ddec41ab_fk_ac_user_id` (`seller_id`),
  CONSTRAINT `ac_product_seller_id_ddec41ab_fk_ac_user_id` FOREIGN KEY (`seller_id`) REFERENCES `ac_user` (`id`),
  CONSTRAINT `ac_product_chk_1` CHECK ((`stock_quantity` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ac_product`
--

LOCK TABLES `ac_product` WRITE;
/*!40000 ALTER TABLE `ac_product` DISABLE KEYS */;
INSERT INTO `ac_product` VALUES (1,'Test Coffee Beans','',150.00,'CROP',0,NULL,'2025-05-03 01:47:38.245635',2);
/*!40000 ALTER TABLE `ac_product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ac_transactionupdate`
--

DROP TABLE IF EXISTS `ac_transactionupdate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ac_transactionupdate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `message` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `transaction_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ac_transactionupdate_created_by_id_9e419d1a_fk_ac_user_id` (`created_by_id`),
  KEY `ac_transactionupdate_transaction_id_cdb67fd4_fk_ac_escrow` (`transaction_id`),
  CONSTRAINT `ac_transactionupdate_created_by_id_9e419d1a_fk_ac_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `ac_user` (`id`),
  CONSTRAINT `ac_transactionupdate_transaction_id_cdb67fd4_fk_ac_escrow` FOREIGN KEY (`transaction_id`) REFERENCES `ac_escrowtransaction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ac_transactionupdate`
--

LOCK TABLES `ac_transactionupdate` WRITE;
/*!40000 ALTER TABLE `ac_transactionupdate` DISABLE KEYS */;
/*!40000 ALTER TABLE `ac_transactionupdate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ac_user`
--

DROP TABLE IF EXISTS `ac_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ac_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(20) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `wallet_balance` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ac_user`
--

LOCK TABLES `ac_user` WRITE;
/*!40000 ALTER TABLE `ac_user` DISABLE KEYS */;
INSERT INTO `ac_user` VALUES (1,'pbkdf2_sha256$1000000$IM3lJ0NwOj5hetxOqb0CEB$JNHFcgLqy7Kdw2ONIWJjaeM57nKYsmTG56e7syg/qbk=',NULL,0,'test_buyer','','','',0,1,'2025-05-03 01:47:16.418642','BUYER',NULL,850.00),(2,'pbkdf2_sha256$1000000$jEGKKKOPVpBhq8T2qDIzd8$qBuLT7ayBcvsRFo4tuWB6Hmj4Toy3QwmRoXKaCDJWSk=',NULL,0,'test_seller','','','',0,1,'2025-05-03 01:47:17.592673','FARMER',NULL,150.00),(3,'!7aDVg2W3ztovpviaifGWMdO2YPAbfrPts2eBg4mV',NULL,0,'test','','','',0,1,'2025-05-03 01:54:50.303858','BUYER','+1234567890',0.00);
/*!40000 ALTER TABLE `ac_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ac_user_groups`
--

DROP TABLE IF EXISTS `ac_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ac_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ac_user_groups_user_id_group_id_dfeb4614_uniq` (`user_id`,`group_id`),
  KEY `ac_user_groups_group_id_c00f9255_fk_auth_group_id` (`group_id`),
  CONSTRAINT `ac_user_groups_group_id_c00f9255_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `ac_user_groups_user_id_fc00fe98_fk_ac_user_id` FOREIGN KEY (`user_id`) REFERENCES `ac_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ac_user_groups`
--

LOCK TABLES `ac_user_groups` WRITE;
/*!40000 ALTER TABLE `ac_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `ac_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ac_user_user_permissions`
--

DROP TABLE IF EXISTS `ac_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ac_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ac_user_user_permissions_user_id_permission_id_58bf567b_uniq` (`user_id`,`permission_id`),
  KEY `ac_user_user_permiss_permission_id_90bd6e9b_fk_auth_perm` (`permission_id`),
  CONSTRAINT `ac_user_user_permiss_permission_id_90bd6e9b_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `ac_user_user_permissions_user_id_8ac6283f_fk_ac_user_id` FOREIGN KEY (`user_id`) REFERENCES `ac_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ac_user_user_permissions`
--

LOCK TABLES `ac_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `ac_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `ac_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add user',6,'add_user'),(22,'Can change user',6,'change_user'),(23,'Can delete user',6,'delete_user'),(24,'Can view user',6,'view_user'),(25,'Can add farmer profile',7,'add_farmerprofile'),(26,'Can change farmer profile',7,'change_farmerprofile'),(27,'Can delete farmer profile',7,'delete_farmerprofile'),(28,'Can view farmer profile',7,'view_farmerprofile'),(29,'Can add product',8,'add_product'),(30,'Can change product',8,'change_product'),(31,'Can delete product',8,'delete_product'),(32,'Can view product',8,'view_product'),(33,'Can add escrow transaction',9,'add_escrowtransaction'),(34,'Can change escrow transaction',9,'change_escrowtransaction'),(35,'Can delete escrow transaction',9,'delete_escrowtransaction'),(36,'Can view escrow transaction',9,'view_escrowtransaction'),(37,'Can add transaction update',10,'add_transactionupdate'),(38,'Can change transaction update',10,'change_transactionupdate'),(39,'Can delete transaction update',10,'delete_transactionupdate'),(40,'Can view transaction update',10,'view_transactionupdate');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_ac_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_ac_user_id` FOREIGN KEY (`user_id`) REFERENCES `ac_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (9,'ac','escrowtransaction'),(7,'ac','farmerprofile'),(8,'ac','product'),(10,'ac','transactionupdate'),(6,'ac','user'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-05-02 23:20:21.188197'),(2,'contenttypes','0002_remove_content_type_name','2025-05-02 23:20:21.409287'),(3,'auth','0001_initial','2025-05-02 23:20:22.124445'),(4,'auth','0002_alter_permission_name_max_length','2025-05-02 23:20:22.270485'),(5,'auth','0003_alter_user_email_max_length','2025-05-02 23:20:22.288788'),(6,'auth','0004_alter_user_username_opts','2025-05-02 23:20:22.308629'),(7,'auth','0005_alter_user_last_login_null','2025-05-02 23:20:22.327023'),(8,'auth','0006_require_contenttypes_0002','2025-05-02 23:20:22.335525'),(9,'auth','0007_alter_validators_add_error_messages','2025-05-02 23:20:22.353465'),(10,'auth','0008_alter_user_username_max_length','2025-05-02 23:20:22.372887'),(11,'auth','0009_alter_user_last_name_max_length','2025-05-02 23:20:22.391488'),(12,'auth','0010_alter_group_name_max_length','2025-05-02 23:20:22.438294'),(13,'auth','0011_update_proxy_permissions','2025-05-02 23:20:22.459876'),(14,'auth','0012_alter_user_first_name_max_length','2025-05-02 23:20:22.479540'),(15,'ac','0001_initial','2025-05-02 23:20:24.696328'),(16,'admin','0001_initial','2025-05-02 23:20:25.135493'),(17,'admin','0002_logentry_remove_auto_add','2025-05-02 23:20:25.172243'),(18,'admin','0003_logentry_add_action_flag_choices','2025-05-02 23:20:25.220529'),(19,'sessions','0001_initial','2025-05-02 23:20:25.312333'),(20,'ac','0002_alter_user_phone','2025-05-03 01:44:16.575959');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-03 11:33:22
