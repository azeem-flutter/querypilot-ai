-- Northstar Retail: synthetic business data.
-- Alag schema (public nahi) taake Supabase ki REST API in tables ko expose na kare.
CREATE SCHEMA IF NOT EXISTS northstar;

CREATE TABLE northstar.customers (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_name text        NOT NULL,
    email         text        NOT NULL UNIQUE,
    city          text,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE northstar.categories (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name text NOT NULL UNIQUE
);

CREATE TABLE northstar.products (
    id           integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name text          NOT NULL,
    category_id  integer       NOT NULL REFERENCES northstar.categories(id),
    unit_price   numeric(12,2) NOT NULL CHECK (unit_price >= 0),
    is_active    boolean       NOT NULL DEFAULT true
);

CREATE TABLE northstar.orders (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id   integer     NOT NULL REFERENCES northstar.customers(id),
    order_date    timestamptz NOT NULL,
    status        text        NOT NULL CHECK (status IN ('pending','completed','cancelled')),
    shipping_city text
);

CREATE TABLE northstar.order_items (
    id              integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id        integer       NOT NULL REFERENCES northstar.orders(id),
    product_id      integer       NOT NULL REFERENCES northstar.products(id),
    quantity        integer       NOT NULL CHECK (quantity > 0),
    unit_price      numeric(12,2) NOT NULL CHECK (unit_price >= 0),
    discount_amount numeric(12,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0)
);

CREATE INDEX idx_products_category ON northstar.products(category_id);
CREATE INDEX idx_orders_customer   ON northstar.orders(customer_id);
CREATE INDEX idx_orders_date       ON northstar.orders(order_date);
CREATE INDEX idx_orders_status     ON northstar.orders(status);
CREATE INDEX idx_items_order       ON northstar.order_items(order_id);
CREATE INDEX idx_items_product     ON northstar.order_items(product_id);