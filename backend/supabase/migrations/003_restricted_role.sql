-- Sirf generated SQL chalane ke liye role. Yehi aakhri security boundary hai.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'query_readonly') THEN
    CREATE ROLE query_readonly NOLOGIN;
  END IF;
END $$;

-- Supabase ke API roles ko business data se door rakho.
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
    REVOKE ALL ON SCHEMA northstar, querypilot FROM anon, authenticated;
    REVOKE ALL ON ALL TABLES IN SCHEMA northstar, querypilot FROM anon, authenticated;
  END IF;
END $$;

GRANT USAGE ON SCHEMA northstar TO query_readonly;

-- Column-level grant: customers.email jaan bujh kar NAHI diya.
GRANT SELECT (id, customer_name, city, created_at) ON northstar.customers TO query_readonly;
GRANT SELECT ON northstar.categories, northstar.products,
                northstar.orders, northstar.order_items TO query_readonly;
-- querypilot schema par koi grant nahi: generated SQL app metadata nahi padh sakti.

ALTER ROLE query_readonly SET search_path = northstar;
ALTER ROLE query_readonly SET statement_timeout = '3s';
ALTER ROLE query_readonly SET default_transaction_read_only = on;
ALTER ROLE query_readonly SET idle_in_transaction_session_timeout = '5s';
ALTER ROLE query_readonly CONNECTION LIMIT 10;