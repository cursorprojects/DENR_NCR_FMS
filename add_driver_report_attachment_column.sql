-- SQL script to manually add driver_report_attachment column to PreInspectionReport table
-- Run this if you cannot run Django migrations
-- This matches Django's FileField default which stores file paths

ALTER TABLE `core_preinspectionreport` 
ADD COLUMN `driver_report_attachment` VARCHAR(100) NULL DEFAULT NULL 
AFTER `photos`;

-- Also add the replaced_parts_images column for PostInspectionReport
ALTER TABLE `core_postinspectionreport` 
ADD COLUMN `replaced_parts_images` VARCHAR(100) NULL DEFAULT NULL 
AFTER `photos`;

