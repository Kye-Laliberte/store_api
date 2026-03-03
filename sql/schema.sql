
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS items(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL CHECK(price >= 0)
);


CREATE TABLE IF NOT EXISTS inventory(

    item_id INTEGER REFERENCES items(id) NO CASCADE,
    quantity INTEGER NOT NULL CHECK(quantity>=0) DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
); 

CREATE TABLE IF NOT EXISTS carts(
    id SERIAL PRIMARY KEY,
     user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE
    purchase_date TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE cart_items (
    cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (cart_id, item_id)
);

CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_amount NUMERIC(10,2) NOT NULL CHECK (total_amount >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE purchase_items (
    purchase_id INTEGER REFERENCES purchases(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    purchase_price NUMERIC(10,2) NOT NULL CHECK (purchase_price >= 0),
    PRIMARY KEY (purchase_id, item_id)
);