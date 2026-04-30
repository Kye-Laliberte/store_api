BACK-END
Tech Stack
Backend,Python,FastAPI,SQLAlchemy ORM,Database,SQL (PostgreSQL)
Other Tools Pydantic,Uvicorn

SQL schema
users table
id INT Primary Key
password_hash user pasword
created_at date of creation

items table
id Primary Key
name item name
description TEXT DEFAULT no description item description is no description by defalt
quantity (inventory stock)
price NUMERIC(10,2) item price

carts
id Primary Key
user_id FK to carts(user_id)
purchase_date date of cart creation

cart_Items
cart_id FK to Carts(id)
item_id FK to items(id)
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

Users
