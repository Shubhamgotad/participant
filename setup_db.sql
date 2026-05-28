-- Run this in MySQL to create the database and user
-- Step 1: Login as root
-- mysql -u root -p

-- Step 2: Create database
CREATE DATABASE IF NOT EXISTS pravaah_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Step 3 (Optional): Create a dedicated user
-- CREATE USER 'pravaah_user'@'localhost' IDENTIFIED BY 'pravaah@2024';
-- GRANT ALL PRIVILEGES ON pravaah_db.* TO 'pravaah_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Then update settings.py with:
-- 'USER': 'pravaah_user',
-- 'PASSWORD': 'pravaah@2024',

SHOW DATABASES;
