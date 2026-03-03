
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);


CREATE TABLE IF NOT EXISTS items(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    quantity INTEGER NOT NULL CHECK(quantity>=0) DEFAULT 0,
    price NUMERIC(10,2) NOT NULL CHECK(price >= 0)
    
);

CREATE TABLE IF NOT EXISTS carts(
    id SERIAL PRIMARY KEY,
     user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purchase_date TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cart_items (
    cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (cart_id, item_id)
);
