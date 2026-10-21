SELECT 'orders >= 300' AS check_name, (SELECT count(*) FROM northstar.orders) >= 300 AS ok
UNION ALL SELECT 'has cancelled orders',  EXISTS (SELECT 1 FROM northstar.orders WHERE status='cancelled')
UNION ALL SELECT 'has pending orders',    EXISTS (SELECT 1 FROM northstar.orders WHERE status='pending')
UNION ALL SELECT 'last calendar month has completed orders',
  EXISTS (SELECT 1 FROM northstar.orders WHERE status='completed'
          AND order_date >= date_trunc('month', now()) - interval '1 month'
          AND order_date <  date_trunc('month', now()))
UNION ALL SELECT 'customer with no orders exists',
  EXISTS (SELECT 1 FROM northstar.customers c WHERE NOT EXISTS (SELECT 1 FROM northstar.orders o WHERE o.customer_id=c.id))
UNION ALL SELECT 'product never sold exists',
  EXISTS (SELECT 1 FROM northstar.products p WHERE NOT EXISTS (SELECT 1 FROM northstar.order_items i WHERE i.product_id=p.id))
UNION ALL SELECT 'customer with NULL city exists', EXISTS (SELECT 1 FROM northstar.customers WHERE city IS NULL)
UNION ALL SELECT 'orders with more than one item exist',
  EXISTS (SELECT 1 FROM northstar.order_items GROUP BY order_id HAVING count(*) > 1);