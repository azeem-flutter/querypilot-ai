"""TEMPORARY (Day 2): chhota fixed schema context. Day 3 mein RAG isay replace karega."""

STATIC_SCHEMA_CONTEXT = """Tables (schema northstar, PostgreSQL):
- customers(id, customer_name, city, created_at)   -- email is NOT available
- categories(id, category_name)
- products(id, product_name, category_id -> categories.id, unit_price, is_active)
- orders(id, customer_id -> customers.id, order_date timestamptz UTC, status in ('pending','completed','cancelled'), shipping_city)
- order_items(id, order_id -> orders.id, product_id -> products.id, quantity, unit_price (price at sale), discount_amount (whole line))

Business definitions:
- Net item revenue = quantity * unit_price - discount_amount.
- Revenue = SUM(net item revenue) for orders with status = 'completed' unless the user asks otherwise. Roman Urdu: sale, bikri.
- Order count = COUNT(DISTINCT orders.id), never count order_items rows.
- Last month = previous calendar month: order_date >= date_trunc('month', now()) - interval '1 month' AND order_date < date_trunc('month', now()). Roman Urdu: pichlay mahine.
- Last 30 days = rolling: order_date >= now() - interval '30 days'. Roman Urdu: pichlay 30 din.
- Cancelled orders are excluded from completed-sales revenue.
- "Top"/"best" needs a metric (revenue or units sold); otherwise ask for clarification.
- No profit, cost, inventory, employee or supplier data exists."""