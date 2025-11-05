-- ============================================
-- SQL Script to Fix Missing Database Columns
-- ============================================
-- Run this script in your MySQL database (phpMyAdmin, MySQL Workbench, or command line)
-- This will add the missing columns for file attachments
-- ============================================

-- Add driver_report_attachment column to PreInspectionReport table
-- This column stores the file path for driver report attachments
ALTER TABLE `core_preinspectionreport` 
ADD COLUMN `driver_report_attachment` VARCHAR(100) NULL DEFAULT NULL 
AFTER `photos`;

-- Add replaced_parts_images column to PostInspectionReport table  
-- This column stores the file path for replaced parts images
ALTER TABLE `core_postinspectionreport` 
ADD COLUMN `replaced_parts_images` VARCHAR(100) NULL DEFAULT NULL 
AFTER `photos`;

-- Verify the columns were added (optional - you can run this to check)
-- SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
-- FROM INFORMATION_SCHEMA.COLUMNS 
-- WHERE TABLE_SCHEMA = 'fleetmanagement' 
-- AND TABLE_NAME = 'core_preinspectionreport' 
-- AND COLUMN_NAME IN ('driver_report_attachment', 'photos');

