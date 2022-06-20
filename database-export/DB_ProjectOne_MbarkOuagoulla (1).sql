CREATE DATABASE  IF NOT EXISTS `smartletterbox` /*!40100 DEFAULT CHARACTER SET utf8 */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `smartletterbox`;
-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: smartletterbox
-- ------------------------------------------------------
-- Server version	8.0.28

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `acties`
--

DROP TABLE IF EXISTS `acties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `acties` (
  `ActieID` int NOT NULL AUTO_INCREMENT,
  `ActieBeschrijving` varchar(150) NOT NULL,
  PRIMARY KEY (`ActieID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `acties`
--

LOCK TABLES `acties` WRITE;
/*!40000 ALTER TABLE `acties` DISABLE KEYS */;
INSERT INTO `acties` VALUES (1,'Deurtje open'),(2,'Deurtje toe'),(3,'Postbus leeggemaakt'),(4,'Gebruiker meldt zich aan');
/*!40000 ALTER TABLE `acties` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gebruikers`
--

DROP TABLE IF EXISTS `gebruikers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gebruikers` (
  `GebruikerID` int NOT NULL,
  `Naam` varchar(45) NOT NULL,
  `Voornaam` varchar(45) NOT NULL,
  `RFID-code` varchar(30) NOT NULL,
  `E-mail-adres` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`GebruikerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gebruikers`
--

LOCK TABLES `gebruikers` WRITE;
/*!40000 ALTER TABLE `gebruikers` DISABLE KEYS */;
INSERT INTO `gebruikers` VALUES (1,'Alleman','Jan','0XF33432D','jan.alleman@live.be'),(2,'Vander','Pieter','0DR44531Q','pieter.vander@live.be'),(3,'Huys','Dieter','0PP25644C','dieter.huys@live.be');
/*!40000 ALTER TABLE `gebruikers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historiekacties`
--

DROP TABLE IF EXISTS `historiekacties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historiekacties` (
  `HistoriekActieID` int NOT NULL AUTO_INCREMENT,
  `FK_ActieID` int NOT NULL,
  `Datum` datetime NOT NULL,
  `FK_GebruikerID` int NOT NULL,
  PRIMARY KEY (`HistoriekActieID`),
  KEY `FK_ActieID_idx` (`FK_ActieID`),
  KEY `FK_GebruikerID_idx` (`FK_GebruikerID`),
  CONSTRAINT `FK_ActieID` FOREIGN KEY (`FK_ActieID`) REFERENCES `acties` (`ActieID`),
  CONSTRAINT `FK_GebruikerID` FOREIGN KEY (`FK_GebruikerID`) REFERENCES `gebruikers` (`GebruikerID`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historiekacties`
--

LOCK TABLES `historiekacties` WRITE;
/*!40000 ALTER TABLE `historiekacties` DISABLE KEYS */;
INSERT INTO `historiekacties` VALUES (1,2,'2021-10-28 13:51:22',2),(2,4,'2021-08-06 21:40:21',1),(3,2,'2021-08-12 00:51:55',2),(4,4,'2021-10-23 04:59:54',3),(5,1,'2021-11-26 02:11:54',2),(6,2,'2022-04-21 14:33:52',1),(7,3,'2021-07-03 08:54:11',3),(8,1,'2022-07-18 12:06:22',1),(9,3,'2022-03-30 03:13:26',2),(10,2,'2022-07-08 04:52:09',1),(11,4,'2023-05-13 09:10:21',2),(12,1,'2022-08-12 13:45:53',2),(13,3,'2021-09-03 00:38:30',2),(14,3,'2022-02-04 10:03:34',3),(15,4,'2021-12-15 02:36:15',3),(16,4,'2022-11-26 01:22:24',2),(17,4,'2021-08-10 07:48:34',3),(18,2,'2021-11-12 02:32:03',2),(19,4,'2021-07-19 19:37:26',3),(20,1,'2022-06-02 11:16:05',2),(21,4,'2023-02-12 23:51:39',1),(22,2,'2022-05-25 02:40:03',2),(23,2,'2022-05-15 16:00:15',2),(24,3,'2022-09-04 10:40:40',3),(25,3,'2023-03-09 19:11:12',1),(26,2,'2022-04-26 14:16:42',2),(27,1,'2021-06-22 15:33:18',3),(28,3,'2021-09-06 22:32:34',3),(29,2,'2021-07-02 20:09:53',1),(30,3,'2022-12-25 16:03:07',3),(31,4,'2022-04-26 22:31:07',2),(32,3,'2022-09-07 20:27:23',3),(33,2,'2021-06-16 23:41:37',3),(34,3,'2021-09-14 11:25:34',1),(35,4,'2021-11-21 05:48:18',3),(36,2,'2022-08-14 00:29:32',3),(37,4,'2022-08-27 09:30:41',3),(38,1,'2022-06-30 08:24:12',2),(39,4,'2022-03-17 12:47:11',3),(40,2,'2022-07-12 14:03:40',3),(41,3,'2022-02-12 09:25:12',3),(42,4,'2021-09-25 02:00:45',3),(43,4,'2021-09-18 00:36:03',2),(44,3,'2022-03-01 06:41:53',2),(45,3,'2022-11-20 15:56:24',1),(46,2,'2021-06-23 02:28:58',3),(47,3,'2023-01-10 19:42:08',1),(48,4,'2023-04-12 18:41:42',2),(49,4,'2023-02-09 23:05:35',1),(50,2,'2022-10-06 15:31:28',1);
/*!40000 ALTER TABLE `historiekacties` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historieksensors`
--

DROP TABLE IF EXISTS `historieksensors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historieksensors` (
  `HistoriekSensorID` int NOT NULL AUTO_INCREMENT,
  `FK_SensorID` int NOT NULL,
  `Datum` datetime NOT NULL,
  `Waarde` varchar(50) NOT NULL,
  PRIMARY KEY (`HistoriekSensorID`),
  KEY `FK_SensorID_idx` (`FK_SensorID`),
  CONSTRAINT `FK_SensorID` FOREIGN KEY (`FK_SensorID`) REFERENCES `sensors` (`SensorID`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historieksensors`
--

LOCK TABLES `historieksensors` WRITE;
/*!40000 ALTER TABLE `historieksensors` DISABLE KEYS */;
INSERT INTO `historieksensors` VALUES (1,1,'2021-10-28 13:51:22','15 g'),(2,2,'2021-08-06 21:40:21','TRUE'),(3,3,'2021-08-12 00:51:55','0X244RFG'),(4,1,'2021-10-23 04:59:54','15 g'),(5,2,'2021-11-26 02:11:54','TRUE'),(6,3,'2022-04-21 14:33:52','0X244RFG'),(7,1,'2021-07-03 08:54:11','15 g'),(8,2,'2022-07-18 12:06:22','TRUE'),(9,3,'2022-03-30 03:13:26','0X244RFG'),(10,1,'2022-07-08 04:52:09','15 g'),(11,2,'2023-05-13 09:10:21','TRUE'),(12,3,'2022-08-12 13:45:53','0X244RFG'),(13,1,'2021-09-03 00:38:30','15 g'),(14,2,'2022-02-04 10:03:34','TRUE'),(15,3,'2021-12-15 02:36:15','0X244RFG'),(16,1,'2022-11-26 01:22:24','15 g'),(17,2,'2021-08-10 07:48:34','TRUE'),(18,3,'2021-11-12 02:32:03','0X244RFG'),(19,1,'2021-07-19 19:37:26','15 g'),(20,2,'2022-06-02 11:16:05','TRUE'),(21,3,'2023-02-12 23:51:39','0X244RFG'),(22,1,'2022-05-25 02:40:03','15 g'),(23,2,'2022-05-15 16:00:15','TRUE'),(24,3,'2022-09-04 10:40:40','0X244RFG'),(25,1,'2023-03-09 19:11:12','15 g'),(26,2,'2022-04-26 14:16:42','TRUE'),(27,3,'2021-06-22 15:33:18','0X244RFG'),(28,1,'2021-09-06 22:32:34','15 g'),(29,2,'2021-07-02 20:09:53','TRUE'),(30,3,'2022-12-25 16:03:07','0X244RFG'),(31,1,'2022-04-26 22:31:07','15 g'),(32,2,'2022-09-07 20:27:23','TRUE'),(33,3,'2021-06-16 23:41:37','0X244RFG'),(34,1,'2021-09-14 11:25:34','15 g'),(35,2,'2021-11-21 05:48:18','TRUE'),(36,3,'2022-08-14 00:29:32','0X244RFG'),(37,1,'2022-08-27 09:30:41','15 g'),(38,2,'2022-06-30 08:24:12','TRUE'),(39,3,'2022-03-17 12:47:11','0X244RFG'),(40,1,'2022-07-12 14:03:40','15 g'),(41,2,'2022-02-12 09:25:12','TRUE'),(42,3,'2021-09-25 02:00:45','0X244RFG'),(43,1,'2021-09-18 00:36:03','15 g'),(44,2,'2022-03-01 06:41:53','TRUE'),(45,3,'2022-11-20 15:56:24','0X244RFG'),(46,1,'2021-06-23 02:28:58','15 g'),(47,2,'2023-01-10 19:42:08','TRUE'),(48,3,'2023-04-12 18:41:42','0X244RFG'),(49,1,'2023-02-09 23:05:35','15 g'),(50,2,'2022-10-06 15:31:28','TRUE');
/*!40000 ALTER TABLE `historieksensors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensors`
--

DROP TABLE IF EXISTS `sensors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensors` (
  `SensorID` int NOT NULL AUTO_INCREMENT,
  `Naam` varchar(45) NOT NULL,
  `Output` varchar(10) DEFAULT 'N.v.t',
  `Kostprijs` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`SensorID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensors`
--

LOCK TABLES `sensors` WRITE;
/*!40000 ALTER TABLE `sensors` DISABLE KEYS */;
INSERT INTO `sensors` VALUES (1,'Weegsensor','g',NULL),(2,'Reedcontact','N.v.t',NULL),(3,'RFID-lezer','N.v.t',NULL);
/*!40000 ALTER TABLE `sensors` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-05-24 11:05:27
