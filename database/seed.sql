-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: localhost    Database: ai_model_reliability
-- ------------------------------------------------------
-- Server version	8.0.33

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
-- Dumping data for table `ai_model`
--

LOCK TABLES `ai_model` WRITE;
/*!40000 ALTER TABLE `ai_model` DISABLE KEYS */;
INSERT INTO `ai_model` VALUES (1,'Financial Fraud Sentinel','Classification','Predicts likelihood of fraudulent financial transactions to mitigate financial crimes.',1,'2026-10-09'),(2,'Subscriber Retention Predictor','Classification','Predicts subscriber churn probabilities based on tenure, service tier, and billing behavior.',2,'2026-09-24');
/*!40000 ALTER TABLE `ai_model` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `data_quality_check`
--

LOCK TABLES `data_quality_check` WRITE;
/*!40000 ALTER TABLE `data_quality_check` DISABLE KEYS */;
INSERT INTO `data_quality_check` VALUES (1,1,'Missing Values Integrity','missing_values',95.00),(2,1,'Record Uniqueness (Duplicates)','duplicates',95.00),(3,1,'Data Type Consistency','data_types',98.00),(4,1,'Numerical Range Validity','numerical_range',90.00),(5,1,'Categorical Consistency','categorical_validity',90.00),(6,1,'Schema Integrity','schema_integrity',100.00),(7,2,'Missing Values Integrity','missing_values',95.00),(8,2,'Record Uniqueness (Duplicates)','duplicates',95.00),(9,2,'Data Type Consistency','data_types',98.00),(10,2,'Numerical Range Validity','numerical_range',90.00),(11,2,'Categorical Consistency','categorical_validity',90.00),(12,2,'Schema Integrity','schema_integrity',100.00);
/*!40000 ALTER TABLE `data_quality_check` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `data_quality_result`
--

LOCK TABLES `data_quality_result` WRITE;
/*!40000 ALTER TABLE `data_quality_result` DISABLE KEYS */;
INSERT INTO `data_quality_result` VALUES (1,1,1,99.45,'PASSED','2026-11-03 12:16:19'),(2,2,1,98.77,'PASSED','2026-11-03 12:16:19'),(3,3,1,100.00,'PASSED','2026-11-03 12:16:19'),(4,4,1,95.76,'PASSED','2026-11-03 12:16:19'),(5,5,1,100.00,'PASSED','2026-11-03 12:16:19'),(6,6,1,100.00,'PASSED','2026-11-03 12:16:19'),(7,1,2,100.00,'PASSED','2026-11-03 12:16:19'),(8,2,2,100.00,'PASSED','2026-11-03 12:16:19'),(9,3,2,100.00,'PASSED','2026-11-03 12:16:19'),(10,4,2,99.75,'PASSED','2026-11-03 12:16:19'),(11,5,2,100.00,'PASSED','2026-11-03 12:16:19'),(12,6,2,100.00,'PASSED','2026-11-03 12:16:19'),(13,7,3,100.00,'PASSED','2026-11-03 12:16:19'),(14,8,3,100.00,'PASSED','2026-11-03 12:16:19'),(15,9,3,100.00,'PASSED','2026-11-03 12:16:19'),(16,10,3,100.00,'PASSED','2026-11-03 12:16:19'),(17,11,3,100.00,'PASSED','2026-11-03 12:16:19'),(18,12,3,100.00,'PASSED','2026-11-03 12:16:19'),(19,7,4,100.00,'PASSED','2026-11-03 12:16:19'),(20,8,4,100.00,'PASSED','2026-11-03 12:16:19'),(21,9,4,100.00,'PASSED','2026-11-03 12:16:19'),(22,10,4,100.00,'PASSED','2026-11-03 12:16:19'),(23,11,4,100.00,'PASSED','2026-11-03 12:16:19'),(24,12,4,100.00,'PASSED','2026-11-03 12:16:19');
/*!40000 ALTER TABLE `data_quality_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `data_source`
--

LOCK TABLES `data_source` WRITE;
/*!40000 ALTER TABLE `data_source` DISABLE KEYS */;
INSERT INTO `data_source` VALUES (1,'Core Banking Transaction Lake','S3 Data Lake','s3://pesu-banking-data/transactions/'),(2,'Customer CRM Data Warehouse','PostgreSQL','postgresql://dw.internal:5432/crm_prod');
/*!40000 ALTER TABLE `data_source` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `dataset`
--

LOCK TABLES `dataset` WRITE;
/*!40000 ALTER TABLE `dataset` DISABLE KEYS */;
INSERT INTO `dataset` VALUES (1,'Bank Transaction Fraud Stream','High-frequency financial transaction records with fraud labels for risk assessment.',1,1,'2026-10-04'),(2,'Customer Subscription & Churn','Telecom subscriber engagement metrics, contract structures, and monthly revenue.',2,2,'2026-09-19');
/*!40000 ALTER TABLE `dataset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `dataset_version`
--

LOCK TABLES `dataset_version` WRITE;
/*!40000 ALTER TABLE `dataset_version` DISABLE KEYS */;
INSERT INTO `dataset_version` VALUES (1,1,'1.0',1215,'2026-10-14'),(2,1,'2.0',1500,'2026-10-29'),(3,2,'1.0',1000,'2026-09-29'),(4,2,'1.1',1100,'2026-10-24');
/*!40000 ALTER TABLE `dataset_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `drift_detection`
--

LOCK TABLES `drift_detection` WRITE;
/*!40000 ALTER TABLE `drift_detection` DISABLE KEYS */;
INSERT INTO `drift_detection` VALUES (1,1,0.0000,'LOW','2026-11-03 12:16:20'),(2,2,0.0000,'LOW','2026-11-03 12:16:21'),(3,3,2.6203,'HIGH','2026-11-03 12:16:23'),(4,4,0.0000,'LOW','2026-11-03 12:16:24'),(5,5,0.4365,'HIGH','2026-11-03 12:16:25');
/*!40000 ALTER TABLE `drift_detection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `evaluation_result`
--

LOCK TABLES `evaluation_result` WRITE;
/*!40000 ALTER TABLE `evaluation_result` DISABLE KEYS */;
INSERT INTO `evaluation_result` VALUES (1,1,84.36,81.93,84.36,82.42),(2,2,84.36,81.27,84.36,81.07),(3,3,72.33,70.68,72.33,69.90),(4,4,73.50,72.46,73.50,72.06),(5,5,69.09,66.77,69.09,66.27);
/*!40000 ALTER TABLE `evaluation_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `evaluation_run`
--

LOCK TABLES `evaluation_run` WRITE;
/*!40000 ALTER TABLE `evaluation_run` DISABLE KEYS */;
INSERT INTO `evaluation_run` VALUES (1,1,1,1,'2026-11-03 12:16:19','COMPLETED'),(2,2,1,1,'2026-11-03 12:16:20','COMPLETED'),(3,2,2,1,'2026-11-03 12:16:21','COMPLETED'),(4,4,3,2,'2026-11-03 12:16:24','COMPLETED'),(5,5,4,2,'2026-11-03 12:16:24','COMPLETED');
/*!40000 ALTER TABLE `evaluation_run` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `model_version`
--

LOCK TABLES `model_version` WRITE;
/*!40000 ALTER TABLE `model_version` DISABLE KEYS */;
INSERT INTO `model_version` VALUES (1,1,'1.0','Logistic Regression','2026-10-12'),(2,1,'2.0','Random Forest','2026-10-19'),(3,1,'3.0','Decision Tree','2026-10-27'),(4,2,'1.0','Logistic Regression','2026-10-04'),(5,2,'2.0','Random Forest','2026-10-22');
/*!40000 ALTER TABLE `model_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `reliability_score`
--

LOCK TABLES `reliability_score` WRITE;
/*!40000 ALTER TABLE `reliability_score` DISABLE KEYS */;
INSERT INTO `reliability_score` VALUES (1,1,99.00,83.20,100.00,92.09,'HIGH'),(2,2,99.00,82.39,100.00,91.72,'HIGH'),(3,3,99.96,70.87,0.00,66.88,'MEDIUM'),(4,4,100.00,72.64,100.00,87.69,'HIGH'),(5,5,100.00,67.40,12.70,67.87,'MEDIUM');
/*!40000 ALTER TABLE `reliability_score` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Mohammed Adaan Hamad','adaan@pesu.edu','Lead Engineer','Data Science'),(2,'Navya Kishore Dash','navya@pesu.edu','Co-Engineer','Data Platform'),(3,'Dr. Deena Hijam','deena.hijam@pesu.edu','Faculty Advisor','Computer Science');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-03 12:17:27
