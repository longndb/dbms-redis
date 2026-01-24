-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL
);

-- Seed sample data
INSERT INTO products (name, price, stock, category) VALUES
    ('Wireless Mouse', 29.99, 150, 'electronics'),
    ('USB-C Cable', 12.99, 500, 'accessories'),
    ('Mechanical Keyboard', 89.99, 75, 'electronics'),
    ('Monitor Stand', 45.00, 200, 'accessories'),
    ('Webcam HD', 59.99, 100, 'electronics');