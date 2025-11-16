-- SQL script to update database schema for Circle API integration
-- Run this if you already have data in the database

-- Add new columns to companies table
ALTER TABLE companies 
ADD COLUMN IF NOT EXISTS circle_wallet_id VARCHAR,
ADD COLUMN IF NOT EXISTS circle_wallet_set_id VARCHAR,
ADD COLUMN IF NOT EXISTS entity_secret_encrypted TEXT;

-- Add new column to payroll_transactions table
ALTER TABLE payroll_transactions 
ADD COLUMN IF NOT EXISTS circle_transaction_id VARCHAR;

-- Update status column to support Circle transaction states
-- Note: This doesn't change existing data, just allows new states
-- Existing statuses: pending, completed, failed
-- New Circle states: INITIATED, QUEUED, SENT, CONFIRMED, COMPLETE

-- Create index on circle_transaction_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_payroll_transactions_circle_tx_id 
ON payroll_transactions(circle_transaction_id);

-- Create index on circle_wallet_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_companies_circle_wallet_id 
ON companies(circle_wallet_id);

