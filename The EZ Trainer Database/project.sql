CREATE DATABASE  IF NOT EXISTS `ieor215_project` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `ieor215_project`;
-- MySQL dump 10.13  Distrib 8.0.38, for macos14 (x86_64)
--
-- Host: localhost    Database: ieor215_project
-- ------------------------------------------------------
-- Server version	9.0.1

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
-- Table structure for table `Employee`
--

DROP TABLE IF EXISTS `Employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Employee` (
  `Employee_ID` int NOT NULL,
  `Person_ID` int DEFAULT NULL,
  `Role_ID` int DEFAULT NULL,
  `Pay_rate` decimal(10,2) DEFAULT NULL,
  `Date_of_joining` date DEFAULT NULL,
  `Employment_type` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`Employee_ID`),
  KEY `Person_ID` (`Person_ID`),
  KEY `Role_ID` (`Role_ID`),
  CONSTRAINT `employee_ibfk_1` FOREIGN KEY (`Person_ID`) REFERENCES `Individual` (`Person_ID`),
  CONSTRAINT `employee_ibfk_2` FOREIGN KEY (`Role_ID`) REFERENCES `Role` (`Role_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Employee`
--

LOCK TABLES `Employee` WRITE;
/*!40000 ALTER TABLE `Employee` DISABLE KEYS */;
INSERT INTO `Employee` VALUES (1,1,1,24.49,'2023-12-05','Contract'),(2,2,2,19.91,'2023-04-04','Full-Time'),(3,3,2,46.19,'2023-03-08','Contract'),(4,4,2,29.28,'2023-07-09','Part-Time'),(5,5,2,36.49,'2023-07-07','Contract'),(6,6,1,25.34,'2022-12-24','Contract'),(7,7,2,32.36,'2023-09-24','Part-Time'),(8,8,3,21.59,'2023-08-29','Contract'),(9,9,3,21.18,'2023-05-07','Contract'),(10,10,2,21.38,'2023-01-17','Full-Time'),(11,11,3,19.33,'2024-01-10','Full-Time'),(12,12,3,46.95,'2024-01-26','Full-Time'),(13,13,1,41.73,'2024-05-07','Part-Time'),(14,14,3,42.08,'2023-01-18','Contract'),(15,15,3,44.25,'2023-12-16','Part-Time'),(16,16,2,37.01,'2023-03-05','Full-Time'),(17,17,2,36.85,'2024-10-23','Part-Time'),(18,18,3,21.63,'2023-12-02','Part-Time'),(19,19,3,27.11,'2024-08-31','Full-Time'),(20,20,3,29.60,'2023-05-02','Part-Time'),(21,21,3,41.43,'2024-02-10','Contract'),(22,22,2,22.70,'2024-07-20','Part-Time'),(23,23,1,21.66,'2023-06-12','Contract'),(24,24,2,34.83,'2024-06-30','Full-Time'),(25,25,3,47.38,'2024-01-30','Contract'),(26,26,3,45.14,'2024-06-10','Part-Time'),(27,27,2,21.90,'2024-05-10','Full-Time'),(28,28,3,21.79,'2024-07-05','Contract'),(29,29,1,31.96,'2023-10-29','Full-Time'),(30,30,1,36.96,'2023-02-05','Full-Time'),(31,31,2,42.54,'2024-09-15','Contract'),(32,32,1,33.35,'2023-06-01','Full-Time'),(33,33,2,41.20,'2023-10-18','Full-Time'),(34,34,2,48.01,'2024-04-25','Part-Time'),(35,35,3,33.95,'2022-12-10','Part-Time'),(36,36,2,19.31,'2023-07-17','Full-Time'),(37,37,3,28.22,'2023-02-14','Full-Time'),(38,38,2,31.23,'2022-12-25','Contract'),(39,39,2,35.42,'2023-05-23','Part-Time'),(40,40,1,26.87,'2023-12-31','Full-Time'),(41,41,2,29.16,'2024-06-03','Contract'),(42,42,2,42.56,'2023-06-14','Part-Time'),(43,43,1,35.88,'2023-06-10','Contract'),(44,44,2,27.86,'2024-07-09','Full-Time'),(45,45,2,25.42,'2024-01-29','Part-Time'),(46,46,2,42.67,'2023-03-07','Part-Time'),(47,47,2,43.82,'2024-07-08','Part-Time'),(48,48,2,39.98,'2023-06-29','Full-Time'),(49,49,2,20.43,'2024-06-30','Full-Time'),(50,50,1,30.16,'2024-06-17','Full-Time'),(51,51,2,33.55,'2023-02-09','Full-Time'),(52,52,1,39.11,'2023-04-06','Contract'),(53,53,1,40.63,'2023-05-01','Full-Time'),(54,54,1,33.05,'2024-01-10','Full-Time'),(55,55,2,24.40,'2024-12-02','Part-Time'),(56,56,1,33.65,'2024-03-16','Part-Time'),(57,57,1,26.82,'2024-04-13','Part-Time'),(58,58,1,25.36,'2023-12-19','Part-Time'),(59,59,3,40.19,'2023-11-12','Full-Time'),(60,60,3,22.40,'2023-10-26','Part-Time'),(61,61,1,34.24,'2023-10-14','Full-Time'),(62,62,3,27.15,'2023-10-04','Contract'),(63,63,3,48.53,'2024-09-07','Full-Time'),(64,64,3,21.21,'2023-10-31','Part-Time'),(65,65,1,18.44,'2023-02-19','Contract'),(66,66,1,26.21,'2022-12-12','Full-Time'),(67,67,2,42.21,'2023-05-31','Part-Time'),(68,68,1,25.53,'2024-06-02','Full-Time'),(69,69,2,39.12,'2023-05-07','Part-Time'),(70,70,2,18.25,'2024-08-12','Contract'),(71,71,2,19.08,'2023-06-04','Part-Time'),(72,72,1,42.19,'2024-06-20','Part-Time'),(73,73,2,29.62,'2024-05-17','Part-Time'),(74,74,3,35.80,'2024-05-19','Contract'),(75,75,2,18.08,'2024-06-18','Part-Time'),(76,76,2,39.68,'2023-10-08','Part-Time'),(77,77,1,40.96,'2024-07-27','Full-Time'),(78,78,3,30.75,'2024-11-02','Full-Time'),(79,79,2,24.99,'2024-06-28','Part-Time'),(80,80,2,44.53,'2024-06-19','Contract'),(81,81,2,27.09,'2024-08-20','Contract'),(82,82,1,27.59,'2024-11-22','Contract'),(83,83,3,26.76,'2023-09-08','Part-Time'),(84,84,3,41.33,'2024-07-06','Part-Time'),(85,85,2,21.06,'2022-12-04','Full-Time'),(86,86,1,39.98,'2024-05-07','Part-Time'),(87,87,1,48.33,'2023-06-26','Full-Time'),(88,88,1,40.66,'2024-03-08','Contract'),(89,89,2,42.47,'2024-01-21','Full-Time'),(90,90,1,48.71,'2023-03-31','Part-Time'),(91,91,3,18.23,'2023-05-06','Full-Time'),(92,92,1,19.46,'2023-03-06','Full-Time'),(93,93,3,44.07,'2023-01-24','Part-Time'),(94,94,3,39.33,'2024-02-25','Contract'),(95,95,1,35.63,'2023-07-18','Contract'),(96,96,1,20.69,'2023-11-07','Contract'),(97,97,1,20.33,'2023-07-27','Contract'),(98,98,3,33.24,'2023-06-28','Part-Time'),(99,99,1,42.51,'2023-09-26','Full-Time'),(100,100,2,25.21,'2023-04-30','Part-Time'),(101,101,2,48.30,'2023-06-04','Part-Time'),(102,102,1,48.13,'2023-09-24','Contract'),(103,103,1,31.44,'2023-07-28','Part-Time'),(104,104,2,26.18,'2023-09-17','Part-Time'),(105,105,1,19.88,'2024-10-20','Contract'),(106,106,3,46.34,'2024-07-08','Full-Time'),(107,107,2,27.42,'2024-05-06','Full-Time'),(108,108,1,26.82,'2023-06-25','Part-Time'),(109,109,1,33.06,'2023-12-06','Part-Time'),(110,110,3,21.65,'2023-12-05','Contract'),(111,111,3,27.90,'2023-09-07','Part-Time'),(112,112,3,42.60,'2023-02-24','Part-Time'),(113,113,2,36.89,'2023-10-16','Part-Time'),(114,114,1,24.18,'2023-06-04','Part-Time'),(115,115,3,42.41,'2024-06-10','Part-Time'),(116,116,2,49.31,'2024-02-15','Contract'),(117,117,3,30.61,'2023-04-12','Full-Time'),(118,118,1,26.16,'2024-01-02','Full-Time'),(119,119,1,35.99,'2024-04-09','Full-Time'),(120,120,3,41.01,'2024-09-10','Contract'),(121,121,2,28.86,'2023-08-27','Part-Time'),(122,122,2,27.07,'2024-09-22','Full-Time'),(123,123,1,43.69,'2023-03-11','Contract'),(124,124,1,39.45,'2024-02-12','Part-Time'),(125,125,3,22.13,'2023-09-02','Full-Time'),(126,126,1,24.40,'2023-08-13','Part-Time'),(127,127,1,27.46,'2024-07-18','Full-Time'),(128,128,3,40.73,'2024-03-22','Part-Time'),(129,129,2,40.19,'2024-08-31','Full-Time'),(130,130,3,42.02,'2024-09-11','Contract'),(131,131,1,49.59,'2023-04-30','Part-Time'),(132,132,2,38.67,'2023-02-10','Part-Time'),(133,133,1,28.71,'2023-09-24','Full-Time'),(134,134,2,26.86,'2024-03-31','Contract'),(135,135,3,34.07,'2023-03-08','Part-Time'),(136,136,1,21.54,'2023-09-26','Full-Time'),(137,137,2,43.74,'2024-06-03','Contract'),(138,138,3,44.85,'2023-10-03','Contract'),(139,139,3,22.63,'2023-02-27','Contract'),(140,140,1,43.15,'2023-09-06','Part-Time'),(141,141,1,25.12,'2024-10-24','Part-Time'),(142,142,1,47.22,'2024-09-06','Full-Time'),(143,143,1,20.30,'2024-01-11','Part-Time'),(144,144,1,41.97,'2024-10-27','Full-Time'),(145,145,2,47.49,'2023-06-13','Contract'),(146,146,1,25.94,'2023-02-04','Contract'),(147,147,2,24.34,'2023-02-14','Full-Time'),(148,148,3,49.16,'2023-10-21','Contract'),(149,149,2,21.28,'2023-07-09','Part-Time'),(150,150,1,40.75,'2022-12-12','Part-Time'),(151,151,3,24.55,'2023-09-17','Full-Time'),(152,152,1,22.87,'2024-08-17','Contract'),(153,153,1,34.34,'2024-11-03','Full-Time'),(154,154,3,28.97,'2023-09-25','Contract'),(155,155,2,44.25,'2023-09-16','Contract'),(156,156,3,27.49,'2023-10-04','Contract'),(157,157,3,34.33,'2024-06-26','Full-Time'),(158,158,2,34.10,'2022-12-19','Contract'),(159,159,3,49.85,'2023-08-18','Contract'),(160,160,2,41.43,'2024-08-27','Contract'),(161,161,2,28.35,'2024-10-22','Part-Time'),(162,162,3,36.06,'2024-05-23','Full-Time'),(163,163,3,39.83,'2024-01-02','Full-Time'),(164,164,3,23.63,'2023-07-20','Contract'),(165,165,3,39.22,'2024-01-15','Full-Time'),(166,166,3,32.37,'2024-11-27','Full-Time'),(167,167,2,49.54,'2024-01-09','Full-Time'),(168,168,2,24.23,'2024-03-09','Full-Time'),(169,169,2,27.53,'2024-04-30','Contract'),(170,170,2,25.40,'2024-01-31','Part-Time'),(171,171,1,47.24,'2024-09-20','Part-Time'),(172,172,1,43.57,'2024-08-18','Contract'),(173,173,1,27.68,'2023-09-24','Contract'),(174,174,3,26.94,'2024-05-01','Full-Time'),(175,175,2,28.88,'2023-09-24','Full-Time'),(176,176,3,22.92,'2023-04-17','Part-Time'),(177,177,1,45.52,'2023-02-16','Contract'),(178,178,2,34.00,'2024-05-30','Full-Time'),(179,179,3,28.69,'2024-01-20','Part-Time'),(180,180,3,36.50,'2024-08-04','Contract'),(181,181,2,31.08,'2023-10-03','Contract'),(182,182,1,26.40,'2024-09-08','Full-Time'),(183,183,1,42.11,'2024-04-24','Contract'),(184,184,2,19.52,'2024-08-18','Full-Time'),(185,185,1,25.39,'2023-03-20','Full-Time'),(186,186,1,46.94,'2024-06-15','Part-Time'),(187,187,3,44.17,'2023-12-10','Part-Time'),(188,188,1,28.42,'2024-04-08','Contract'),(189,189,1,33.09,'2024-11-28','Contract'),(190,190,3,23.66,'2023-01-16','Contract'),(191,191,2,32.55,'2023-02-01','Part-Time'),(192,192,2,36.34,'2024-11-25','Contract'),(193,193,1,27.33,'2023-06-11','Contract'),(194,194,3,19.96,'2023-09-11','Part-Time'),(195,195,2,49.89,'2024-09-16','Part-Time'),(196,196,1,22.33,'2023-07-17','Contract'),(197,197,3,33.73,'2024-08-13','Contract'),(198,198,3,38.23,'2024-02-28','Full-Time'),(199,199,1,35.23,'2023-10-07','Part-Time'),(200,200,1,44.51,'2023-09-12','Part-Time');
/*!40000 ALTER TABLE `Employee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Employee_Role`
--

DROP TABLE IF EXISTS `Employee_Role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Employee_Role` (
  `Employee_ID` int NOT NULL,
  `Role_ID` int NOT NULL,
  PRIMARY KEY (`Employee_ID`,`Role_ID`),
  KEY `Role_ID` (`Role_ID`),
  CONSTRAINT `employee_role_ibfk_1` FOREIGN KEY (`Employee_ID`) REFERENCES `Employee` (`Employee_ID`),
  CONSTRAINT `employee_role_ibfk_2` FOREIGN KEY (`Role_ID`) REFERENCES `Role` (`Role_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Employee_Role`
--

LOCK TABLES `Employee_Role` WRITE;
/*!40000 ALTER TABLE `Employee_Role` DISABLE KEYS */;
/*!40000 ALTER TABLE `Employee_Role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Exercise`
--

DROP TABLE IF EXISTS `Exercise`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Exercise` (
  `Exercise_ID` int NOT NULL,
  `Workout_ID` int DEFAULT NULL,
  `Name` varchar(50) DEFAULT NULL,
  `Schedule` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Exercise_ID`),
  KEY `Workout_ID` (`Workout_ID`),
  CONSTRAINT `exercise_ibfk_1` FOREIGN KEY (`Workout_ID`) REFERENCES `Workout_Session` (`Workout_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Exercise`
--

LOCK TABLES `Exercise` WRITE;
/*!40000 ALTER TABLE `Exercise` DISABLE KEYS */;
/*!40000 ALTER TABLE `Exercise` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Group_Trainer`
--

DROP TABLE IF EXISTS `Group_Trainer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Group_Trainer` (
  `Employee_ID` int NOT NULL,
  `Certification` varchar(100) DEFAULT NULL,
  `Specialization` varchar(100) DEFAULT NULL,
  `Rating` decimal(3,2) DEFAULT NULL,
  PRIMARY KEY (`Employee_ID`),
  CONSTRAINT `group_trainer_ibfk_1` FOREIGN KEY (`Employee_ID`) REFERENCES `Employee` (`Employee_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Group_Trainer`
--

LOCK TABLES `Group_Trainer` WRITE;
/*!40000 ALTER TABLE `Group_Trainer` DISABLE KEYS */;
/*!40000 ALTER TABLE `Group_Trainer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Group_Trainer_Conducts_Workout_Session`
--

DROP TABLE IF EXISTS `Group_Trainer_Conducts_Workout_Session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Group_Trainer_Conducts_Workout_Session` (
  `Employee_ID` int NOT NULL,
  `Workout_ID` int NOT NULL,
  PRIMARY KEY (`Employee_ID`,`Workout_ID`),
  KEY `Workout_ID` (`Workout_ID`),
  CONSTRAINT `group_trainer_conducts_workout_session_ibfk_1` FOREIGN KEY (`Employee_ID`) REFERENCES `Group_Trainer` (`Employee_ID`),
  CONSTRAINT `group_trainer_conducts_workout_session_ibfk_2` FOREIGN KEY (`Workout_ID`) REFERENCES `Workout_Session` (`Workout_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Group_Trainer_Conducts_Workout_Session`
--

LOCK TABLES `Group_Trainer_Conducts_Workout_Session` WRITE;
/*!40000 ALTER TABLE `Group_Trainer_Conducts_Workout_Session` DISABLE KEYS */;
/*!40000 ALTER TABLE `Group_Trainer_Conducts_Workout_Session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Individual`
--

DROP TABLE IF EXISTS `Individual`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Individual` (
  `Person_ID` int NOT NULL,
  `First_name` varchar(50) DEFAULT NULL,
  `MI` char(1) DEFAULT NULL,
  `Last_name` varchar(50) DEFAULT NULL,
  `Age` int DEFAULT NULL,
  `Phone` varchar(15) DEFAULT NULL,
  `Sex` char(1) DEFAULT NULL,
  PRIMARY KEY (`Person_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Individual`
--

LOCK TABLES `Individual` WRITE;
/*!40000 ALTER TABLE `Individual` DISABLE KEYS */;
INSERT INTO `Individual` VALUES (1,'Sara','E','Norquoy',13,'653-260-6638',NULL),(2,'Greggory','Y','Benam',6,'116-351-2287',NULL),(3,'Sasha','B','Maffulli',15,'642-405-1304',NULL),(4,'Chandler','R','Linwood',26,'897-190-5308',NULL),(5,'Doralyn','I','Carrier',38,'812-516-7101',NULL),(6,'Renate','F','Kohlerman',34,'387-318-0599',NULL),(7,'Latashia','U','Bohin',23,'827-977-1726',NULL),(8,'Barton','E','McTeggart',18,'939-827-9780',NULL),(9,'Nicholle','Q','Copp',34,'301-100-2674',NULL),(10,'Tan','F','Rea',35,'909-344-7672',NULL),(11,'Dominic','O','Caudelier',33,'342-441-5874',NULL),(12,'Kristofor','F','Longbottom',3,'765-558-3571',NULL),(13,'Sascha','N','Mansell',26,'601-880-4965',NULL),(14,'Doralynn','Q','Comer',15,'654-343-6189',NULL),(15,'Nikki','S','Weathers',7,'791-361-6571',NULL),(16,'Antonella','H','Bladge',16,'260-730-3325',NULL),(17,'Lolly','K','Dunley',4,'327-462-2809',NULL),(18,'Dina','X','Popescu',3,'363-305-0348',NULL),(19,'Laurie','C','Jantel',29,'305-608-5631',NULL),(20,'Welbie','N','Cuolahan',27,'312-959-6254',NULL),(21,'Cherin','F','Bowskill',25,'433-302-9964',NULL),(22,'Lynne','T','Sowerbutts',29,'333-635-0913',NULL),(23,'Willabella','J','Alleburton',37,'230-918-4649',NULL),(24,'Normand','O','Heinsen',18,'132-582-5136',NULL),(25,'Abraham','V','Pasquale',26,'675-744-0129',NULL),(26,'Kayne','R','Doneld',1,'840-443-7785',NULL),(27,'Mia','J','Lecount',5,'463-128-9498',NULL),(28,'Carolynn','X','Argrave',27,'783-393-9297',NULL),(29,'Reginauld','Q','Lube',24,'905-126-1123',NULL),(30,'Berny','G','Izakoff',31,'114-265-2926',NULL),(31,'Eugenio','D','Postgate',22,'364-137-2063',NULL),(32,'Sherilyn','B','Stitch',9,'177-197-7274',NULL),(33,'Nelie','X','Nasi',11,'153-426-6846',NULL),(34,'Pierrette','T','Tomasello',29,'301-200-9493',NULL),(35,'Lancelot','Y','Saket',17,'717-976-3766',NULL),(36,'Bobbie','Z','Winchurch',33,'490-754-3921',NULL),(37,'Ferdinand','U','Churches',40,'442-331-4853',NULL),(38,'Winfred','G','Gimeno',8,'559-936-5613',NULL),(39,'Corrie','F','Zannetti',7,'382-822-4953',NULL),(40,'Bronnie','K','Carress',33,'247-946-6935',NULL),(41,'Ulrike','P','Hillyatt',31,'714-673-4824',NULL),(42,'Bar','Q','Rand',6,'330-940-3843',NULL),(43,'Glenden','Z','O\'Kieran',8,'732-435-0078',NULL),(44,'Lindi','W','Stallan',40,'224-867-4336',NULL),(45,'Mehetabel','R','Bleibaum',28,'187-963-7929',NULL),(46,'Neel','U','Jarry',3,'518-959-6032',NULL),(47,'Shayna','H','Haster',34,'372-460-8313',NULL),(48,'Kelsey','M','Borrington',13,'611-976-1436',NULL),(49,'Orelee','V','Goldstraw',40,'296-585-3638',NULL),(50,'Renaldo','S','Stearndale',18,'664-550-9772',NULL),(51,'Irene','N','Grishukhin',24,'113-178-6688',NULL),(52,'Suzanne','M','Bayley',11,'384-486-2550',NULL),(53,'Ingmar','L','Frick',35,'910-749-8031',NULL),(54,'Rufe','T','Silvester',26,'168-489-0603',NULL),(55,'Guinevere','F','Bascombe',26,'258-358-6549',NULL),(56,'Allene','J','Gentil',36,'446-115-4107',NULL),(57,'Claudius','X','Furby',2,'145-270-8671',NULL),(58,'Dido','E','Eglese',5,'368-361-7968',NULL),(59,'Wright','N','Meach',22,'603-347-1136',NULL),(60,'Rabi','Z','Fellgatt',31,'206-236-9229',NULL),(61,'Rosaleen','L','Gain',25,'491-223-0800',NULL),(62,'Jonathon','Y','Demelt',14,'483-790-4861',NULL),(63,'Beau','Q','Summerbell',12,'822-170-4658',NULL),(64,'Sonnnie','W','Bafford',18,'688-993-3097',NULL),(65,'Samuel','C','Self',24,'424-642-0446',NULL),(66,'Ernesta','L','Longhorn',32,'889-511-3022',NULL),(67,'Clementius','J','O\'Hogertie',1,'765-619-4140',NULL),(68,'Alexa','D','Lorraine',40,'337-209-2063',NULL),(69,'Leonidas','I','McIlrath',38,'971-559-9105',NULL),(70,'Shaun','H','Schowenburg',40,'153-333-4390',NULL),(71,'Davidde','Z','Libby',11,'946-651-3435',NULL),(72,'Bernette','Q','Salvadori',7,'645-923-8110',NULL),(73,'Cissy','T','Whewill',15,'383-472-8575',NULL),(74,'Eliza','B','Grishenkov',11,'897-220-3645',NULL),(75,'Raquela','Q','Dykins',1,'726-461-7290',NULL),(76,'Candra','M','Woodus',8,'825-251-5399',NULL),(77,'Karee','T','Zuenelli',32,'806-646-3163',NULL),(78,'Dyanne','Q','Mackie',30,'965-904-7364',NULL),(79,'Clark','E','Mallya',4,'754-614-9723',NULL),(80,'Francesca','I','Parlet',13,'485-352-0811',NULL),(81,'Sybil','K','Heavyside',26,'566-593-0088',NULL),(82,'Cord','T','Immings',38,'188-465-6468',NULL),(83,'Elwood','B','Bosson',30,'472-801-7507',NULL),(84,'Granger','Q','Baughn',21,'761-112-8456',NULL),(85,'Brig','Z','Buxey',4,'562-689-3581',NULL),(86,'Clay','S','Nana',13,'714-653-4244',NULL),(87,'Kimbra','I','Horsell',26,'316-982-2822',NULL),(88,'Susannah','K','Foxon',25,'287-673-1589',NULL),(89,'Marin','H','Bellie',11,'274-279-8803',NULL),(90,'Aubrie','V','Seale',1,'240-163-9522',NULL),(91,'Simmonds','O','Ridgway',21,'355-133-5999',NULL),(92,'Malinde','L','Roseborough',25,'252-127-1372',NULL),(93,'Berti','W','Bolstridge',29,'869-482-7183',NULL),(94,'Mitzi','D','Umpleby',31,'549-839-6295',NULL),(95,'Gray','F','Bairnsfather',38,'650-661-1256',NULL),(96,'Orton','X','Rubinivitz',36,'568-109-8512',NULL),(97,'Camala','G','Tomicki',38,'845-211-9334',NULL),(98,'Tammy','V','Minithorpe',3,'155-944-0227',NULL),(99,'Linn','Q','Rassell',13,'293-459-3336',NULL),(100,'Cosetta','V','De Wolfe',24,'689-912-5796',NULL),(101,'Sig','R','Maken',8,'297-837-2809',NULL),(102,'Marijo','H','Dameisele',8,'189-554-3229',NULL),(103,'Floyd','M','Stoakes',18,'538-505-1126',NULL),(104,'Gerta','I','Rosel',23,'706-665-0596',NULL),(105,'Elvera','W','Lumsdaine',6,'852-203-7398',NULL),(106,'Maura','R','Scoggans',27,'306-793-0939',NULL),(107,'Margo','N','Dury',16,'778-646-9648',NULL),(108,'Christoper','X','Gorhardt',16,'831-647-0612',NULL),(109,'Abagail','N','Barkley',18,'173-677-7562',NULL),(110,'Nancy','Z','Younie',38,'610-433-1064',NULL),(111,'Udall','L','Bickerdicke',38,'437-566-4152',NULL),(112,'Nerissa','B','Butner',19,'702-171-0004',NULL),(113,'Benjy','K','Kelcher',30,'276-653-9810',NULL),(114,'Hedy','M','Seaking',40,'716-700-0999',NULL),(115,'Neysa','W','Cayley',32,'600-456-3970',NULL),(116,'Julie','Z','Vedenyakin',30,'353-147-1565',NULL),(117,'Linet','F','Fountain',18,'656-222-6579',NULL),(118,'Rozalie','B','Morgan',16,'154-864-5353',NULL),(119,'North','K','Whiteoak',36,'860-484-3074',NULL),(120,'Anna-maria','L','Dolder',34,'945-694-9635',NULL),(121,'Ashil','B','Blonfield',32,'277-188-0654',NULL),(122,'Rubina','G','Claxton',11,'359-772-1564',NULL),(123,'Fawnia','G','Putman',6,'100-266-3768',NULL),(124,'Zacharias','S','Whitebrook',21,'308-294-5512',NULL),(125,'Carley','R','Peron',2,'667-132-3015',NULL),(126,'Drucill','E','Easby',7,'630-672-8955',NULL),(127,'Bil','A','Bernt',19,'351-646-7998',NULL),(128,'Howard','Q','Kovalski',5,'485-214-0334',NULL),(129,'August','Y','Parkeson',21,'544-653-7578',NULL),(130,'Leilah','K','Celes',8,'903-671-9542',NULL),(131,'Paige','B','Barkworth',8,'445-980-2309',NULL),(132,'Chaunce','L','Bumphries',4,'600-263-3187',NULL),(133,'Sarena','L','Downes',34,'793-378-3018',NULL),(134,'Collette','M','Paddon',12,'864-162-0080',NULL),(135,'Goraud','J','Jaquemar',38,'800-791-8464',NULL),(136,'Milka','C','Scholler',26,'607-877-0507',NULL),(137,'Durand','T','Pomery',18,'775-359-0290',NULL),(138,'Natalee','P','Headford',12,'139-517-4831',NULL),(139,'Knox','N','Valerius',12,'407-119-5182',NULL),(140,'Kory','E','Khadir',19,'390-725-6742',NULL),(141,'Giacinta','U','Biffen',21,'658-237-2122',NULL),(142,'Tania','K','Scorah',16,'651-178-2122',NULL),(143,'Tiffy','M','Palluschek',19,'432-882-7319',NULL),(144,'Trever','R','Durbyn',11,'193-243-3569',NULL),(145,'Ilyse','G','Vida',5,'145-598-4558',NULL),(146,'Ibbie','T','Guilloton',21,'464-226-2471',NULL),(147,'Ardath','M','Malyon',6,'553-543-6834',NULL),(148,'Rowland','T','Alexsandrovich',28,'213-854-5742',NULL),(149,'Raphaela','K','Smithyman',12,'716-550-2564',NULL),(150,'Mia','G','Richter',14,'116-562-7650',NULL),(151,'Seka','U','Pesik',12,'715-710-5006',NULL),(152,'Tessie','Y','Darlington',22,'255-869-4869',NULL),(153,'Olive','D','Rissen',6,'997-344-1925',NULL),(154,'Gawen','O','Stegers',10,'294-532-7899',NULL),(155,'Prudi','Q','Zanicchi',13,'288-835-2178',NULL),(156,'Brynn','N','Alderwick',15,'554-511-6213',NULL),(157,'Jamaal','Y','Dows',25,'791-447-2287',NULL),(158,'Glenn','F','Loreit',23,'857-103-2968',NULL),(159,'Elenore','F','Kellitt',29,'471-401-5821',NULL),(160,'Hazel','X','Blazic',19,'201-908-4518',NULL),(161,'Jehanna','S','Castellanos',24,'369-995-3238',NULL),(162,'Joly','H','Shelmerdine',24,'579-639-7959',NULL),(163,'Haily','V','Mayger',37,'837-290-7188',NULL),(164,'Leann','R','Adel',31,'389-765-2251',NULL),(165,'Carmel','O','Tiller',22,'857-594-1137',NULL),(166,'Gerald','L','Swarbrick',25,'296-964-8568',NULL),(167,'Edna','A','Rounsefell',9,'988-961-7971',NULL),(168,'Dorey','Q','Crossfeld',29,'578-868-1093',NULL),(169,'Leonore','G','Hallawell',33,'275-152-5904',NULL),(170,'Yurik','Y','MacAllester',14,'393-814-5877',NULL),(171,'Garreth','T','Le land',38,'328-871-6612',NULL),(172,'Noach','D','Ajean',20,'265-403-1987',NULL),(173,'Shannon','D','Pirson',26,'352-654-3724',NULL),(174,'Viv','F','Graal',4,'750-123-4999',NULL),(175,'Wallas','J','Plose',16,'571-122-8751',NULL),(176,'Lanie','J','Vickors',30,'512-653-4727',NULL),(177,'Jeremy','F','Skellen',4,'589-708-3912',NULL),(178,'Olenka','N','MacMakin',10,'763-963-5371',NULL),(179,'Zuzana','S','Haggas',34,'120-334-4602',NULL),(180,'Freddy','D','Lake',4,'689-133-1145',NULL),(181,'Nedda','O','Callar',4,'974-531-7520',NULL),(182,'Jenilee','T','Grene',17,'923-892-6453',NULL),(183,'Iorgos','O','Linfitt',13,'341-299-7511',NULL),(184,'Sandy','J','Yellop',3,'561-526-2930',NULL),(185,'Brittni','G','Tyrwhitt',18,'779-770-9431',NULL),(186,'Jere','M','Gepheart',6,'931-556-7209',NULL),(187,'Elfrieda','P','Jeayes',36,'386-558-9552',NULL),(188,'Tish','G','Ketchaside',29,'890-666-8970',NULL),(189,'Rheba','G','McDugal',24,'731-668-9580',NULL),(190,'Ervin','D','Wiszniewski',10,'491-689-3401',NULL),(191,'Stormy','L','Mulran',17,'769-199-0221',NULL),(192,'Minna','B','Eacle',29,'368-249-0841',NULL),(193,'Emmye','T','Burge',11,'249-922-4184',NULL),(194,'Mendel','R','Daykin',9,'529-619-0191',NULL),(195,'Maddy','B','Selliman',20,'528-654-5078',NULL),(196,'Doug','T','Hellier',6,'169-380-1516',NULL),(197,'Bab','Y','Foxton',12,'864-685-5965',NULL),(198,'Joby','C','Kermit',37,'765-662-4866',NULL),(199,'Georgette','R','Threadgall',40,'880-198-3748',NULL),(200,'Regen','X','Neicho',14,'698-917-7927',NULL),(201,'Moyna','A','Trainor',36,'380-514-4687',NULL),(202,'Marcellina','L','Fonzone',12,'517-768-9671',NULL),(203,'Marena','C','Garrat',5,'464-112-4816',NULL),(204,'Even','B','Squibb',8,'712-926-4965',NULL),(205,'Inesita','X','Camilletti',12,'577-960-0997',NULL),(206,'Xenia','C','Cantrell',31,'627-734-1396',NULL),(207,'Duffy','K','Mc Gorley',2,'304-973-9931',NULL),(208,'Quintana','N','Tilzey',8,'587-530-2496',NULL),(209,'Ange','N','Harner',22,'179-453-5057',NULL),(210,'Clair','E','Ahrendsen',15,'383-169-6483',NULL),(211,'Cloe','Z','Fike',32,'109-674-7202',NULL),(212,'Ashlen','M','Olyet',21,'429-159-7812',NULL),(213,'Saloma','L','Miranda',2,'116-904-5075',NULL),(214,'Lesya','Q','Jindra',31,'588-663-4971',NULL),(215,'Constantia','F','Fuentez',38,'896-562-8088',NULL),(216,'Harland','U','Henric',14,'226-555-2943',NULL),(217,'Kay','Z','Huckin',32,'864-492-3418',NULL),(218,'Dorris','O','Chevis',18,'816-251-1783',NULL),(219,'Dimitri','T','Whatson',4,'361-209-1978',NULL),(220,'Petrina','C','Crowther',24,'841-530-5293',NULL),(221,'Chen','X','Benjafield',35,'674-655-2618',NULL),(222,'Glenna','F','Santus',34,'522-115-8601',NULL),(223,'Harli','Q','Vossgen',5,'491-185-4876',NULL),(224,'Faulkner','K','Lebel',11,'833-394-6436',NULL),(225,'Guenna','K','Happel',16,'264-562-1375',NULL),(226,'Dudley','M','Durtnall',21,'482-614-0481',NULL),(227,'Mona','X','Sokell',39,'854-473-7931',NULL),(228,'Ayn','X','Nichol',20,'318-449-5336',NULL),(229,'Marcello','Y','Petraitis',31,'809-361-6029',NULL),(230,'Josefina','C','Dodshon',12,'183-637-6458',NULL),(231,'Angelita','H','Stenning',23,'329-430-6928',NULL),(232,'Harri','S','Connechy',20,'637-640-8658',NULL),(233,'Mufi','E','Gilham',2,'949-671-3151',NULL),(234,'Dorice','X','Grigson',31,'218-464-6025',NULL),(235,'Ulick','Y','Ticehurst',38,'585-862-5216',NULL),(236,'Boone','D','Abelson',29,'769-457-8170',NULL),(237,'Emile','G','Cornejo',12,'177-133-8754',NULL),(238,'Jasun','W','Hauxby',1,'508-707-2087',NULL),(239,'Rosalynd','X','Reside',25,'641-752-7924',NULL),(240,'Annette','W','Boot',10,'237-168-3465',NULL),(241,'Brooke','D','Matteo',8,'199-415-4672',NULL),(242,'Elsi','C','Metzig',13,'698-489-0964',NULL),(243,'Alric','O','Goldhill',29,'473-756-3552',NULL),(244,'Edward','R','Siggins',3,'930-507-1967',NULL),(245,'Hewie','M','Slewcock',12,'461-943-5337',NULL),(246,'Agretha','U','Thornber',31,'713-276-4469',NULL),(247,'Keslie','X','Davy',16,'512-362-0135',NULL),(248,'Marion','W','Marchent',35,'337-185-7135',NULL),(249,'Rivi','N','McLachlan',19,'989-576-5754',NULL),(250,'Maddie','U','Durgan',28,'952-914-8636',NULL),(251,'Toni','Z','Dibden',16,'877-865-9672',NULL),(252,'Lay','U','Marven',1,'347-446-9903',NULL),(253,'Willetta','J','Coniff',39,'283-961-9086',NULL),(254,'Paige','B','Bartleet',16,'704-989-5043',NULL),(255,'Horatia','T','Tamsett',1,'834-137-5951',NULL),(256,'Jamesy','P','Grgic',16,'885-737-4429',NULL),(257,'Colin','R','Taunton',9,'434-395-5394',NULL),(258,'Dorris','Z','Ginnety',26,'643-543-3408',NULL),(259,'Patrick','X','Rosi',38,'586-306-6306',NULL),(260,'Calli','Y','Boyda',15,'541-101-2631',NULL),(261,'Corine','Q','Robbins',7,'800-402-6190',NULL),(262,'Jeremie','X','Gelling',28,'107-391-7041',NULL),(263,'Kelbee','N','Parnham',39,'633-396-1652',NULL),(264,'Dickie','V','Aspin',32,'839-384-4823',NULL),(265,'Gussie','D','Igo',29,'492-582-5597',NULL),(266,'Davon','S','Erett',29,'898-657-3311',NULL),(267,'Lennie','K','Bonder',20,'416-707-8381',NULL),(268,'Mala','N','Gallico',37,'654-853-1275',NULL),(269,'Bobbie','S','Youd',18,'560-914-1024',NULL),(270,'Rivi','K','Birtonshaw',13,'225-460-4303',NULL),(271,'Jena','K','Liddel',14,'572-735-3939',NULL),(272,'Emlyn','Q','Sonley',30,'628-497-8161',NULL),(273,'Beverlie','N','Caulcott',28,'320-799-4771',NULL),(274,'Frederique','V','Garlic',21,'387-737-2342',NULL),(275,'Neille','K','Diggin',1,'982-536-4912',NULL),(276,'Kylen','U','Pardew',22,'861-312-7596',NULL),(277,'Sissy','L','Tremblay',31,'419-945-4094',NULL),(278,'Perren','B','Drakers',3,'568-970-0667',NULL),(279,'Loni','I','Masey',3,'222-881-9715',NULL),(280,'Shirline','S','Whipp',26,'706-912-0443',NULL),(281,'Duffie','Y','Waterland',29,'529-831-3064',NULL),(282,'Alano','E','Tarbath',21,'526-930-2123',NULL),(283,'Joannes','A','Stenyng',38,'238-426-4442',NULL),(284,'Edd','R','Hischke',4,'402-357-3220',NULL),(285,'Ruthe','G','Connett',28,'603-806-3770',NULL),(286,'Ash','D','Dewire',21,'450-250-4312',NULL),(287,'Maridel','L','Graffin',27,'939-873-9093',NULL),(288,'Nickolai','E','Banbridge',38,'503-449-3082',NULL),(289,'Roscoe','T','Hatwells',36,'974-145-8115',NULL),(290,'Auroora','G','Pritty',20,'258-396-2487',NULL),(291,'Milli','R','Hallaways',19,'235-301-4322',NULL),(292,'Correna','O','Esland',34,'563-759-3271',NULL),(293,'Asia','G','Blitz',40,'782-221-0964',NULL),(294,'Emiline','C','Cornill',7,'509-150-0215',NULL),(295,'Alfred','B','Bourner',2,'323-530-0043',NULL),(296,'Karrah','E','Crates',22,'142-965-5923',NULL),(297,'Isahella','V','Jowers',8,'598-637-7903',NULL),(298,'Hagen','Q','Winsborrow',28,'967-674-8951',NULL),(299,'Norma','I','Vispo',13,'136-104-0345',NULL),(300,'Binny','Z','Stango',1,'567-140-3930',NULL),(301,'Inga','Z','Tommis',34,'281-499-9931',NULL),(302,'Dame','F','Setchfield',24,'360-129-3329',NULL),(303,'Tina','J','Larciere',23,'828-131-9269',NULL),(304,'Glenn','E','Bowdidge',37,'176-332-1947',NULL),(305,'Merrilee','Z','McGrady',16,'757-779-0862',NULL),(306,'Bettina','P','Andersson',22,'929-974-5036',NULL),(307,'Kizzie','G','Skews',28,'981-296-2011',NULL),(308,'Morry','L','Bawden',8,'298-849-7819',NULL),(309,'Rozanna','T','De Robertis',29,'843-490-8676',NULL),(310,'Caro','R','Gatheral',33,'158-663-2540',NULL),(311,'Nydia','Y','Roden',32,'396-670-3528',NULL),(312,'Ivan','B','Brydie',26,'628-881-9062',NULL),(313,'Alyce','E','Richly',15,'897-843-2903',NULL),(314,'Granville','U','Tarpey',4,'359-712-5093',NULL),(315,'Carr','L','Plank',20,'808-749-2107',NULL),(316,'Sibyl','Y','Nornasell',30,'218-247-3393',NULL),(317,'Doll','G','Clougher',32,'543-545-4395',NULL),(318,'Roseanna','D','Taborre',11,'884-494-3415',NULL),(319,'Mitch','W','Schuck',30,'778-296-5134',NULL),(320,'Cordell','Z','Claus',32,'136-712-1569',NULL),(321,'Roseline','F','Rulf',36,'759-174-1156',NULL),(322,'Octavia','O','Mac Geaney',36,'732-395-1426',NULL),(323,'Berri','M','Lishmund',15,'570-931-2283',NULL),(324,'Even','L','Quaintance',28,'888-398-7706',NULL),(325,'Collen','Y','Janoschek',18,'116-138-5172',NULL),(326,'Lexine','O','Lydiard',10,'440-889-3123',NULL),(327,'Phebe','G','Boal',3,'124-495-5614',NULL),(328,'Giralda','A','Behne',25,'892-530-5081',NULL),(329,'Charlotte','L','Morcom',33,'386-638-3441',NULL),(330,'Pat','P','Chelnam',38,'734-441-7954',NULL),(331,'Persis','X','Lapre',29,'879-694-5550',NULL),(332,'Grissel','B','Barrabeale',24,'345-431-9951',NULL),(333,'Priscella','G','Delph',5,'101-434-1154',NULL),(334,'Vania','Q','Folger',11,'914-460-5865',NULL),(335,'Gussy','W','Hassall',12,'347-598-8773',NULL),(336,'Isis','K','Bonnick',10,'407-398-2418',NULL),(337,'Joanna','X','Chapman',28,'192-695-8142',NULL),(338,'Llywellyn','P','Ganforth',18,'381-175-7741',NULL),(339,'Godard','D','Bratchell',12,'824-556-8221',NULL),(340,'Vanessa','G','Bayston',23,'274-902-8748',NULL),(341,'Alysa','T','Brunning',21,'532-614-2179',NULL),(342,'Philippa','V','Duffie',12,'353-134-5625',NULL),(343,'Forester','I','Berendsen',38,'451-840-4274',NULL),(344,'Rosmunda','X','Collaton',20,'534-749-4618',NULL),(345,'Charley','U','Mynett',16,'198-783-2898',NULL),(346,'Antin','K','Arton',29,'558-557-8188',NULL),(347,'Bibbie','T','Nancekivell',38,'424-715-4506',NULL),(348,'Wernher','U','Henkmann',37,'730-763-1276',NULL),(349,'Giacomo','W','D\'Abbot-Doyle',16,'107-884-7702',NULL),(350,'Broddy','K','Andrew',13,'400-982-4703',NULL),(351,'Bertie','E','Koppelmann',28,'278-531-9114',NULL),(352,'Athene','K','Stichall',12,'907-800-7940',NULL),(353,'Mari','Q','Hebburn',15,'646-220-7016',NULL),(354,'Hanni','Q','Maasz',1,'302-112-9782',NULL),(355,'Cally','A','Colling',4,'967-883-4437',NULL),(356,'Killian','K','Sabbatier',14,'744-888-7011',NULL),(357,'Shannah','E','Bennedick',27,'653-301-0451',NULL),(358,'Stanislaus','W','Huskinson',14,'408-861-1482',NULL),(359,'Evelin','Q','Mandrey',3,'564-167-6547',NULL),(360,'Ginger','U','Burgill',8,'110-630-5455',NULL),(361,'Leia','Q','Gravener',29,'865-198-0811',NULL),(362,'Jonathan','S','Stansell',23,'608-385-9033',NULL),(363,'Wernher','B','Stronghill',15,'848-544-7089',NULL),(364,'Thalia','T','Girodias',24,'748-132-1927',NULL),(365,'Putnem','B','Hull',26,'439-991-6821',NULL),(366,'Irv','Q','Josse',21,'963-425-5932',NULL),(367,'Nataniel','O','Ablitt',7,'890-693-1027',NULL),(368,'Janaye','Q','Halliwell',21,'609-922-9396',NULL),(369,'Pascale','V','Membry',11,'898-212-1746',NULL),(370,'Raphael','M','Reade',29,'156-345-6878',NULL),(371,'Retha','K','Calcott',18,'519-566-4522',NULL),(372,'Ekaterina','A','Crowdace',21,'945-377-9737',NULL),(373,'Abbot','G','Bigley',15,'567-477-1391',NULL),(374,'Merwin','W','Hansley',24,'414-198-1504',NULL),(375,'Micheil','H','McReath',36,'550-310-7149',NULL),(376,'Clemente','C','Bodsworth',37,'662-864-8628',NULL),(377,'Adel','Q','Phillis',27,'846-610-9708',NULL),(378,'Brigitta','C','Markushkin',27,'424-227-1193',NULL),(379,'Kevan','B','Kendle',33,'483-359-1029',NULL),(380,'Myer','Z','Gay',34,'937-729-1699',NULL),(381,'Ganny','G','Antonovic',34,'401-180-7536',NULL),(382,'Bruce','O','Klich',1,'133-342-7439',NULL),(383,'Aime','B','Andriuzzi',5,'862-549-9224',NULL),(384,'Fergus','M','Kroger',22,'576-948-4531',NULL),(385,'Joela','D','Tristram',23,'634-370-2017',NULL),(386,'Frederica','Q','Matveyev',2,'755-853-9078',NULL),(387,'Karin','W','Rosberg',28,'950-894-8102',NULL),(388,'Allene','Z','Oswick',30,'332-349-4450',NULL),(389,'Fergus','D','Maccrie',27,'830-810-0423',NULL),(390,'Desi','G','Padefield',14,'294-564-1089',NULL),(391,'Jessa','J','Axford',17,'813-764-0712',NULL),(392,'Carena','M','Partener',10,'984-270-9348',NULL),(393,'Wendall','Z','Hoyer',37,'474-731-4229',NULL),(394,'Broderic','J','Ahlf',5,'188-156-9048',NULL),(395,'Correna','K','Jonin',9,'116-254-4882',NULL),(396,'Jeannie','K','Durdy',26,'428-489-2595',NULL),(397,'Gerrie','K','Raymen',19,'651-629-6132',NULL),(398,'Gilbertine','A','Chaplin',19,'375-259-3625',NULL),(399,'Ashlen','V','Greenstock',32,'230-541-9623',NULL),(400,'Andrus','T','Corten',4,'219-376-3072',NULL),(401,'Malachi','G','Ecclestone',6,'200-599-6539',NULL),(402,'Margalit','P','Petican',9,'324-800-9444',NULL),(403,'Lillis','T','Yusupov',24,'864-371-6182',NULL),(404,'Delly','R','Coot',10,'461-192-1986',NULL),(405,'Lidia','C','Garrod',30,'777-620-9862',NULL),(406,'Lenna','R','Hookes',17,'735-397-5834',NULL),(407,'Jocelin','T','Ferrier',19,'660-112-7821',NULL),(408,'Georgia','H','Dorot',9,'910-656-6467',NULL),(409,'Leola','U','Tribbeck',31,'304-193-1059',NULL),(410,'Toddy','L','Battrum',36,'121-684-9927',NULL),(411,'Aurlie','Y','Kilgour',12,'798-931-0758',NULL),(412,'Verne','Q','Conring',10,'874-731-3307',NULL),(413,'Trenna','Y','Anthoin',7,'683-715-8714',NULL),(414,'Thekla','G','Teesdale',36,'859-719-4362',NULL),(415,'Wyndham','M','Aveson',22,'928-527-0845',NULL),(416,'Hyacintha','B','Trousdale',21,'638-127-8129',NULL),(417,'Gwen','E','Balfre',37,'941-147-3069',NULL),(418,'Corty','D','Kennsley',12,'303-433-4701',NULL),(419,'Tatiana','R','Figg',20,'520-688-7182',NULL),(420,'Chad','V','Sawnwy',31,'788-817-3162',NULL),(421,'Tova','Z','MacAnelley',20,'585-133-4602',NULL),(422,'Marya','A','Esp',34,'287-300-0551',NULL),(423,'Bethena','C','Mellows',2,'405-573-4229',NULL),(424,'Tisha','M','Schrei',26,'924-171-7018',NULL),(425,'John','E','McClosh',7,'638-472-6318',NULL),(426,'Trisha','T','Christon',27,'633-272-1264',NULL),(427,'Genvieve','U','Krale',26,'112-714-4042',NULL),(428,'Lurline','K','Grimoldby',22,'231-910-1003',NULL),(429,'Juanita','N','Matiebe',22,'909-721-6636',NULL),(430,'Carlos','N','Cowans',7,'373-797-5101',NULL),(431,'Anthia','X','Fellows',39,'570-696-8023',NULL),(432,'Emlyn','B','Pawlyn',2,'636-187-5618',NULL),(433,'Durward','V','Siggers',20,'304-547-8813',NULL),(434,'Teddie','P','Trencher',33,'714-398-5158',NULL),(435,'Moises','B','Ivankov',8,'126-942-3721',NULL),(436,'Jessamyn','W','Caistor',6,'104-441-6617',NULL),(437,'Gene','Y','Saltsberg',26,'453-518-1629',NULL),(438,'Moria','S','Boulter',19,'368-423-8452',NULL),(439,'Cristina','B','Tuson',2,'480-536-0284',NULL),(440,'Betsey','D','Peterken',25,'990-127-2326',NULL),(441,'Dyann','R','Scotchford',36,'500-365-0795',NULL),(442,'Corby','C','Jann',15,'918-383-5916',NULL),(443,'Jack','K','Backshell',38,'241-476-0530',NULL),(444,'Martie','B','Oakly',36,'654-337-9046',NULL),(445,'Amerigo','N','Elias',33,'410-583-4734',NULL),(446,'Ina','H','McGettrick',26,'510-501-6047',NULL),(447,'Garland','X','Craister',35,'973-807-5678',NULL),(448,'Costa','B','Stocker',6,'736-561-3797',NULL),(449,'Sherman','W','Broggini',12,'348-764-6973',NULL),(450,'Wylie','T','Tournay',22,'829-949-7073',NULL),(451,'Melisande','S','Bennike',9,'443-468-1267',NULL),(452,'Regine','R','Tapsell',10,'748-880-2449',NULL),(453,'Gui','K','Nestoruk',2,'278-616-0834',NULL),(454,'Gratia','R','Boots',29,'765-891-2645',NULL),(455,'Irma','P','Delort',23,'869-383-5186',NULL),(456,'Tabby','Q','Pyburn',35,'120-593-0293',NULL),(457,'Morris','I','Rabb',23,'940-542-0272',NULL),(458,'Arin','N','Badam',6,'547-704-3322',NULL),(459,'Evvie','I','Elia',11,'678-289-0602',NULL),(460,'Elissa','F','Clavering',36,'668-319-4553',NULL),(461,'Tracy','L','Rissom',6,'101-954-7876',NULL),(462,'Myrtie','S','Grieve',33,'320-638-9450',NULL),(463,'Constantina','K','McDaid',1,'499-614-2361',NULL),(464,'Frederic','P','Boxer',29,'163-471-2595',NULL),(465,'Tina','S','Mordey',6,'173-878-5458',NULL),(466,'Marthe','F','Moseby',12,'384-145-6120',NULL),(467,'Sandy','A','Betjeman',8,'513-223-1144',NULL),(468,'Celie','H','Jurasek',40,'378-524-1985',NULL),(469,'Khalil','E','Littlejohn',20,'215-729-7283',NULL),(470,'Ethelbert','T','Skalls',14,'594-585-2591',NULL),(471,'Ed','P','Fieldgate',10,'304-439-5720',NULL),(472,'Hamnet','C','Vann',25,'759-850-2830',NULL),(473,'Alicea','K','Lilliman',36,'877-571-2861',NULL),(474,'Cull','X','Codron',40,'657-413-9941',NULL),(475,'Diane-marie','Y','Baud',40,'810-736-3623',NULL),(476,'Allyson','V','Dreschler',27,'104-859-8337',NULL),(477,'Cynthie','S','Mathivet',7,'770-993-0758',NULL),(478,'Tuck','V','Hempel',26,'754-905-4562',NULL),(479,'Mindy','S','Eccott',8,'473-894-5223',NULL),(480,'Latashia','Y','Cow',26,'284-788-9616',NULL),(481,'Winny','N','Mingauld',34,'479-816-5041',NULL),(482,'Jonell','C','Foulds',17,'431-580-5952',NULL),(483,'Anne-marie','A','Batho',5,'242-877-1303',NULL),(484,'Cristiano','V','Tween',6,'175-526-7088',NULL),(485,'Harriet','C','Sheldrick',1,'625-975-1609',NULL),(486,'Koo','V','Beynke',4,'322-458-2416',NULL),(487,'Lavinie','I','Dayce',29,'837-682-6407',NULL),(488,'Kristel','B','Solomon',16,'637-320-6264',NULL),(489,'Isiahi','G','Buzza',3,'700-129-0535',NULL),(490,'Zedekiah','G','Filasov',16,'926-463-3794',NULL),(491,'Valli','R','Carillo',7,'171-504-2551',NULL),(492,'Graig','K','Lohoar',34,'534-144-6205',NULL),(493,'Sile','B','Hobson',14,'558-493-3756',NULL),(494,'Terrance','U','O\' Hanvey',1,'602-967-2456',NULL),(495,'Mickey','W','Rottery',8,'947-792-1276',NULL),(496,'Town','Z','Kollas',40,'245-311-5100',NULL),(497,'Christopher','N','Baynam',4,'547-762-6355',NULL),(498,'Leonelle','N','Kirsche',19,'787-839-2721',NULL),(499,'Ginger','T','Frew',37,'226-925-9493',NULL),(500,'Rice','P','Mayworth',40,'492-168-7330',NULL);
/*!40000 ALTER TABLE `Individual` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Medical_Condition`
--

DROP TABLE IF EXISTS `Medical_Condition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Medical_Condition` (
  `Condition_ID` int NOT NULL,
  `Member_ID` int DEFAULT NULL,
  `Person_ID` int DEFAULT NULL,
  `Condition_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Condition_ID`),
  KEY `Member_ID` (`Member_ID`),
  KEY `Person_ID` (`Person_ID`),
  CONSTRAINT `medical_condition_ibfk_1` FOREIGN KEY (`Member_ID`) REFERENCES `Member` (`Member_ID`),
  CONSTRAINT `medical_condition_ibfk_2` FOREIGN KEY (`Person_ID`) REFERENCES `Individual` (`Person_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Medical_Condition`
--

LOCK TABLES `Medical_Condition` WRITE;
/*!40000 ALTER TABLE `Medical_Condition` DISABLE KEYS */;
/*!40000 ALTER TABLE `Medical_Condition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Member`
--

DROP TABLE IF EXISTS `Member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Member` (
  `Member_ID` int NOT NULL,
  `Person_ID` int DEFAULT NULL,
  `Membership_status` varchar(20) DEFAULT NULL,
  `Height` decimal(5,2) DEFAULT NULL,
  `Weight` decimal(5,2) DEFAULT NULL,
  `BMI` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`Member_ID`),
  KEY `Person_ID` (`Person_ID`),
  CONSTRAINT `member_ibfk_1` FOREIGN KEY (`Person_ID`) REFERENCES `Individual` (`Person_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Member`
--

LOCK TABLES `Member` WRITE;
/*!40000 ALTER TABLE `Member` DISABLE KEYS */;
INSERT INTO `Member` VALUES (1,201,'Active',1.78,94.98,49.58),(2,202,'Inactive',1.68,140.44,23.14),(3,203,'Active',1.84,150.53,46.14),(4,204,'Active',1.75,176.27,15.99),(5,205,'Inactive',1.51,98.34,17.36),(6,206,'Inactive',1.56,147.11,46.34),(7,207,'Active',1.92,194.83,45.73),(8,208,'Inactive',1.56,117.88,11.43),(9,209,'Active',1.67,85.36,46.23),(10,210,'Active',1.80,166.98,28.86),(11,211,'Inactive',1.88,97.26,33.13),(12,212,'Inactive',1.83,140.54,10.07),(13,213,'Active',1.53,198.74,21.37),(14,214,'Active',1.70,192.07,46.35),(15,215,'Active',1.50,185.98,44.40),(16,216,'Active',1.55,209.87,19.48),(17,217,'Inactive',1.63,182.17,38.91),(18,218,'Inactive',1.93,162.49,16.60),(19,219,'Inactive',1.74,132.67,41.13),(20,220,'Inactive',1.67,86.90,42.33),(21,221,'Active',1.66,149.94,21.69),(22,222,'Inactive',1.59,86.35,17.04),(23,223,'Inactive',1.76,166.66,45.86),(24,224,'Active',1.95,199.41,25.66),(25,225,'Active',1.90,172.85,24.23),(26,226,'Inactive',1.87,110.72,11.03),(27,227,'Active',1.65,211.77,36.04),(28,228,'Inactive',1.56,133.23,47.03),(29,229,'Inactive',1.54,176.56,20.51),(30,230,'Active',1.99,106.65,18.17),(31,231,'Active',1.82,204.90,35.77),(32,232,'Inactive',1.68,102.60,34.88),(33,233,'Inactive',1.65,186.31,29.55),(34,234,'Active',1.90,121.76,49.73),(35,235,'Active',1.91,82.14,47.36),(36,236,'Active',1.71,185.59,37.88),(37,237,'Inactive',1.69,214.30,36.19),(38,238,'Active',1.52,204.61,20.52),(39,239,'Active',1.71,191.97,38.95),(40,240,'Active',1.95,213.03,47.60),(41,241,'Active',1.90,146.55,39.65),(42,242,'Inactive',1.80,86.57,39.79),(43,243,'Active',1.59,133.16,28.42),(44,244,'Active',1.73,122.63,40.50),(45,245,'Active',1.75,211.59,26.54),(46,246,'Inactive',1.67,107.40,29.66),(47,247,'Active',1.56,212.56,41.52),(48,248,'Inactive',1.91,179.02,20.11),(49,249,'Active',1.93,190.31,36.72),(50,250,'Inactive',1.75,154.20,14.55),(51,251,'Inactive',1.84,146.49,41.51),(52,252,'Active',1.56,184.71,10.74),(53,253,'Inactive',1.61,97.12,26.75),(54,254,'Inactive',1.71,134.69,17.64),(55,255,'Inactive',1.98,137.60,22.96),(56,256,'Inactive',1.97,97.33,27.22),(57,257,'Inactive',1.89,143.29,48.23),(58,258,'Active',1.91,89.14,46.43),(59,259,'Active',1.93,81.66,26.20),(60,260,'Inactive',1.69,198.59,28.09),(61,261,'Inactive',1.69,113.36,29.56),(62,262,'Inactive',1.80,142.84,42.18),(63,263,'Active',1.65,189.90,26.47),(64,264,'Inactive',1.78,201.20,19.74),(65,265,'Active',1.57,189.69,41.07),(66,266,'Inactive',1.50,119.23,36.10),(67,267,'Active',1.67,197.27,20.61),(68,268,'Inactive',1.64,183.43,47.31),(69,269,'Active',1.83,151.57,40.19),(70,270,'Inactive',1.69,202.60,18.20),(71,271,'Inactive',1.60,190.92,36.61),(72,272,'Inactive',1.85,138.38,11.28),(73,273,'Inactive',1.88,210.06,14.62),(74,274,'Inactive',1.69,199.89,15.58),(75,275,'Active',1.75,138.27,23.09),(76,276,'Inactive',1.95,107.80,38.02),(77,277,'Inactive',1.68,196.24,21.60),(78,278,'Active',1.95,126.58,44.38),(79,279,'Inactive',1.58,93.08,18.55),(80,280,'Inactive',1.88,201.20,10.64),(81,281,'Inactive',1.54,136.33,33.41),(82,282,'Inactive',1.63,155.04,27.77),(83,283,'Active',2.00,120.82,44.34),(84,284,'Inactive',1.77,212.26,11.87),(85,285,'Inactive',1.53,118.50,10.50),(86,286,'Active',1.87,132.90,26.77),(87,287,'Active',1.93,198.96,11.04),(88,288,'Inactive',1.95,200.60,12.86),(89,289,'Active',1.69,149.24,36.90),(90,290,'Inactive',1.84,193.45,28.63),(91,291,'Active',1.58,139.57,28.20),(92,292,'Active',1.84,211.13,26.65),(93,293,'Inactive',1.72,203.19,22.31),(94,294,'Active',1.68,178.06,21.62),(95,295,'Inactive',1.89,99.10,47.56),(96,296,'Inactive',1.70,108.78,40.96),(97,297,'Inactive',1.73,184.00,24.29),(98,298,'Inactive',1.58,195.20,23.37),(99,299,'Active',1.89,128.65,23.96),(100,300,'Active',1.68,202.26,36.96),(101,301,'Inactive',1.65,113.77,47.04),(102,302,'Active',1.83,101.11,45.41),(103,303,'Inactive',1.89,207.45,35.26),(104,304,'Active',1.76,124.32,19.04),(105,305,'Inactive',1.69,107.49,24.05),(106,306,'Active',1.66,191.37,35.22),(107,307,'Inactive',1.55,103.63,29.00),(108,308,'Active',1.78,93.21,38.30),(109,309,'Active',1.53,168.78,30.40),(110,310,'Inactive',1.80,137.34,19.65),(111,311,'Active',1.80,146.91,39.20),(112,312,'Active',1.87,182.15,12.32),(113,313,'Active',1.52,155.82,46.06),(114,314,'Inactive',1.79,200.28,17.01),(115,315,'Inactive',1.89,110.27,15.85),(116,316,'Inactive',1.76,165.61,39.87),(117,317,'Inactive',1.73,179.10,43.65),(118,318,'Active',1.54,191.84,43.88),(119,319,'Inactive',1.79,209.28,31.59),(120,320,'Inactive',1.79,165.84,41.04),(121,321,'Active',1.53,139.76,35.51),(122,322,'Active',1.59,185.74,36.43),(123,323,'Inactive',1.55,139.29,39.76),(124,324,'Inactive',1.91,208.13,40.72),(125,325,'Active',1.83,180.51,20.52),(126,326,'Active',1.76,98.67,19.25),(127,327,'Active',1.98,105.93,28.80),(128,328,'Active',1.82,153.58,45.52),(129,329,'Active',1.72,104.09,42.58),(130,330,'Inactive',1.50,188.56,22.86),(131,331,'Inactive',1.70,116.84,33.96),(132,332,'Inactive',1.92,109.21,17.25),(133,333,'Inactive',1.87,111.92,43.50),(134,334,'Inactive',1.52,154.65,28.13),(135,335,'Inactive',1.56,125.48,33.24),(136,336,'Active',1.76,116.61,35.30),(137,337,'Inactive',1.67,109.65,29.34),(138,338,'Active',1.72,134.66,34.09),(139,339,'Inactive',1.63,101.71,41.94),(140,340,'Inactive',1.52,138.39,17.23),(141,341,'Inactive',1.62,199.44,31.14),(142,342,'Active',1.89,159.51,22.58),(143,343,'Inactive',1.54,198.68,26.28),(144,344,'Active',1.52,94.58,11.86),(145,345,'Active',1.86,173.29,34.84),(146,346,'Inactive',2.00,162.27,12.35),(147,347,'Active',1.98,103.44,29.30),(148,348,'Inactive',1.60,132.20,38.36),(149,349,'Active',1.97,137.49,15.22),(150,350,'Inactive',1.86,156.03,41.66),(151,351,'Inactive',1.79,100.45,45.07),(152,352,'Active',1.69,154.68,23.79),(153,353,'Active',1.88,210.67,35.51),(154,354,'Active',1.63,196.12,31.35),(155,355,'Inactive',1.67,200.97,33.12),(156,356,'Active',1.51,124.03,37.51),(157,357,'Inactive',1.69,139.14,41.92),(158,358,'Inactive',1.57,129.09,27.04),(159,359,'Inactive',1.69,141.84,35.21),(160,360,'Inactive',1.72,133.50,11.20),(161,361,'Active',1.79,151.82,14.28),(162,362,'Inactive',1.83,176.07,11.78),(163,363,'Active',1.70,169.63,23.90),(164,364,'Inactive',1.66,104.75,32.77),(165,365,'Active',1.86,89.59,48.94),(166,366,'Active',1.91,171.51,27.83),(167,367,'Active',1.62,174.08,35.64),(168,368,'Active',1.68,145.58,41.33),(169,369,'Active',1.99,123.01,25.99),(170,370,'Inactive',1.72,201.62,32.67),(171,371,'Active',1.85,128.60,48.93),(172,372,'Active',1.68,102.77,37.62),(173,373,'Active',1.63,124.47,40.70),(174,374,'Active',1.79,171.74,36.89),(175,375,'Inactive',1.63,90.93,36.88),(176,376,'Active',1.51,145.07,18.14),(177,377,'Inactive',1.88,86.35,25.45),(178,378,'Inactive',1.70,127.81,46.20),(179,379,'Inactive',1.87,157.08,30.21),(180,380,'Inactive',1.86,81.56,30.43),(181,381,'Active',1.58,120.46,20.82),(182,382,'Inactive',1.80,122.43,25.95),(183,383,'Inactive',1.86,111.91,34.33),(184,384,'Active',1.73,179.95,16.29),(185,385,'Active',1.71,110.05,17.60),(186,386,'Inactive',1.59,174.77,30.88),(187,387,'Inactive',1.80,149.51,46.77),(188,388,'Active',1.75,120.13,20.65),(189,389,'Inactive',1.90,121.08,25.81),(190,390,'Inactive',1.96,152.50,47.26),(191,391,'Active',1.83,161.58,31.74),(192,392,'Active',1.66,113.78,32.38),(193,393,'Active',1.63,99.22,12.29),(194,394,'Active',1.59,138.14,33.40),(195,395,'Inactive',1.71,211.38,16.74),(196,396,'Inactive',1.82,118.42,29.15),(197,397,'Inactive',1.71,145.15,39.62),(198,398,'Active',1.58,163.91,20.89),(199,399,'Inactive',1.51,95.30,25.55),(200,400,'Active',1.98,125.92,35.06),(201,401,'Inactive',1.61,210.51,14.19),(202,402,'Active',1.89,110.34,44.19),(203,403,'Inactive',1.90,114.09,25.88),(204,404,'Inactive',1.86,80.01,16.98),(205,405,'Active',1.64,214.21,15.76),(206,406,'Active',2.00,179.10,49.63),(207,407,'Active',1.90,150.11,25.95),(208,408,'Active',1.70,173.35,45.51),(209,409,'Inactive',1.58,173.60,43.05),(210,410,'Active',1.77,108.13,36.00),(211,411,'Inactive',1.74,170.90,18.59),(212,412,'Inactive',1.74,180.43,15.23),(213,413,'Active',1.82,193.91,13.67),(214,414,'Inactive',1.98,196.77,40.40),(215,415,'Inactive',1.81,90.13,42.94),(216,416,'Inactive',1.55,166.56,23.47),(217,417,'Active',1.76,116.46,11.01),(218,418,'Active',1.54,132.48,21.72),(219,419,'Active',1.56,127.63,49.35),(220,420,'Active',1.92,86.05,47.27),(221,421,'Active',1.98,175.80,25.76),(222,422,'Active',1.51,141.48,12.80),(223,423,'Inactive',1.56,85.94,41.41),(224,424,'Inactive',1.87,162.49,12.60),(225,425,'Active',1.83,117.68,24.36),(226,426,'Inactive',1.57,151.09,25.94),(227,427,'Inactive',1.85,193.80,48.88),(228,428,'Active',1.99,117.94,35.00),(229,429,'Active',1.63,194.26,17.82),(230,430,'Inactive',1.76,137.01,12.07),(231,431,'Inactive',1.68,193.98,21.97),(232,432,'Inactive',1.64,189.60,35.00),(233,433,'Active',1.52,198.18,14.66),(234,434,'Active',1.52,189.97,10.11),(235,435,'Active',1.69,138.11,39.47),(236,436,'Active',1.64,92.46,12.37),(237,437,'Inactive',1.96,164.32,16.12),(238,438,'Inactive',1.70,168.91,36.49),(239,439,'Inactive',1.87,170.80,42.91),(240,440,'Active',1.75,109.23,31.34),(241,441,'Active',1.89,91.30,48.92),(242,442,'Active',1.96,95.90,14.66),(243,443,'Inactive',1.82,115.37,17.02),(244,444,'Inactive',1.85,165.91,35.11),(245,445,'Active',1.75,147.50,11.12),(246,446,'Active',1.52,89.36,29.90),(247,447,'Active',1.60,106.27,18.96),(248,448,'Active',1.69,140.09,42.00),(249,449,'Active',1.80,207.52,26.73),(250,450,'Inactive',1.90,125.10,30.61),(251,451,'Active',1.70,131.29,20.68),(252,452,'Inactive',1.97,134.13,21.41),(253,453,'Active',1.81,207.74,27.40),(254,454,'Active',1.51,118.32,24.95),(255,455,'Inactive',1.61,86.19,40.97),(256,456,'Active',1.97,91.07,44.49),(257,457,'Inactive',1.51,103.75,12.00),(258,458,'Active',2.00,88.96,10.36),(259,459,'Inactive',1.69,213.53,46.16),(260,460,'Active',1.92,177.00,13.94),(261,461,'Active',1.73,85.07,34.41),(262,462,'Active',1.73,100.42,47.04),(263,463,'Active',1.93,105.00,22.06),(264,464,'Active',1.54,203.02,17.40),(265,465,'Active',1.54,149.70,13.55),(266,466,'Inactive',1.94,122.94,21.29),(267,467,'Active',1.93,189.80,11.89),(268,468,'Inactive',1.93,116.86,33.33),(269,469,'Inactive',1.67,195.29,15.64),(270,470,'Inactive',1.96,184.70,45.43),(271,471,'Inactive',1.67,108.80,44.67),(272,472,'Inactive',1.58,126.74,15.80),(273,473,'Active',1.66,204.46,17.55),(274,474,'Inactive',1.56,192.13,22.25),(275,475,'Active',1.62,144.34,42.59),(276,476,'Inactive',1.87,139.04,13.35),(277,477,'Inactive',1.73,109.39,29.41),(278,478,'Active',1.71,213.94,42.25),(279,479,'Active',1.70,123.36,41.18),(280,480,'Active',1.99,95.95,18.48),(281,481,'Active',1.64,102.91,38.46),(282,482,'Inactive',1.56,148.77,17.76),(283,483,'Active',1.67,205.20,11.90),(284,484,'Inactive',1.57,182.25,47.21),(285,485,'Active',1.69,139.13,26.01),(286,486,'Active',1.74,149.00,14.29),(287,487,'Inactive',1.75,202.60,38.66),(288,488,'Active',1.94,141.92,41.79),(289,489,'Inactive',1.85,177.56,31.61),(290,490,'Inactive',1.76,122.70,45.59),(291,491,'Inactive',1.87,82.91,16.31),(292,492,'Inactive',1.75,206.86,30.88),(293,493,'Inactive',1.73,164.00,30.69),(294,494,'Active',1.58,190.59,10.03),(295,495,'Inactive',1.96,118.59,45.08),(296,496,'Active',1.69,165.72,45.95),(297,497,'Active',1.67,82.85,25.32),(298,498,'Inactive',1.67,209.25,26.42),(299,499,'Inactive',1.72,177.12,31.21),(300,500,'Active',1.68,129.56,10.35);
/*!40000 ALTER TABLE `Member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Member_Consults_Nutritionist`
--

DROP TABLE IF EXISTS `Member_Consults_Nutritionist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Member_Consults_Nutritionist` (
  `Member_ID` int NOT NULL,
  `Employee_ID` int NOT NULL,
  PRIMARY KEY (`Member_ID`,`Employee_ID`),
  KEY `Employee_ID` (`Employee_ID`),
  CONSTRAINT `member_consults_nutritionist_ibfk_1` FOREIGN KEY (`Member_ID`) REFERENCES `Member` (`Member_ID`),
  CONSTRAINT `member_consults_nutritionist_ibfk_2` FOREIGN KEY (`Employee_ID`) REFERENCES `Nutritionist` (`Employee_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Member_Consults_Nutritionist`
--

LOCK TABLES `Member_Consults_Nutritionist` WRITE;
/*!40000 ALTER TABLE `Member_Consults_Nutritionist` DISABLE KEYS */;
INSERT INTO `Member_Consults_Nutritionist` VALUES (1,8),(62,8),(123,8),(184,8),(245,8),(2,9),(63,9),(124,9),(185,9),(246,9),(3,11),(64,11),(125,11),(186,11),(247,11),(4,12),(65,12),(126,12),(187,12),(248,12),(5,14),(66,14),(127,14),(188,14),(249,14),(6,15),(67,15),(128,15),(189,15),(250,15),(7,18),(68,18),(129,18),(190,18),(8,19),(69,19),(130,19),(191,19),(9,20),(70,20),(131,20),(192,20),(10,21),(71,21),(132,21),(193,21),(11,25),(72,25),(133,25),(194,25),(12,26),(73,26),(134,26),(195,26),(13,28),(74,28),(135,28),(196,28),(14,35),(75,35),(136,35),(197,35),(15,37),(76,37),(137,37),(198,37),(16,59),(77,59),(138,59),(199,59),(17,60),(78,60),(139,60),(200,60),(18,62),(79,62),(140,62),(201,62),(19,63),(80,63),(141,63),(202,63),(20,64),(81,64),(142,64),(203,64),(21,74),(82,74),(143,74),(204,74),(22,78),(83,78),(144,78),(205,78),(23,83),(84,83),(145,83),(206,83),(24,84),(85,84),(146,84),(207,84),(25,91),(86,91),(147,91),(208,91),(26,93),(87,93),(148,93),(209,93),(27,94),(88,94),(149,94),(210,94),(28,98),(89,98),(150,98),(211,98),(29,106),(90,106),(151,106),(212,106),(30,110),(91,110),(152,110),(213,110),(31,111),(92,111),(153,111),(214,111),(32,112),(93,112),(154,112),(215,112),(33,115),(94,115),(155,115),(216,115),(34,117),(95,117),(156,117),(217,117),(35,120),(96,120),(157,120),(218,120),(36,125),(97,125),(158,125),(219,125),(37,128),(98,128),(159,128),(220,128),(38,130),(99,130),(160,130),(221,130),(39,135),(100,135),(161,135),(222,135),(40,138),(101,138),(162,138),(223,138),(41,139),(102,139),(163,139),(224,139),(42,148),(103,148),(164,148),(225,148),(43,151),(104,151),(165,151),(226,151),(44,154),(105,154),(166,154),(227,154),(45,156),(106,156),(167,156),(228,156),(46,157),(107,157),(168,157),(229,157),(47,159),(108,159),(169,159),(230,159),(48,162),(109,162),(170,162),(231,162),(49,163),(110,163),(171,163),(232,163),(50,164),(111,164),(172,164),(233,164),(51,165),(112,165),(173,165),(234,165),(52,166),(113,166),(174,166),(235,166),(53,174),(114,174),(175,174),(236,174),(54,176),(115,176),(176,176),(237,176),(55,179),(116,179),(177,179),(238,179),(56,180),(117,180),(178,180),(239,180),(57,187),(118,187),(179,187),(240,187),(58,190),(119,190),(180,190),(241,190),(59,194),(120,194),(181,194),(242,194),(60,197),(121,197),(182,197),(243,197),(61,198),(122,198),(183,198),(244,198);
/*!40000 ALTER TABLE `Member_Consults_Nutritionist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Member_Participates_Workout_Session`
--

DROP TABLE IF EXISTS `Member_Participates_Workout_Session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Member_Participates_Workout_Session` (
  `Member_ID` int NOT NULL,
  `Workout_ID` int NOT NULL,
  PRIMARY KEY (`Member_ID`,`Workout_ID`),
  KEY `Workout_ID` (`Workout_ID`),
  CONSTRAINT `member_participates_workout_session_ibfk_1` FOREIGN KEY (`Member_ID`) REFERENCES `Member` (`Member_ID`),
  CONSTRAINT `member_participates_workout_session_ibfk_2` FOREIGN KEY (`Workout_ID`) REFERENCES `Workout_Session` (`Workout_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Member_Participates_Workout_Session`
--

LOCK TABLES `Member_Participates_Workout_Session` WRITE;
/*!40000 ALTER TABLE `Member_Participates_Workout_Session` DISABLE KEYS */;
INSERT INTO `Member_Participates_Workout_Session` VALUES (10,1),(175,2),(192,3),(167,4),(81,5),(233,6),(215,7),(138,8),(180,9),(129,10),(103,11),(79,12),(4,13),(282,14),(173,15),(157,16),(240,17),(243,18),(211,19),(283,20),(268,21),(69,22),(21,23),(181,24),(37,25),(59,26),(160,27),(136,28),(110,29),(244,30),(49,31),(33,32),(139,33),(61,34),(65,35),(183,36),(246,37),(259,38),(142,39),(23,40),(271,41),(134,42),(125,43),(60,44),(98,45),(105,46),(116,47),(29,48),(166,49),(157,50),(199,51),(257,52),(122,53),(160,54),(196,55),(183,56),(240,57),(267,58),(132,59),(136,60),(210,61),(56,62),(209,63),(130,64),(127,65),(51,66),(97,67),(192,68),(203,69),(282,70),(122,71),(247,72),(53,73),(223,74),(259,75),(36,76),(206,77),(82,78),(77,79),(127,80),(126,81),(198,82),(299,83),(222,84),(6,85),(63,86),(92,87),(42,88),(183,89),(255,90),(16,91),(256,92),(79,93),(273,94),(81,95),(125,96),(209,97),(286,98),(96,99),(21,100),(254,101),(100,102),(78,103),(148,104),(86,105),(192,106),(264,107),(178,108),(3,109),(194,110),(266,111),(200,112),(180,113),(216,114),(148,115),(170,116),(219,117),(40,118),(157,119),(278,120),(248,121),(216,122),(115,123),(222,124),(105,125),(28,126),(10,127),(87,128),(202,129),(65,130),(249,131),(196,132),(63,133),(154,134),(245,135),(92,136),(269,137),(119,138),(21,139),(195,140),(103,141),(226,142),(51,143),(167,144),(228,145),(206,146),(212,147),(230,148),(196,149),(9,150),(170,151),(69,152),(54,153),(261,154),(77,155),(67,156),(97,157),(94,158),(249,159),(296,160),(296,161),(197,162),(276,163),(147,164),(227,165),(246,166),(283,167),(297,168),(91,169),(22,170),(30,171),(248,172),(37,173),(286,174),(242,175),(14,176),(66,177),(300,178),(118,179),(142,180),(150,181),(227,182),(90,183),(84,184),(36,185),(271,186),(254,187),(176,188),(121,189),(240,190),(184,191),(168,192),(183,193),(66,194),(251,195),(261,196),(224,197),(49,198),(266,199),(250,200),(246,201),(95,202),(36,203),(230,204),(160,205),(27,206),(297,207),(14,208),(23,209),(263,210),(147,211),(253,212),(19,213),(169,214),(195,215),(51,216),(62,217),(54,218),(153,219),(231,220),(144,221),(137,222),(36,223),(41,224),(119,225),(113,226),(127,227),(170,228),(289,229),(30,230),(107,231),(201,232),(118,233),(91,234),(249,235),(51,236),(165,237),(39,238),(81,239),(25,240),(238,241),(279,242),(283,243),(228,244),(202,245),(47,246),(120,247),(281,248),(174,249),(280,250),(107,251),(70,252),(259,253),(64,254),(102,255),(90,256),(168,257),(122,258),(234,259),(298,260),(232,261),(51,262),(12,263),(241,264),(64,265),(242,266),(263,267),(245,268),(63,269),(168,270),(113,271),(207,272),(120,273),(159,274),(36,275),(280,276),(63,277),(185,278),(148,279),(274,280),(300,281),(154,282),(229,283),(6,284),(33,285),(58,286),(124,287),(100,288),(186,289),(6,290),(25,291),(150,292),(62,293),(192,294),(155,295),(78,296),(229,297),(241,298),(207,299),(79,300),(300,301),(262,302),(180,303),(300,304),(248,305),(236,306),(127,307),(71,308),(220,309),(94,310),(92,311),(186,312),(116,313),(26,314),(118,315),(282,316),(176,317),(251,318),(282,319),(8,320),(114,321),(4,322),(167,323),(127,324),(143,325),(46,326),(211,327),(246,328),(110,329),(275,330),(214,331),(45,332),(270,333),(20,334),(85,335),(151,336),(99,337),(69,338),(266,339),(285,340),(243,341),(228,342),(275,343),(261,344),(7,345),(195,346),(224,347),(263,348),(187,349),(78,350),(274,351),(203,352),(24,353),(191,354),(275,355),(27,356),(254,357),(64,358),(48,359),(229,360),(132,361),(87,362),(43,363),(235,364),(192,365),(175,366),(164,367),(191,368),(51,369),(155,370),(91,371),(244,372),(1,373),(205,374),(115,375),(218,376),(3,377),(7,378),(293,379),(148,380),(30,381),(182,382),(177,383),(198,384),(103,385),(209,386),(122,387),(156,388),(212,389),(148,390),(154,391),(245,392),(72,393),(21,394),(247,395),(205,396),(292,397),(47,398),(91,399),(128,400),(256,401),(96,402),(92,403),(136,404),(284,405),(102,406),(7,407),(229,408),(7,409),(292,410),(157,411),(238,412),(26,413),(2,414),(172,415),(95,416),(171,417),(190,418),(287,419),(189,420),(170,421),(143,422),(74,423),(16,424),(28,425),(93,426),(154,427),(182,428),(14,429),(230,430),(79,431),(241,432),(269,433),(201,434),(138,435),(14,436),(139,437),(145,438),(78,439),(92,440),(109,441),(228,442),(162,443),(263,444),(211,445),(198,446),(137,447),(213,448),(77,449),(234,450),(212,451),(174,452),(4,453),(281,454),(217,455),(178,456),(274,457),(294,458),(66,459),(99,460),(233,461),(126,462),(150,463),(16,464),(51,465),(266,466),(287,467),(87,468),(119,469),(111,470),(169,471),(117,472),(203,473),(208,474),(23,475),(258,476),(40,477),(66,478),(143,479),(153,480),(129,481),(132,482),(120,483),(140,484),(251,485),(147,486),(282,487),(153,488),(204,489),(21,490),(221,491),(46,492),(36,493),(234,494),(84,495),(65,496),(96,497),(188,498),(210,499),(50,500);
/*!40000 ALTER TABLE `Member_Participates_Workout_Session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Member_VR_Preferences`
--

DROP TABLE IF EXISTS `Member_VR_Preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Member_VR_Preferences` (
  `Member_ID` int NOT NULL,
  `VR_Preferences` varchar(50) DEFAULT NULL,
  `Person_ID` int DEFAULT NULL,
  PRIMARY KEY (`Member_ID`),
  KEY `Person_ID` (`Person_ID`),
  CONSTRAINT `member_vr_preferences_ibfk_1` FOREIGN KEY (`Person_ID`) REFERENCES `Individual` (`Person_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Member_VR_Preferences`
--

LOCK TABLES `Member_VR_Preferences` WRITE;
/*!40000 ALTER TABLE `Member_VR_Preferences` DISABLE KEYS */;
/*!40000 ALTER TABLE `Member_VR_Preferences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Nutrition_Plan`
--

DROP TABLE IF EXISTS `Nutrition_Plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Nutrition_Plan` (
  `Plan_Name` varchar(50) NOT NULL,
  `Member_ID` int NOT NULL,
  `Goal` varchar(100) DEFAULT NULL,
  `Duration` int DEFAULT NULL,
  `Calories` decimal(5,2) DEFAULT NULL,
  `Protein` decimal(5,2) DEFAULT NULL,
  `Carbs` decimal(5,2) DEFAULT NULL,
  `Fat` decimal(5,2) DEFAULT NULL,
  `Employee_ID` int DEFAULT NULL,
  PRIMARY KEY (`Plan_Name`,`Member_ID`),
  KEY `Member_ID` (`Member_ID`),
  KEY `Employee_ID` (`Employee_ID`),
  CONSTRAINT `nutrition_plan_ibfk_1` FOREIGN KEY (`Member_ID`) REFERENCES `Member` (`Member_ID`),
  CONSTRAINT `nutrition_plan_ibfk_2` FOREIGN KEY (`Employee_ID`) REFERENCES `Employee` (`Employee_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Nutrition_Plan`
--

LOCK TABLES `Nutrition_Plan` WRITE;
/*!40000 ALTER TABLE `Nutrition_Plan` DISABLE KEYS */;
/*!40000 ALTER TABLE `Nutrition_Plan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Nutritionist`
--

DROP TABLE IF EXISTS `Nutritionist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Nutritionist` (
  `Employee_ID` int NOT NULL,
  `Certifications` varchar(100) DEFAULT NULL,
  `Experience_level` varchar(50) DEFAULT NULL,
  `Active_clients` int DEFAULT NULL,
  PRIMARY KEY (`Employee_ID`),
  CONSTRAINT `nutritionist_ibfk_1` FOREIGN KEY (`Employee_ID`) REFERENCES `Employee` (`Employee_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Nutritionist`
--

LOCK TABLES `Nutritionist` WRITE;
/*!40000 ALTER TABLE `Nutritionist` DISABLE KEYS */;
INSERT INTO `Nutritionist` VALUES (8,'Certified Nutritionist (CN)','Experienced',2),(9,'Certified Nutritionist (CN)','Experienced',5),(11,'Registered Dietitian (RD)','Experienced',6),(12,'Certified Nutrition Specialist (CNS)','Experienced',5),(14,'Registered Dietitian (RD)','Experienced',1),(15,'Certified Nutrition Specialist (CNS)','Entry level',0),(18,'Certified Nutrition Specialist (CNS)','Experienced',0),(19,'Certified Nutritionist (CN)','Experienced',1),(20,'Certified Nutritionist (CN)','Entry level',5),(21,'Certified Nutritionist (CN)','Entry level',3),(25,'Registered Dietitian (RD)','Entry level',0),(26,'Registered Dietitian (RD)','Experienced',4),(28,'Registered Dietitian (RD)','Experienced',3),(35,'Registered Dietitian (RD)','Entry level',3),(37,'Certified Nutrition Specialist (CNS)','Entry level',6),(59,'Certified Nutrition Specialist (CNS)','Experienced',6),(60,'Registered Dietitian (RD)','Experienced',0),(62,'Certified Nutrition Specialist (CNS)','Entry level',0),(63,'Certified Nutrition Specialist (CNS)','Entry level',6),(64,'Registered Dietitian (RD)','Entry level',3),(74,'Certified Nutritionist (CN)','Entry level',6),(78,'Certified Nutritionist (CN)','Entry level',4),(83,'Certified Nutritionist (CN)','Experienced',3),(84,'Certified Nutrition Specialist (CNS)','Experienced',2),(91,'Certified Nutrition Specialist (CNS)','Experienced',1),(93,'Certified Nutrition Specialist (CNS)','Experienced',2),(94,'Certified Nutrition Specialist (CNS)','Entry level',0),(98,'Certified Nutrition Specialist (CNS)','Entry level',5),(106,'Certified Nutritionist (CN)','Entry level',2),(110,'Registered Dietitian (RD)','Entry level',0),(111,'Certified Nutrition Specialist (CNS)','Experienced',3),(112,'Registered Dietitian (RD)','Entry level',1),(115,'Registered Dietitian (RD)','Entry level',5),(117,'Certified Nutritionist (CN)','Experienced',1),(120,'Certified Nutritionist (CN)','Entry level',5),(125,'Certified Nutrition Specialist (CNS)','Experienced',4),(128,'Certified Nutritionist (CN)','Entry level',1),(130,'Certified Nutritionist (CN)','Experienced',6),(135,'Registered Dietitian (RD)','Entry level',5),(138,'Certified Nutrition Specialist (CNS)','Entry level',5),(139,'Certified Nutritionist (CN)','Experienced',3),(148,'Registered Dietitian (RD)','Entry level',4),(151,'Registered Dietitian (RD)','Experienced',4),(154,'Certified Nutritionist (CN)','Entry level',0),(156,'Certified Nutritionist (CN)','Entry level',4),(157,'Registered Dietitian (RD)','Experienced',2),(159,'Certified Nutritionist (CN)','Experienced',6),(162,'Certified Nutrition Specialist (CNS)','Experienced',0),(163,'Certified Nutritionist (CN)','Experienced',2),(164,'Certified Nutritionist (CN)','Entry level',0),(165,'Registered Dietitian (RD)','Entry level',1),(166,'Certified Nutritionist (CN)','Experienced',4),(174,'Certified Nutritionist (CN)','Entry level',0),(176,'Certified Nutritionist (CN)','Entry level',4),(179,'Certified Nutrition Specialist (CNS)','Entry level',5),(180,'Certified Nutritionist (CN)','Experienced',3),(187,'Certified Nutritionist (CN)','Experienced',1),(190,'Registered Dietitian (RD)','Entry level',1),(194,'Registered Dietitian (RD)','Experienced',3),(197,'Certified Nutrition Specialist (CNS)','Entry level',0),(198,'Certified Nutritionist (CN)','Experienced',4);
/*!40000 ALTER TABLE `Nutritionist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Payment`
--

DROP TABLE IF EXISTS `Payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Payment` (
  `Payment_ID` int NOT NULL,
  `Member_ID` int DEFAULT NULL,
  `Payment_date` date DEFAULT NULL,
  `Mode_of_payment` varchar(50) DEFAULT NULL,
  `Amount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`Payment_ID`),
  KEY `Member_ID` (`Member_ID`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`Member_ID`) REFERENCES `Member` (`Member_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Payment`
--

LOCK TABLES `Payment` WRITE;
/*!40000 ALTER TABLE `Payment` DISABLE KEYS */;
/*!40000 ALTER TABLE `Payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Role`
--

DROP TABLE IF EXISTS `Role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Role` (
  `Role_ID` int NOT NULL,
  `Role_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Role_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Role`
--

LOCK TABLES `Role` WRITE;
/*!40000 ALTER TABLE `Role` DISABLE KEYS */;
INSERT INTO `Role` VALUES (1,'Front desk'),(2,'Trainer'),(3,'Nutritionist');
/*!40000 ALTER TABLE `Role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Shift`
--

DROP TABLE IF EXISTS `Shift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Shift` (
  `Employee_ID` int NOT NULL,
  `Day` date NOT NULL,
  `Time` time NOT NULL,
  PRIMARY KEY (`Employee_ID`,`Day`,`Time`),
  CONSTRAINT `shift_ibfk_1` FOREIGN KEY (`Employee_ID`) REFERENCES `Employee` (`Employee_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Shift`
--

LOCK TABLES `Shift` WRITE;
/*!40000 ALTER TABLE `Shift` DISABLE KEYS */;
/*!40000 ALTER TABLE `Shift` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `VR_Equipment`
--

DROP TABLE IF EXISTS `VR_Equipment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `VR_Equipment` (
  `Equipment_ID` int NOT NULL,
  `Type` varchar(50) DEFAULT NULL,
  `Name` varchar(50) DEFAULT NULL,
  `Status` varchar(20) DEFAULT NULL,
  `Maintenance_schedule` date DEFAULT NULL,
  PRIMARY KEY (`Equipment_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `VR_Equipment`
--

LOCK TABLES `VR_Equipment` WRITE;
/*!40000 ALTER TABLE `VR_Equipment` DISABLE KEYS */;
INSERT INTO `VR_Equipment` VALUES (1,'Cycling VR','LawnGreen Cycling VR','Available','2024-09-05'),(2,'Boxing VR','HotPink Boxing VR','In Maintenance','2024-03-24'),(3,'Treadmill VR','NavajoWhite Treadmill VR','In Maintenance','2024-10-30'),(4,'Yoga VR','DarkViolet Yoga VR','In Maintenance','2023-08-22'),(5,'Treadmill VR','LightGoldenRodYellow Treadmill VR','Out of Order','2024-10-25'),(6,'Cycling VR','Moccasin Cycling VR','In Maintenance','2023-03-07'),(7,'Yoga VR','Beige Yoga VR','Available','2024-04-10'),(8,'Cycling VR','Sienna Cycling VR','In Maintenance','2024-02-28'),(9,'Treadmill VR','MediumTurquoise Treadmill VR','Out of Order','2024-06-25'),(10,'Yoga VR','SeaGreen Yoga VR','Available','2024-10-22'),(11,'Cycling VR','DarkGoldenRod Cycling VR','Out of Order','2024-01-25'),(12,'Cycling VR','DarkOrchid Cycling VR','In Maintenance','2023-05-10'),(13,'Cycling VR','GoldenRod Cycling VR','Available','2023-01-25'),(14,'Treadmill VR','Ivory Treadmill VR','In Maintenance','2024-07-18'),(15,'Boxing VR','Teal Boxing VR','In Maintenance','2023-08-16'),(16,'Boxing VR','DarkCyan Boxing VR','Available','2024-01-09'),(17,'Boxing VR','PaleVioletRed Boxing VR','Out of Order','2024-11-24'),(18,'Boxing VR','Snow Boxing VR','Out of Order','2023-05-11'),(19,'Boxing VR','LightSalmon Boxing VR','In Maintenance','2023-11-03'),(20,'Boxing VR','DarkViolet Boxing VR','Available','2023-09-28'),(21,'Boxing VR','IndianRed Boxing VR','In Maintenance','2024-05-12'),(22,'Cycling VR','PeachPuff Cycling VR','In Maintenance','2024-04-10'),(23,'Boxing VR','DarkKhaki Boxing VR','In Maintenance','2024-12-08'),(24,'Rowing VR','LightSlateGray Rowing VR','Out of Order','2023-12-13'),(25,'Cycling VR','LightYellow Cycling VR','In Maintenance','2024-10-09'),(26,'Treadmill VR','Wheat Treadmill VR','Available','2024-04-12'),(27,'Yoga VR','PaleGreen Yoga VR','In Maintenance','2023-03-27'),(28,'Yoga VR','MistyRose Yoga VR','In Maintenance','2024-05-13'),(29,'Yoga VR','DarkSeaGreen Yoga VR','Available','2023-07-21'),(30,'Treadmill VR','RoyalBlue Treadmill VR','Available','2024-10-19'),(31,'Cycling VR','LightGreen Cycling VR','Available','2023-07-26'),(32,'Yoga VR','Aquamarine Yoga VR','In Maintenance','2023-06-22'),(33,'Cycling VR','Ivory Cycling VR','Out of Order','2023-02-13'),(34,'Treadmill VR','Orchid Treadmill VR','Out of Order','2023-08-13'),(35,'Cycling VR','Yellow Cycling VR','Available','2023-12-14'),(36,'Treadmill VR','LightGoldenRodYellow Treadmill VR','Out of Order','2023-02-24'),(37,'Treadmill VR','Gainsboro Treadmill VR','Available','2024-09-22'),(38,'Yoga VR','DarkBlue Yoga VR','Out of Order','2023-12-11'),(39,'Boxing VR','Azure Boxing VR','Out of Order','2023-12-29'),(40,'Cycling VR','DarkBlue Cycling VR','In Maintenance','2023-08-14'),(41,'Yoga VR','DarkTurquoise Yoga VR','In Maintenance','2023-04-05'),(42,'Yoga VR','SandyBrown Yoga VR','Available','2023-03-01'),(43,'Boxing VR','GhostWhite Boxing VR','In Maintenance','2023-06-29'),(44,'Rowing VR','Yellow Rowing VR','In Maintenance','2024-05-12'),(45,'Treadmill VR','Sienna Treadmill VR','In Maintenance','2024-01-18'),(46,'Treadmill VR','IndianRed Treadmill VR','Out of Order','2024-08-10'),(47,'Yoga VR','OliveDrab Yoga VR','In Maintenance','2024-04-29'),(48,'Treadmill VR','Gray Treadmill VR','In Maintenance','2024-03-24'),(49,'Yoga VR','Turquoise Yoga VR','Available','2023-03-17'),(50,'Cycling VR','LightBlue Cycling VR','In Maintenance','2024-01-09');
/*!40000 ALTER TABLE `VR_Equipment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Workout_Log`
--

DROP TABLE IF EXISTS `Workout_Log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Workout_Log` (
  `Log_ID` int NOT NULL,
  `Member_ID` int DEFAULT NULL,
  `Workout_Session_ID` int DEFAULT NULL,
  `Calories_burnt` decimal(5,2) DEFAULT NULL,
  `Heart_rate` int DEFAULT NULL,
  `Oxygen_level` decimal(5,2) DEFAULT NULL,
  `Exercise_ID` int DEFAULT NULL,
  `Equipment_ID` int DEFAULT NULL,
  `Sets` int DEFAULT NULL,
  `Reps` int DEFAULT NULL,
  `Weight` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`Log_ID`),
  KEY `Member_ID` (`Member_ID`),
  KEY `Workout_Session_ID` (`Workout_Session_ID`),
  KEY `Exercise_ID` (`Exercise_ID`),
  KEY `Equipment_ID` (`Equipment_ID`),
  CONSTRAINT `workout_log_ibfk_1` FOREIGN KEY (`Member_ID`) REFERENCES `Member` (`Member_ID`),
  CONSTRAINT `workout_log_ibfk_2` FOREIGN KEY (`Workout_Session_ID`) REFERENCES `Workout_Session` (`Workout_ID`),
  CONSTRAINT `workout_log_ibfk_3` FOREIGN KEY (`Exercise_ID`) REFERENCES `Exercise` (`Exercise_ID`),
  CONSTRAINT `workout_log_ibfk_4` FOREIGN KEY (`Equipment_ID`) REFERENCES `VR_Equipment` (`Equipment_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Workout_Log`
--

LOCK TABLES `Workout_Log` WRITE;
/*!40000 ALTER TABLE `Workout_Log` DISABLE KEYS */;
/*!40000 ALTER TABLE `Workout_Log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Workout_Session`
--

DROP TABLE IF EXISTS `Workout_Session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Workout_Session` (
  `Workout_ID` int NOT NULL,
  `Member_ID` int DEFAULT NULL,
  `Program_type` varchar(50) DEFAULT NULL,
  `VR_Environment` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Workout_ID`),
  KEY `Member_ID` (`Member_ID`),
  CONSTRAINT `workout_session_ibfk_1` FOREIGN KEY (`Member_ID`) REFERENCES `Member` (`Member_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Workout_Session`
--

LOCK TABLES `Workout_Session` WRITE;
/*!40000 ALTER TABLE `Workout_Session` DISABLE KEYS */;
INSERT INTO `Workout_Session` VALUES (1,211,'Cardio','Surfing'),(2,156,'Strength Training','Hiking'),(3,62,'HIIT','Mountain Climbing'),(4,278,'Cardio','Rowing'),(5,120,'HIIT','Mountain Climbing'),(6,188,'HIIT','Hiking'),(7,34,'HIIT','Rowing'),(8,148,'Cardio','Mountain Climbing'),(9,274,'Strength Training','Surfing'),(10,238,'HIIT','Rowing'),(11,32,'Strength Training','Rowing'),(12,50,'HIIT','Mountain Climbing'),(13,146,'HIIT','Mountain Climbing'),(14,186,'Cardio','Rowing'),(15,44,'HIIT','Rowing'),(16,123,'Cardio','Rowing'),(17,1,'Strength Training','Rowing'),(18,45,'Cardio','Rowing'),(19,191,'HIIT','Hiking'),(20,214,'Strength Training','Mountain Climbing'),(21,136,'Strength Training','Surfing'),(22,165,'HIIT','Rowing'),(23,47,'Strength Training','Hiking'),(24,1,'HIIT','Rowing'),(25,17,'HIIT','Hiking'),(26,243,'HIIT','Mountain Climbing'),(27,27,'Strength Training','Rowing'),(28,183,'Strength Training','Mountain Climbing'),(29,41,'Strength Training','Rowing'),(30,244,'HIIT','Hiking'),(31,181,'Strength Training','Mountain Climbing'),(32,252,'HIIT','Hiking'),(33,45,'Cardio','Surfing'),(34,282,'Strength Training','Rowing'),(35,128,'Strength Training','Surfing'),(36,79,'Strength Training','Rowing'),(37,269,'HIIT','Rowing'),(38,225,'Strength Training','Hiking'),(39,261,'HIIT','Surfing'),(40,132,'Cardio','Surfing'),(41,293,'Cardio','Hiking'),(42,138,'Cardio','Rowing'),(43,140,'Cardio','Rowing'),(44,298,'Strength Training','Rowing'),(45,108,'HIIT','Surfing'),(46,63,'HIIT','Mountain Climbing'),(47,215,'HIIT','Hiking'),(48,296,'HIIT','Mountain Climbing'),(49,249,'HIIT','Surfing'),(50,115,'HIIT','Rowing'),(51,22,'Cardio','Hiking'),(52,260,'Cardio','Rowing'),(53,291,'HIIT','Mountain Climbing'),(54,254,'HIIT','Rowing'),(55,257,'Cardio','Hiking'),(56,247,'HIIT','Mountain Climbing'),(57,17,'Strength Training','Rowing'),(58,202,'HIIT','Surfing'),(59,54,'Strength Training','Hiking'),(60,58,'Cardio','Rowing'),(61,260,'Cardio','Hiking'),(62,127,'Cardio','Hiking'),(63,107,'Strength Training','Mountain Climbing'),(64,61,'Strength Training','Mountain Climbing'),(65,23,'HIIT','Rowing'),(66,62,'Strength Training','Rowing'),(67,11,'Strength Training','Surfing'),(68,75,'HIIT','Hiking'),(69,82,'HIIT','Mountain Climbing'),(70,80,'Cardio','Mountain Climbing'),(71,137,'HIIT','Surfing'),(72,277,'Cardio','Surfing'),(73,62,'Strength Training','Mountain Climbing'),(74,264,'HIIT','Mountain Climbing'),(75,121,'Strength Training','Surfing'),(76,287,'HIIT','Hiking'),(77,165,'Cardio','Mountain Climbing'),(78,10,'HIIT','Rowing'),(79,89,'Cardio','Mountain Climbing'),(80,143,'Cardio','Hiking'),(81,70,'Cardio','Mountain Climbing'),(82,72,'Cardio','Surfing'),(83,111,'HIIT','Rowing'),(84,161,'Strength Training','Rowing'),(85,69,'Strength Training','Surfing'),(86,139,'HIIT','Hiking'),(87,193,'HIIT','Mountain Climbing'),(88,287,'Cardio','Mountain Climbing'),(89,116,'HIIT','Surfing'),(90,174,'Cardio','Rowing'),(91,126,'Strength Training','Mountain Climbing'),(92,242,'Strength Training','Surfing'),(93,108,'HIIT','Hiking'),(94,142,'Cardio','Rowing'),(95,10,'HIIT','Rowing'),(96,222,'Cardio','Mountain Climbing'),(97,94,'HIIT','Rowing'),(98,210,'Cardio','Hiking'),(99,48,'Strength Training','Hiking'),(100,207,'Strength Training','Surfing'),(101,97,'Strength Training','Mountain Climbing'),(102,253,'Cardio','Mountain Climbing'),(103,144,'Strength Training','Surfing'),(104,147,'Cardio','Rowing'),(105,29,'Cardio','Rowing'),(106,207,'Strength Training','Hiking'),(107,246,'HIIT','Surfing'),(108,67,'Cardio','Rowing'),(109,257,'Strength Training','Rowing'),(110,164,'Strength Training','Surfing'),(111,121,'HIIT','Mountain Climbing'),(112,189,'Cardio','Mountain Climbing'),(113,131,'HIIT','Surfing'),(114,293,'Strength Training','Mountain Climbing'),(115,196,'Cardio','Mountain Climbing'),(116,83,'Cardio','Mountain Climbing'),(117,19,'Cardio','Surfing'),(118,175,'HIIT','Rowing'),(119,135,'Cardio','Surfing'),(120,171,'Cardio','Rowing'),(121,36,'HIIT','Mountain Climbing'),(122,128,'Cardio','Surfing'),(123,129,'Cardio','Surfing'),(124,269,'Cardio','Mountain Climbing'),(125,249,'Cardio','Surfing'),(126,279,'Cardio','Rowing'),(127,234,'Cardio','Hiking'),(128,12,'Strength Training','Mountain Climbing'),(129,14,'HIIT','Mountain Climbing'),(130,141,'Cardio','Hiking'),(131,162,'HIIT','Rowing'),(132,166,'Cardio','Mountain Climbing'),(133,54,'Strength Training','Hiking'),(134,213,'Cardio','Mountain Climbing'),(135,68,'HIIT','Mountain Climbing'),(136,119,'HIIT','Surfing'),(137,284,'HIIT','Hiking'),(138,145,'Strength Training','Surfing'),(139,250,'Strength Training','Surfing'),(140,170,'Cardio','Hiking'),(141,242,'HIIT','Rowing'),(142,221,'Strength Training','Hiking'),(143,167,'Cardio','Mountain Climbing'),(144,128,'Cardio','Surfing'),(145,38,'Cardio','Surfing'),(146,15,'HIIT','Surfing'),(147,102,'HIIT','Rowing'),(148,168,'Cardio','Rowing'),(149,70,'HIIT','Rowing'),(150,255,'Strength Training','Hiking'),(151,274,'Cardio','Hiking'),(152,129,'HIIT','Mountain Climbing'),(153,198,'Cardio','Mountain Climbing'),(154,179,'Cardio','Rowing'),(155,7,'Strength Training','Rowing'),(156,279,'Strength Training','Mountain Climbing'),(157,44,'Strength Training','Mountain Climbing'),(158,143,'Strength Training','Surfing'),(159,283,'HIIT','Hiking'),(160,144,'HIIT','Surfing'),(161,184,'HIIT','Rowing'),(162,240,'HIIT','Surfing'),(163,92,'HIIT','Surfing'),(164,275,'Strength Training','Mountain Climbing'),(165,240,'HIIT','Mountain Climbing'),(166,5,'Cardio','Mountain Climbing'),(167,203,'Cardio','Hiking'),(168,137,'Cardio','Mountain Climbing'),(169,48,'HIIT','Surfing'),(170,111,'Cardio','Mountain Climbing'),(171,147,'HIIT','Hiking'),(172,21,'Strength Training','Rowing'),(173,44,'HIIT','Surfing'),(174,16,'Cardio','Hiking'),(175,212,'Cardio','Hiking'),(176,34,'HIIT','Hiking'),(177,259,'Strength Training','Rowing'),(178,167,'HIIT','Hiking'),(179,165,'Cardio','Rowing'),(180,273,'HIIT','Mountain Climbing'),(181,181,'HIIT','Hiking'),(182,241,'Strength Training','Mountain Climbing'),(183,136,'Cardio','Rowing'),(184,15,'Cardio','Hiking'),(185,137,'HIIT','Mountain Climbing'),(186,267,'Cardio','Hiking'),(187,38,'Cardio','Mountain Climbing'),(188,52,'HIIT','Rowing'),(189,22,'Cardio','Hiking'),(190,203,'Strength Training','Mountain Climbing'),(191,299,'HIIT','Rowing'),(192,142,'HIIT','Mountain Climbing'),(193,236,'Cardio','Mountain Climbing'),(194,177,'Cardio','Surfing'),(195,35,'HIIT','Surfing'),(196,115,'Strength Training','Surfing'),(197,254,'HIIT','Rowing'),(198,247,'Cardio','Hiking'),(199,121,'Strength Training','Hiking'),(200,18,'Cardio','Hiking'),(201,142,'HIIT','Surfing'),(202,210,'Strength Training','Hiking'),(203,164,'Strength Training','Rowing'),(204,127,'Strength Training','Hiking'),(205,196,'Cardio','Mountain Climbing'),(206,157,'Strength Training','Rowing'),(207,277,'HIIT','Rowing'),(208,185,'Cardio','Mountain Climbing'),(209,72,'Strength Training','Mountain Climbing'),(210,82,'HIIT','Surfing'),(211,226,'HIIT','Rowing'),(212,234,'HIIT','Mountain Climbing'),(213,134,'Strength Training','Surfing'),(214,94,'Cardio','Hiking'),(215,127,'Strength Training','Mountain Climbing'),(216,107,'HIIT','Mountain Climbing'),(217,63,'Cardio','Mountain Climbing'),(218,88,'Strength Training','Surfing'),(219,32,'HIIT','Rowing'),(220,5,'Cardio','Rowing'),(221,169,'Cardio','Rowing'),(222,114,'HIIT','Surfing'),(223,151,'HIIT','Surfing'),(224,86,'Cardio','Mountain Climbing'),(225,120,'Strength Training','Surfing'),(226,256,'Strength Training','Hiking'),(227,146,'HIIT','Mountain Climbing'),(228,124,'Cardio','Hiking'),(229,21,'HIIT','Rowing'),(230,274,'HIIT','Surfing'),(231,45,'Cardio','Mountain Climbing'),(232,251,'HIIT','Hiking'),(233,31,'HIIT','Mountain Climbing'),(234,48,'Cardio','Surfing'),(235,262,'Strength Training','Rowing'),(236,188,'HIIT','Mountain Climbing'),(237,94,'HIIT','Surfing'),(238,277,'Strength Training','Rowing'),(239,34,'HIIT','Rowing'),(240,261,'HIIT','Rowing'),(241,148,'Strength Training','Mountain Climbing'),(242,203,'Strength Training','Rowing'),(243,59,'HIIT','Rowing'),(244,107,'HIIT','Rowing'),(245,203,'HIIT','Rowing'),(246,10,'Strength Training','Hiking'),(247,122,'Cardio','Rowing'),(248,268,'Cardio','Hiking'),(249,81,'HIIT','Surfing'),(250,250,'Cardio','Mountain Climbing'),(251,56,'HIIT','Mountain Climbing'),(252,223,'Cardio','Mountain Climbing'),(253,212,'HIIT','Mountain Climbing'),(254,271,'Cardio','Mountain Climbing'),(255,277,'HIIT','Surfing'),(256,149,'Strength Training','Rowing'),(257,10,'HIIT','Mountain Climbing'),(258,251,'Strength Training','Mountain Climbing'),(259,20,'Strength Training','Rowing'),(260,294,'Cardio','Rowing'),(261,44,'Strength Training','Rowing'),(262,171,'Cardio','Mountain Climbing'),(263,260,'Strength Training','Mountain Climbing'),(264,29,'Cardio','Surfing'),(265,254,'HIIT','Mountain Climbing'),(266,8,'Cardio','Rowing'),(267,300,'HIIT','Surfing'),(268,50,'Strength Training','Hiking'),(269,165,'HIIT','Rowing'),(270,259,'Cardio','Hiking'),(271,54,'Cardio','Hiking'),(272,116,'Cardio','Rowing'),(273,297,'Strength Training','Surfing'),(274,153,'Strength Training','Surfing'),(275,233,'Strength Training','Hiking'),(276,22,'HIIT','Mountain Climbing'),(277,53,'HIIT','Mountain Climbing'),(278,217,'HIIT','Mountain Climbing'),(279,195,'Cardio','Mountain Climbing'),(280,146,'HIIT','Mountain Climbing'),(281,47,'Strength Training','Rowing'),(282,89,'Cardio','Hiking'),(283,251,'Cardio','Mountain Climbing'),(284,103,'Strength Training','Rowing'),(285,80,'Strength Training','Hiking'),(286,287,'Strength Training','Mountain Climbing'),(287,35,'Cardio','Hiking'),(288,222,'Strength Training','Hiking'),(289,145,'Cardio','Rowing'),(290,246,'Strength Training','Surfing'),(291,144,'Strength Training','Surfing'),(292,145,'Cardio','Hiking'),(293,262,'HIIT','Rowing'),(294,91,'HIIT','Mountain Climbing'),(295,162,'Cardio','Surfing'),(296,169,'HIIT','Rowing'),(297,4,'Cardio','Hiking'),(298,221,'HIIT','Surfing'),(299,219,'HIIT','Hiking'),(300,142,'Cardio','Surfing'),(301,85,'Cardio','Hiking'),(302,163,'Cardio','Mountain Climbing'),(303,78,'Strength Training','Surfing'),(304,300,'HIIT','Hiking'),(305,30,'Cardio','Rowing'),(306,134,'Strength Training','Surfing'),(307,153,'Strength Training','Hiking'),(308,14,'Cardio','Mountain Climbing'),(309,27,'HIIT','Rowing'),(310,224,'Cardio','Mountain Climbing'),(311,168,'Cardio','Hiking'),(312,151,'Cardio','Rowing'),(313,44,'Strength Training','Surfing'),(314,170,'HIIT','Hiking'),(315,12,'HIIT','Mountain Climbing'),(316,160,'HIIT','Mountain Climbing'),(317,63,'Strength Training','Mountain Climbing'),(318,229,'HIIT','Rowing'),(319,260,'Strength Training','Mountain Climbing'),(320,206,'Strength Training','Mountain Climbing'),(321,128,'Strength Training','Mountain Climbing'),(322,168,'Strength Training','Mountain Climbing'),(323,49,'Cardio','Hiking'),(324,88,'Strength Training','Surfing'),(325,137,'Strength Training','Surfing'),(326,11,'Cardio','Hiking'),(327,108,'Cardio','Mountain Climbing'),(328,207,'Strength Training','Mountain Climbing'),(329,279,'Cardio','Hiking'),(330,135,'Strength Training','Hiking'),(331,119,'HIIT','Surfing'),(332,130,'Cardio','Surfing'),(333,210,'HIIT','Hiking'),(334,247,'HIIT','Hiking'),(335,138,'Strength Training','Hiking'),(336,24,'Strength Training','Hiking'),(337,1,'Strength Training','Mountain Climbing'),(338,172,'HIIT','Mountain Climbing'),(339,183,'Cardio','Surfing'),(340,37,'Cardio','Surfing'),(341,90,'Strength Training','Rowing'),(342,125,'HIIT','Surfing'),(343,85,'Strength Training','Rowing'),(344,36,'HIIT','Hiking'),(345,276,'HIIT','Hiking'),(346,156,'Cardio','Rowing'),(347,197,'Strength Training','Mountain Climbing'),(348,262,'Cardio','Surfing'),(349,148,'Cardio','Mountain Climbing'),(350,177,'Cardio','Mountain Climbing'),(351,296,'Strength Training','Rowing'),(352,68,'HIIT','Mountain Climbing'),(353,165,'Strength Training','Mountain Climbing'),(354,103,'Strength Training','Hiking'),(355,67,'Strength Training','Mountain Climbing'),(356,189,'Cardio','Rowing'),(357,254,'Cardio','Surfing'),(358,22,'Strength Training','Surfing'),(359,46,'Cardio','Rowing'),(360,188,'HIIT','Mountain Climbing'),(361,68,'Cardio','Surfing'),(362,70,'HIIT','Hiking'),(363,90,'HIIT','Mountain Climbing'),(364,245,'Strength Training','Hiking'),(365,172,'HIIT','Hiking'),(366,291,'Cardio','Hiking'),(367,137,'Cardio','Mountain Climbing'),(368,123,'HIIT','Hiking'),(369,144,'Strength Training','Hiking'),(370,163,'Strength Training','Surfing'),(371,247,'Strength Training','Rowing'),(372,296,'HIIT','Rowing'),(373,57,'Cardio','Hiking'),(374,120,'Cardio','Surfing'),(375,128,'Strength Training','Surfing'),(376,292,'Cardio','Rowing'),(377,192,'Cardio','Hiking'),(378,166,'HIIT','Surfing'),(379,73,'HIIT','Surfing'),(380,97,'Strength Training','Hiking'),(381,206,'Strength Training','Rowing'),(382,76,'HIIT','Surfing'),(383,219,'HIIT','Surfing'),(384,51,'HIIT','Mountain Climbing'),(385,184,'Strength Training','Mountain Climbing'),(386,79,'Strength Training','Mountain Climbing'),(387,100,'HIIT','Rowing'),(388,146,'Cardio','Surfing'),(389,79,'HIIT','Hiking'),(390,277,'Strength Training','Mountain Climbing'),(391,210,'Cardio','Mountain Climbing'),(392,72,'HIIT','Rowing'),(393,3,'HIIT','Surfing'),(394,221,'Cardio','Rowing'),(395,225,'HIIT','Hiking'),(396,52,'Strength Training','Rowing'),(397,193,'Strength Training','Rowing'),(398,96,'HIIT','Surfing'),(399,158,'Cardio','Mountain Climbing'),(400,70,'HIIT','Surfing'),(401,263,'Strength Training','Mountain Climbing'),(402,174,'HIIT','Mountain Climbing'),(403,113,'Cardio','Rowing'),(404,270,'Cardio','Surfing'),(405,47,'Strength Training','Mountain Climbing'),(406,135,'HIIT','Hiking'),(407,184,'Strength Training','Rowing'),(408,184,'Cardio','Mountain Climbing'),(409,199,'Strength Training','Surfing'),(410,236,'Cardio','Rowing'),(411,16,'Strength Training','Hiking'),(412,216,'Cardio','Mountain Climbing'),(413,74,'Strength Training','Mountain Climbing'),(414,150,'HIIT','Surfing'),(415,133,'HIIT','Surfing'),(416,223,'HIIT','Hiking'),(417,190,'Strength Training','Mountain Climbing'),(418,86,'Cardio','Rowing'),(419,75,'HIIT','Rowing'),(420,269,'Strength Training','Surfing'),(421,33,'Strength Training','Hiking'),(422,149,'HIIT','Mountain Climbing'),(423,231,'HIIT','Rowing'),(424,157,'HIIT','Surfing'),(425,296,'Cardio','Hiking'),(426,272,'Strength Training','Rowing'),(427,97,'HIIT','Surfing'),(428,119,'Cardio','Hiking'),(429,123,'HIIT','Hiking'),(430,103,'Strength Training','Hiking'),(431,90,'Cardio','Hiking'),(432,293,'HIIT','Rowing'),(433,63,'Cardio','Rowing'),(434,33,'Cardio','Surfing'),(435,112,'Strength Training','Rowing'),(436,156,'Strength Training','Hiking'),(437,195,'Cardio','Mountain Climbing'),(438,137,'HIIT','Rowing'),(439,243,'Cardio','Rowing'),(440,106,'Strength Training','Rowing'),(441,75,'HIIT','Mountain Climbing'),(442,63,'HIIT','Mountain Climbing'),(443,213,'Cardio','Rowing'),(444,31,'Strength Training','Mountain Climbing'),(445,12,'Strength Training','Mountain Climbing'),(446,231,'Strength Training','Rowing'),(447,92,'HIIT','Hiking'),(448,160,'Cardio','Hiking'),(449,269,'Cardio','Mountain Climbing'),(450,127,'HIIT','Hiking'),(451,121,'Cardio','Hiking'),(452,14,'Cardio','Hiking'),(453,47,'Cardio','Rowing'),(454,35,'Strength Training','Rowing'),(455,297,'HIIT','Mountain Climbing'),(456,259,'Strength Training','Rowing'),(457,286,'Strength Training','Surfing'),(458,39,'Cardio','Rowing'),(459,116,'Strength Training','Rowing'),(460,115,'Cardio','Surfing'),(461,25,'Cardio','Hiking'),(462,88,'Cardio','Rowing'),(463,209,'Strength Training','Hiking'),(464,202,'Strength Training','Surfing'),(465,295,'Strength Training','Rowing'),(466,140,'HIIT','Mountain Climbing'),(467,147,'Cardio','Hiking'),(468,244,'Cardio','Mountain Climbing'),(469,130,'Strength Training','Surfing'),(470,40,'HIIT','Hiking'),(471,121,'Strength Training','Surfing'),(472,206,'HIIT','Hiking'),(473,32,'HIIT','Hiking'),(474,19,'Cardio','Hiking'),(475,37,'Strength Training','Rowing'),(476,70,'Strength Training','Hiking'),(477,247,'Strength Training','Mountain Climbing'),(478,168,'Strength Training','Surfing'),(479,59,'HIIT','Surfing'),(480,79,'Strength Training','Mountain Climbing'),(481,268,'Strength Training','Surfing'),(482,275,'Cardio','Rowing'),(483,128,'HIIT','Rowing'),(484,280,'Strength Training','Surfing'),(485,46,'HIIT','Hiking'),(486,75,'Cardio','Surfing'),(487,148,'HIIT','Rowing'),(488,200,'HIIT','Surfing'),(489,264,'Strength Training','Surfing'),(490,19,'HIIT','Hiking'),(491,246,'HIIT','Hiking'),(492,51,'Strength Training','Mountain Climbing'),(493,286,'Strength Training','Mountain Climbing'),(494,86,'HIIT','Surfing'),(495,226,'HIIT','Mountain Climbing'),(496,14,'HIIT','Surfing'),(497,55,'Strength Training','Mountain Climbing'),(498,122,'HIIT','Hiking'),(499,19,'Strength Training','Hiking'),(500,24,'Strength Training','Surfing');
/*!40000 ALTER TABLE `Workout_Session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Workout_Session_Exercise`
--

DROP TABLE IF EXISTS `Workout_Session_Exercise`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Workout_Session_Exercise` (
  `Session_ID` int NOT NULL,
  `Exercise_ID` int NOT NULL,
  PRIMARY KEY (`Session_ID`,`Exercise_ID`),
  KEY `Exercise_ID` (`Exercise_ID`),
  CONSTRAINT `workout_session_exercise_ibfk_1` FOREIGN KEY (`Session_ID`) REFERENCES `Workout_Session` (`Workout_ID`),
  CONSTRAINT `workout_session_exercise_ibfk_2` FOREIGN KEY (`Exercise_ID`) REFERENCES `Exercise` (`Exercise_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Workout_Session_Exercise`
--

LOCK TABLES `Workout_Session_Exercise` WRITE;
/*!40000 ALTER TABLE `Workout_Session_Exercise` DISABLE KEYS */;
/*!40000 ALTER TABLE `Workout_Session_Exercise` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Workout_Session_Uses_Equipment`
--

DROP TABLE IF EXISTS `Workout_Session_Uses_Equipment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Workout_Session_Uses_Equipment` (
  `Session_ID` int NOT NULL,
  `Equipment_ID` int NOT NULL,
  PRIMARY KEY (`Session_ID`,`Equipment_ID`),
  KEY `Equipment_ID` (`Equipment_ID`),
  CONSTRAINT `workout_session_uses_equipment_ibfk_1` FOREIGN KEY (`Session_ID`) REFERENCES `Workout_Session` (`Workout_ID`),
  CONSTRAINT `workout_session_uses_equipment_ibfk_2` FOREIGN KEY (`Equipment_ID`) REFERENCES `VR_Equipment` (`Equipment_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Workout_Session_Uses_Equipment`
--

LOCK TABLES `Workout_Session_Uses_Equipment` WRITE;
/*!40000 ALTER TABLE `Workout_Session_Uses_Equipment` DISABLE KEYS */;
INSERT INTO `Workout_Session_Uses_Equipment` VALUES (13,1),(127,1),(264,1),(285,1),(408,1),(421,1),(455,1),(460,1),(154,2),(306,2),(341,2),(356,2),(382,2),(416,2),(425,2),(459,2),(148,3),(173,3),(187,3),(192,3),(200,3),(237,3),(263,3),(268,3),(288,3),(471,3),(54,4),(182,4),(217,4),(39,5),(101,5),(149,5),(312,5),(315,5),(320,5),(323,5),(346,5),(398,5),(404,5),(406,5),(10,6),(37,6),(128,6),(142,6),(224,6),(302,6),(373,6),(393,6),(410,6),(444,6),(451,6),(484,6),(485,6),(8,7),(9,7),(30,7),(150,7),(259,7),(414,7),(477,7),(492,7),(31,8),(74,8),(99,8),(179,8),(248,8),(313,8),(348,8),(417,8),(108,9),(153,9),(161,9),(249,9),(250,9),(292,9),(299,9),(322,9),(357,9),(361,9),(377,9),(411,9),(424,9),(36,10),(59,10),(87,10),(209,10),(273,10),(282,10),(298,10),(307,10),(358,10),(413,10),(474,10),(488,10),(76,11),(102,11),(118,11),(156,11),(199,11),(247,11),(253,11),(266,11),(319,11),(333,11),(350,11),(351,11),(353,11),(383,11),(405,11),(478,11),(19,12),(75,12),(90,12),(126,12),(229,12),(304,12),(309,12),(327,12),(401,12),(464,12),(55,13),(69,13),(85,13),(191,13),(207,13),(226,13),(254,13),(362,13),(366,13),(412,13),(35,14),(64,14),(184,14),(244,14),(287,14),(347,14),(436,14),(468,14),(475,14),(486,14),(20,15),(27,15),(65,15),(88,15),(144,15),(152,15),(389,15),(430,15),(438,15),(439,15),(487,15),(28,16),(34,16),(124,16),(232,16),(276,16),(283,16),(284,16),(316,16),(337,16),(386,16),(407,16),(66,17),(137,17),(159,17),(181,17),(210,17),(296,17),(321,17),(355,17),(466,17),(25,18),(121,18),(131,18),(185,18),(213,18),(235,18),(245,18),(328,18),(415,18),(447,18),(26,19),(89,19),(117,19),(132,19),(140,19),(164,19),(169,19),(196,19),(258,19),(274,19),(360,19),(448,19),(473,19),(52,20),(60,20),(303,20),(318,20),(369,20),(450,20),(452,20),(458,20),(461,20),(38,21),(57,21),(95,21),(97,21),(109,21),(139,21),(141,21),(294,21),(371,21),(183,22),(190,22),(257,22),(280,22),(354,22),(446,22),(480,22),(45,23),(112,23),(205,23),(239,23),(243,23),(278,23),(301,23),(442,23),(497,23),(15,24),(40,24),(46,24),(70,24),(133,24),(178,24),(331,24),(387,24),(51,25),(68,25),(214,25),(349,25),(370,25),(394,25),(453,25),(481,25),(1,26),(22,26),(104,26),(206,26),(314,26),(340,26),(392,26),(441,26),(456,26),(470,26),(495,26),(498,26),(53,27),(86,27),(91,27),(197,27),(297,27),(388,27),(400,27),(432,27),(491,27),(63,28),(110,28),(119,28),(170,28),(317,28),(375,28),(384,28),(391,28),(111,29),(114,29),(135,29),(145,29),(162,29),(227,29),(255,29),(272,29),(286,29),(308,29),(2,30),(16,30),(93,30),(180,30),(228,30),(32,31),(33,31),(116,31),(125,31),(147,31),(167,31),(201,31),(220,31),(225,31),(230,31),(332,31),(379,31),(434,31),(7,32),(42,32),(92,32),(100,32),(252,32),(277,32),(325,32),(500,32),(23,33),(82,33),(94,33),(158,33),(194,33),(396,33),(454,33),(463,33),(479,33),(17,34),(49,34),(72,34),(81,34),(122,34),(166,34),(260,34),(295,34),(372,34),(106,35),(186,35),(219,35),(221,35),(262,35),(305,35),(326,35),(418,35),(420,35),(462,35),(21,36),(41,36),(48,36),(71,36),(136,36),(193,36),(208,36),(240,36),(324,36),(395,36),(5,37),(146,37),(428,37),(490,37),(493,37),(6,38),(105,38),(123,38),(175,38),(246,38),(267,38),(291,38),(311,38),(368,38),(419,38),(465,38),(472,38),(120,39),(174,39),(177,39),(241,39),(275,39),(338,39),(390,39),(423,39),(78,40),(216,40),(231,40),(271,40),(300,40),(352,40),(50,41),(62,41),(96,41),(160,41),(163,41),(172,41),(211,41),(215,41),(261,41),(265,41),(270,41),(329,41),(364,41),(376,41),(426,41),(429,41),(445,41),(18,42),(113,42),(134,42),(155,42),(203,42),(212,42),(336,42),(345,42),(431,42),(496,42),(4,43),(138,43),(171,43),(202,43),(223,43),(381,43),(385,43),(433,43),(11,44),(56,44),(79,44),(103,44),(107,44),(129,44),(168,44),(222,44),(236,44),(269,44),(457,44),(476,44),(499,44),(43,45),(44,45),(77,45),(80,45),(130,45),(188,45),(218,45),(234,45),(251,45),(409,45),(469,45),(3,46),(61,46),(67,46),(115,46),(198,46),(204,46),(293,46),(330,46),(359,46),(363,46),(397,46),(12,47),(14,47),(24,47),(58,47),(143,47),(151,47),(279,47),(290,47),(310,47),(378,47),(399,47),(73,48),(83,48),(98,48),(165,48),(189,48),(233,48),(238,48),(281,48),(289,48),(334,48),(342,48),(365,48),(402,48),(422,48),(440,48),(489,48),(494,48),(84,49),(157,49),(242,49),(335,49),(339,49),(343,49),(374,49),(380,49),(427,49),(435,49),(443,49),(467,49),(482,49),(483,49),(29,50),(47,50),(176,50),(195,50),(256,50),(344,50),(367,50),(403,50),(437,50),(449,50);
/*!40000 ALTER TABLE `Workout_Session_Uses_Equipment` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-03 15:03:29
