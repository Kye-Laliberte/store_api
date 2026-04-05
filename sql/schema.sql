
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);


CREATE TABLE IF NOT EXISTS items(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT "no description",
    quantity INTEGER NOT NULL CHECK(quantity>=0) DEFAULT 0,
    price NUMERIC(10,2) NOT NULL CHECK(price >= 0)
    
);

CREATE TABLE IF NOT EXISTS carts(
    id SERIAL PRIMARY KEY,
     user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purchase_date TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cart_items (
    cart_id INTEGER NOT NULL REFERENCES  carts(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES  items(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (cart_id, item_id)
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    total_price NUMERIC(10,2) NOT NULL CHECK(total_price >= 0),
    user_id INT NOT NULL REFERENCES users(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id INTEGER NOT NULL REFERENCES  items(id) ON DELETE CASCADE,
    quantity int NOT NULL CHECK (quantity > 0),
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    price_at_order NUMERIC(10,2) NOT NULL CHECK(price_at_order >= 0),
    PRIMARY KEY (order_id, item_id)
);