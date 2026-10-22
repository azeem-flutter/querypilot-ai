# ADR-001: Business tables live in schema `northstar`, not `public`

Supabase exposes `public` tables through its auto-generated REST API. A separate schema keeps the
data off that surface and lets the SQL policy allowlist a single schema. The restricted role
(`query_readonly`) gets USAGE on `northstar` only, and `customers.email` is deliberately not granted.