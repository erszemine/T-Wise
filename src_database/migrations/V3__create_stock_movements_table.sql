CREATE TABLE IF NOT EXISTS StockMovement (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    movement_type VARCHAR(20) NOT NULL, -- 'GIRIS', 'CIKIS', 'TRANSFER'
    amount INTEGER NOT NULL CHECK (amount > 0),
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    explanation TEXT,
    FOREIGN KEY (product_id) REFERENCES Products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE SET NULL,
);

