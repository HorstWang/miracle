DROP DATABASE IF EXISTS vplex_log;
DROP USER IF EXISTS 'vplex_log_db_access'@'localhost';
CREATE USER 'vplex_log_db_access'@'localhost' IDENTIFIED BY 'VPlex_1234567890';
CREATE DATABASE vplex_log;
GRANT ALL PRIVILEGES ON vplex_log.* TO 'vplex_log_db_access'@'localhost';