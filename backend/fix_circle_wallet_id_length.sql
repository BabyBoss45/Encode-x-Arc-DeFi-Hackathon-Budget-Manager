-- Fix circle_wallet_id column length to support full UUID (36 characters)
-- UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (36 chars total)

-- Check current column type
-- SELECT column_name, data_type, character_maximum_length 
-- FROM information_schema.columns 
-- WHERE table_name = 'companies' AND column_name = 'circle_wallet_id';

-- Update column to VARCHAR(36) or TEXT to support full UUID
ALTER TABLE companies 
ALTER COLUMN circle_wallet_id TYPE VARCHAR(36);

-- Also update circle_wallet_set_id if needed
ALTER TABLE companies 
ALTER COLUMN circle_wallet_set_id TYPE VARCHAR(36);

-- Update circle_transaction_id in payroll_transactions
ALTER TABLE payroll_transactions 
ALTER COLUMN circle_transaction_id TYPE VARCHAR(36);

-- Verify the change
-- SELECT column_name, data_type, character_maximum_length 
-- FROM information_schema.columns 
-- WHERE table_name = 'companies' AND column_name = 'circle_wallet_id';

