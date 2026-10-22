# Supabase setup (dev project, synthetic data only)
1. Create a NEW Supabase project (never reuse a personal/production one).
2. In the SQL Editor run, in order: migrations/001 -> 002 -> 003, then seed.sql, seed_glossary.sql.
3. Run tests/002_data_sanity.sql (all true) and tests/001_role_check.sql (all PASS).
4. Set the role password manually in the SQL Editor (never commit it):
   ALTER ROLE query_readonly LOGIN PASSWORD '<strong-password>';
5. Put the query_readonly connection string in backend/.env as DATABASE_URL.
   With the pooler, the username looks like query_readonly.<project-ref>.

Notes
- Business tables live in schema `northstar`, AI metadata in `querypilot`.
- Seed dates are relative to now(); golden expected results come from `reference_sql`.