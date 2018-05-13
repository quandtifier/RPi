-- MySQL dump 10.13  Distrib 5.5.60, for debian-linux-gnu (armv8l)
--
-- Host: localhost    Database: noise_canceller
-- ------------------------------------------------------
-- Server version	5.5.60-0+deb8u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `noise_data`
--

DROP TABLE IF EXISTS `noise_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `noise_data` (
  `start_of_delta` time NOT NULL,
  `end_of_delta` time DEFAULT NULL,
  `avg_noise` decimal(10,0) DEFAULT NULL,
  `max_noise` decimal(10,0) DEFAULT NULL,
  `min_noise` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`start_of_delta`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `noise_data`
--

LOCK TABLES `noise_data` WRITE;
/*!40000 ALTER TABLE `noise_data` DISABLE KEYS */;
INSERT INTO `noise_data` VALUES ('17:12:00','17:12:05',247,330,165),('17:12:10','17:12:15',0,0,0),('17:12:21','17:12:26',4,14,0),('17:12:32','17:12:37',249,747,0),('17:12:43','17:12:48',287,748,54),('17:12:54','17:12:59',178,534,0),('17:13:05','17:13:10',316,758,0),('17:13:16','17:13:21',204,275,133),('17:13:26','17:13:31',94,133,75),('17:13:37','17:13:42',329,837,76),('17:13:48','17:13:53',330,837,75);
/*!40000 ALTER TABLE `noise_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `noise_readings`
--

DROP TABLE IF EXISTS `noise_readings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `noise_readings` (
  `rtime` time NOT NULL,
  `noise_level` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`rtime`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `noise_readings`
--

LOCK TABLES `noise_readings` WRITE;
/*!40000 ALTER TABLE `noise_readings` DISABLE KEYS */;
INSERT INTO `noise_readings` VALUES ('17:11:56',0),('17:11:58',272),('17:12:00',15),('17:12:02',165),('17:12:05',330),('17:12:07',744),('17:12:09',99),('17:12:11',0),('17:12:13',0),('17:12:15',0),('17:12:18',694),('17:12:20',0),('17:12:22',14),('17:12:24',0),('17:12:26',0),('17:12:28',746),('17:12:31',0),('17:12:33',747),('17:12:35',0),('17:12:37',0),('17:12:39',0),('17:12:42',0),('17:12:44',54),('17:12:46',60),('17:12:48',748),('17:12:50',0),('17:12:53',0),('17:12:55',0),('17:12:57',0),('17:12:59',534),('17:13:01',0),('17:13:03',30),('17:13:06',0),('17:13:08',191),('17:13:10',758),('17:13:12',39),('17:13:14',134),('17:13:16',101),('17:13:19',133),('17:13:21',275),('17:13:23',75),('17:13:25',123),('17:13:27',75),('17:13:29',75),('17:13:31',133),('17:13:34',666),('17:13:36',79),('17:13:38',76),('17:13:40',76),('17:13:42',837),('17:13:45',237),('17:13:47',786),('17:13:49',837),('17:13:51',75),('17:13:53',78),('17:13:55',641),('17:13:57',77);
/*!40000 ALTER TABLE `noise_readings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wind_data`
--

DROP TABLE IF EXISTS `wind_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wind_data` (
  `start_of_delta` time NOT NULL,
  `end_of_delta` time DEFAULT NULL,
  `avg_noise` decimal(10,0) DEFAULT NULL,
  `max_noise` decimal(10,0) DEFAULT NULL,
  `min_noise` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`start_of_delta`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wind_data`
--

LOCK TABLES `wind_data` WRITE;
/*!40000 ALTER TABLE `wind_data` DISABLE KEYS */;
INSERT INTO `wind_data` VALUES ('17:12:00','17:12:05',7,10,5),('17:12:10','17:12:15',59,61,57),('17:12:21','17:12:26',17,26,7),('17:12:32','17:12:37',66,102,28),('17:12:43','17:12:48',66,70,63),('17:12:54','17:12:59',23,23,23),('17:13:05','17:13:10',23,23,23),('17:13:16','17:13:21',22,35,9),('17:13:26','17:13:31',43,50,34),('17:13:37','17:13:42',4,8,0),('17:13:48','17:13:53',13,29,0);
/*!40000 ALTER TABLE `wind_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wind_speeds`
--

DROP TABLE IF EXISTS `wind_speeds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wind_speeds` (
  `rtime` time NOT NULL,
  `wind_speed` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`rtime`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wind_speeds`
--

LOCK TABLES `wind_speeds` WRITE;
/*!40000 ALTER TABLE `wind_speeds` DISABLE KEYS */;
INSERT INTO `wind_speeds` VALUES ('17:11:56',1),('17:11:58',5),('17:12:00',5),('17:12:02',5),('17:12:05',10),('17:12:07',26),('17:12:09',43),('17:12:11',57),('17:12:13',61),('17:12:15',59),('17:12:18',50),('17:12:20',39),('17:12:22',26),('17:12:24',19),('17:12:26',7),('17:12:28',4),('17:12:31',18),('17:12:33',28),('17:12:35',69),('17:12:37',102),('17:12:39',90),('17:12:42',90),('17:12:44',70),('17:12:46',65),('17:12:48',63),('17:12:50',58),('17:12:53',36),('17:12:55',23),('17:12:57',23),('17:12:59',23),('17:13:01',23),('17:13:03',23),('17:13:06',23),('17:13:08',23),('17:13:10',23),('17:13:12',23),('17:13:14',23),('17:13:16',23),('17:13:19',9),('17:13:21',35),('17:13:23',31),('17:13:25',14),('17:13:27',45),('17:13:29',50),('17:13:31',34),('17:13:34',28),('17:13:36',16),('17:13:38',0),('17:13:40',4),('17:13:42',8),('17:13:45',11),('17:13:47',27),('17:13:49',29),('17:13:51',12),('17:13:53',0),('17:13:55',0),('17:13:57',0);
/*!40000 ALTER TABLE `wind_speeds` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-05-12 17:17:34
