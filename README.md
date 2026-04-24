this is a online store API its a backend service and nodes.js that manages store inventory and user shopping carts and orders.
curently it allows users to browse items, add them to a cart,
with swager you can order items while maintaining accurate stock levels and look at past orders.

The system validates available inventory before completing a order and automatically updates item stock when a transaction occurs.
This project was built to practice backend system design concepts such as:

REST API development, relational database modeling, SQL joins, transaction-style inventory updates, nodes.js/React JavaScript

Features
Inventory Management

Create and manage store inventory Track item stock levels
Prevent purchases when inventory is insufficient, 
created a documented record of past orders amd orderItems

Cart System

Create carts for users Add, remove and Update items quantities for carts 
a user can only curintly have one cart at a time that may change but for now it keeps it
more of a structered system and less of a overlaping feature.
Checkout Logic

Validates cart items against available inventory, then deducts purchased quantities from stock
Removes items from cart after Order. then it creates the order->orderItem record so past orders can be seen.

Error Handling

API returns structured error responses for cases such as:
cart not found, item not found
insufficient stock,invalid requests
and in some cases telling the the amoun of the items left or the item_id
db.rollbacks set up in the database and in trys where change can happen 

Tech Stack
forontend:
React (Vite), React Router, Fetch API (async/await)Javascript
Backend:
Python,FastAPI,SQLAlchemy ORM,
Database:
SQL (PostgreSQL),
Other Tools Pydantic,Uvicorn,nodes.js,

Project Structure
api/        #FAST API backend
api/routers/  FAST API routes 
api/models/   OMR models 
sql/        sql shemea
api/database.py   #db conecton folder
api/psycoq_models pydantic models

frontend/
src/
components/
api/
APP.jsx

BackEnd setup
cd api
python -m venv .venv
Activate virtual environment: 
PowerShell->.venv\Scripts\activate 
Bash->.venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Run server:
uvicorn main:app --reload

Backend runs on:
http://127.0.0.1:8000 
API docs should be available at http://127.0.0.1:8000/docs for testing 

Frontend (React + Vite):
open shell power termonal 
 cd frontend 
 npm install if needed 
 npm run dev
Frontend runs on:http://localhost:5173

How the System Works
React UI → FastAPI API → Database
React fetches data using async/await
FastAPI handles validation and business logic
Database stores users, items, carts, and orders

User Session (Important)
This project uses a simple session system:
User ID is stored in localStorage
Set via:
Manual input
Email login widget or user_id
so you must set a user ID 

SQL schema
Users table
id INT Primary Key
password_hash user pasword
created_at date of creation

Items table
id Primary Key
name item name
description DEFAULT no description item description is no description by defalt
quantity (inventory stock)
price NUMERIC(10,2) item price

Carts
id Primary Key
user_id FK to users(id)
purchase_date date this id now by defalt and

Cart_Items
cart_id FK to Carts
item_id FK to items
quantity (amount requested by user) NOT NULL CHECK (quantity > 0)
PRIMARY KEY (cart_id, item_id)/compound key(cart_id/item_id)

orders 
id PRIMARY KEY,
total_price NUMERIC(10,2) total price of all order_items in a order,
user_id FK to users(id),
order_date DEFAULT CURRENT_TIMESTAMP time stamp of order

order_items 
item_id FK to items(id) ON DELETE CASCADE, is deleted if item is deleated may change
quantity number of item_id that where ordered,
order_id FK to orders(id) ON DELETE CASCADE, 
price_at_order NUMERIC(10,2), price of item at the order 
PRIMARY KEY (order_id, item_id) 


Design notes:

items.quantity represents inventory stock.  cart_items.quantity represents how many units a user wants to purchase.

if items.quantity is ever >  cart_items.quantity there is a http to prevent over selling
/routers
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
Remove item from cart removes a CartItem from Cart
  DELETE /cart/{user_id}/removeItem,response_model=create_cartItem


Order
createOrder
  POST "/orders/{user_id}/createorder"
  creates a record of the item in a cart and puts them in a (order=> orderitems) format
  also removes the items from the cart.user_id and item-cartitem.quantity will be set to item.quantity
  will fail if CartItem.quantity > item.quantity

viewOrderDetails
  GET"/orders/{user_id}/vieworderdetails"
  shows all detals of past orders incluting item infermation and price at order time returns a list of OrderItems with item detalies

getAllOrders
  GET "/orders/getallorders"
  returns all orders in the database, for testing purposes only
  may use in admin

/(psycopg_models.py and psyc_order for order and orderitem)
psycopg models are in thes files.

sqlAmodels and (ordermodels for orders and orderItems)
this is where ORM.SQLAlchemy models are created.


frontend/
APP.jsx

frontend/api/ javascript fetching for difrent JONSON form the fatAPI
CartClient.js(addToCart(),viewCart(), addCart())
itemClient.js(getItem(),getAllItems())
orderClient.js(None)
userClient.js(Emaillogin())

frontend/componets/
(AdminPage.jxs,OrderPage.jsx,itemPage.jsx) are not done yet so nothing more than words
CartPage.jsx
  a basic set up for displaying all avalibal items and adding them to your cart with a nodes frame work
UserWidgit.jsx
 a basic log_in system to get the user_id.
you can do it with email, or ID !WARNING direct ID login will not block yo if ID dous not exist only email will


SET UP

Clone repository
git clone <https://github.com/Kye-Laliberte/store_api.git>
Install dependencies
pip install -r requirements.txt

Start server
run setup_db.py to seed the data and set up tabels
set up a .env or directly conect the database to the server

run setup.py
to seed and set up the tabels

uvicorn main:app --reload
API will run on
http://127.0.0.1:8000
docs available /docs

/docs
Future Improvements
Authentication
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
