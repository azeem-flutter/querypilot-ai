DO $$
DECLARE n int;
BEGIN
  SET LOCAL ROLE query_readonly;

  SELECT count(*) INTO n FROM northstar.orders;
  RAISE NOTICE 'PASS read orders (% rows)', n;
  PERFORM id, customer_name, city FROM northstar.customers LIMIT 1;
  RAISE NOTICE 'PASS read allowed customer columns';

  BEGIN PERFORM email FROM northstar.customers LIMIT 1;
    RAISE NOTICE 'FAIL email readable'; EXCEPTION WHEN insufficient_privilege THEN RAISE NOTICE 'PASS email denied'; END;
  BEGIN PERFORM * FROM querypilot.schema_documents LIMIT 1;
    RAISE NOTICE 'FAIL querypilot readable'; EXCEPTION WHEN insufficient_privilege THEN RAISE NOTICE 'PASS querypilot schema denied'; END;
  BEGIN DELETE FROM northstar.orders;
    RAISE NOTICE 'FAIL delete worked'; EXCEPTION WHEN insufficient_privilege OR read_only_sql_transaction THEN RAISE NOTICE 'PASS delete blocked'; END;
  BEGIN UPDATE northstar.products SET unit_price = 0;
    RAISE NOTICE 'FAIL update worked'; EXCEPTION WHEN insufficient_privilege OR read_only_sql_transaction THEN RAISE NOTICE 'PASS update blocked'; END;
  BEGIN INSERT INTO northstar.categories(category_name) VALUES ('x');
    RAISE NOTICE 'FAIL insert worked'; EXCEPTION WHEN insufficient_privilege OR read_only_sql_transaction THEN RAISE NOTICE 'PASS insert blocked'; END;
  BEGIN EXECUTE 'DROP TABLE northstar.orders';
    RAISE NOTICE 'FAIL drop worked'; EXCEPTION WHEN insufficient_privilege OR read_only_sql_transaction THEN RAISE NOTICE 'PASS drop blocked'; END;
  BEGIN EXECUTE 'CREATE TABLE northstar.hack(x int)';
    RAISE NOTICE 'FAIL create worked'; EXCEPTION WHEN insufficient_privilege OR read_only_sql_transaction THEN RAISE NOTICE 'PASS create blocked'; END;

  RESET ROLE;
END $$;