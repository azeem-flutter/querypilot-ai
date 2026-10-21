-- Synthetic data. Dates now() ke hisaab se hain, isliye "last month" mein hamesha data hoga.
-- Dobara chal sakta hai (TRUNCATE karta hai). SIRF dev project par chalao.
TRUNCATE northstar.order_items, northstar.orders, northstar.products,
         northstar.categories, northstar.customers RESTART IDENTITY CASCADE;
SELECT setseed(0.42);

INSERT INTO northstar.categories (category_name) VALUES
 ('Electronics'),('Clothing'),('Home & Kitchen'),('Books'),('Sports'),('Beauty');

INSERT INTO northstar.products (product_name, category_id, unit_price, is_active) VALUES
 ('Wireless Earbuds',1,59.99,true),('Smart Watch',1,149.00,true),('Bluetooth Speaker',1,39.50,true),('Phone Charger',1,12.99,true),
 ('Cotton T-Shirt',2,15.00,true),('Denim Jacket',2,69.00,true),('Running Shoes',2,89.90,true),('Winter Scarf',2,18.50,true),
 ('Air Fryer',3,95.00,true),('Blender',3,45.00,true),('Cookware Set',3,120.00,true),('Table Lamp',3,28.00,true),
 ('Data Science Handbook',4,35.00,true),('Urdu Poetry Collection',4,14.00,true),('Kids Story Book',4,9.50,true),('Cooking Basics',4,22.00,true),
 ('Yoga Mat',5,24.00,true),('Football',5,19.99,true),('Dumbbell Set',5,55.00,true),('Cricket Bat',5,75.00,true),
 ('Face Cream',6,21.00,true),('Perfume',6,48.00,true),
 ('Retro Camera',1,210.00,false),      -- inactive aur kabhi nahi bika (edge case)
 ('Limited Edition Mug',3,11.00,false);

INSERT INTO northstar.customers (customer_name, email, city, created_at)
SELECT (ARRAY['Ali','Sara','Ahmed','Fatima','Hassan','Ayesha','Usman','Zainab','Bilal','Hira'])[1 + i % 10] || ' ' ||
       (ARRAY['Khan','Malik','Sheikh','Butt','Raza','Chaudhry','Iqbal','Ansari','Qureshi','Siddiqui'])[1 + (i*7) % 10],
       'customer' || i || '@example.com',
       CASE WHEN i = 60 THEN NULL       -- NULL city (edge case)
            ELSE (ARRAY['Faisalabad','Lahore','Karachi','Islamabad','Multan','Peshawar'])[1 + i % 6] END,
       now() - random() * interval '700 days'
FROM generate_series(1, 60) AS i;
-- Customers 55-60 kabhi order nahi dete (edge case: "customers with no orders").

INSERT INTO northstar.orders (customer_id, order_date, status, shipping_city)
SELECT 1 + floor(random() * 54)::int,
       now() - random() * interval '180 days',
       CASE WHEN r < 0.70 THEN 'completed' WHEN r < 0.85 THEN 'pending' ELSE 'cancelled' END,
       (ARRAY['Faisalabad','Lahore','Karachi','Islamabad','Multan','Peshawar'])[1 + floor(random()*6)::int]
FROM (SELECT random() AS r FROM generate_series(1, 400)) t;

-- Har order mein 1-4 items (count order id se), product random (22 active mein se).
INSERT INTO northstar.order_items (order_id, product_id, quantity, unit_price, discount_amount)
SELECT l.order_id, l.product_id, l.qty, p.unit_price,
       CASE WHEN l.r < 0.2 THEN round((l.qty * p.unit_price * 0.10)::numeric, 2) ELSE 0 END
FROM (
  SELECT o.id AS order_id,
         1 + floor(random() * 22)::int AS product_id,
         1 + floor(random() * 5)::int  AS qty,
         random() AS r
  FROM northstar.orders o
  CROSS JOIN LATERAL generate_series(1, 1 + (o.id % 4)) AS g(n)
) l
JOIN northstar.products p ON p.id = l.product_id;

ANALYZE;