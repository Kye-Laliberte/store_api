this is a online store API its a backend service that manages store inventory and user shopping carts.
It allows users to browse items, add them to a cart, and purchase items while maintaining accurate stock levels.

The system validates available inventory before completing purchases and automatically updates item stock when a transaction occurs.
This project was built to practice backend system design concepts such as:

REST API development, relational database modeling, SQL joins, transaction-style inventory updates

Features
Inventory Management

Create and manage store inventory Track item stock levels
Prevent purchases when inventory is insufficient

Cart System

Create carts for users Add, remove and Update items quantities for carts 
a user can only curintly have one cart at a time that may change but for now it keeps it
more of a structered system and less of a overlaping feature.
Checkout Logic

Validates cart items against available inventory, then deducts purchased quantities from stock
Removes items from cart after purchase.

Error Handling

API returns structured error responses for cases such as:
cart not found, item not found
insufficient stock,invalid requests
and in some cases telling the the amoun of the items left or the item_id

Tech Stack

Backend,Python,FastAPI,SQLAlchemy ORM,Database,SQL (PostgreSQL)
Other Tools Pydantic,Uvicorn

SQL schema
Users table
id Primary Key
password_hash user pasword
created_at date of creation

Items table
id Primary Key
name item name
description TEXT DEFAULT no description item description is no description by defalt
quantity (inventory stock)
price item price

Carts
id Primary Key
user_id FK to carts
purchase_date date of cart creation

Cart_Items
cart_id FK to Carts
item_id FK to items
quantity (amount requested by user) NOT NULL CHECK (quantity > 0)
PRIMARY KEY (cart_id, item_id)/compound key(cart_id/item_id)

Design notes:

items.quantity represents inventory stock.  cart_items.quantity represents how many units a user wants to purchase.

if items.quantity is ever >  cart_items.quantity there is a http to prevent over selling

API Endpoints
Items
get all items in ther sql omr models
GET (/items/get_all)
Create item
POST (/items/add_item) defcreate_item,response_model=item
Get items
GET /items/{item_id}/detals,response_model=item)
Update item
PUT /items/{item_id}/update",response_model=item
Delete item
DELETE /items/{item_id}
Cart

Create cart
POST /cart/{user_id}/newcart", response_model=carts
View cart
GET /cart/{user_id}/viewcart",response_model=List[CartItemsOut])
Add item to cart
POST /cart/{user_id}/addItem,response_model=CartItemsOut
Remove item from cart
DELETE /cart/{user_id}/removeItem,response_model=create_cartItem
Checkout
POST/cart/{user_id}/PurchaseItems",response_model=purchaseout
POST/{user_id}/PurchaseCart",response_model=List[purchaseout]
This ensures that inventory cannot go negative.

Running the Project

Clone repository
git clone <repo-url>
Install dependencies
pip install -r requirements.txt
Start server
uvicorn main:app --reload

API will run on
http://127.0.0.1:8000
Interactive docs available at

/docs
Future Improvements
Authentication
password hashing
login system
JWT authentication

Security
rate limiting
request validation improvements
Database
order history table
transaction logging
Cart Enhancements
persistent carts
cart expiration
multiple carts per user
Performance, indexing query optimization
