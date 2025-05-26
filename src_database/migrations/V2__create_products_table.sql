CREATE TABLE IF NOT EXISTS Product (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    product_information TEXT,
    barcode VARCHAR(50) UNIQUE,
)