BACK-END
Tech Stack
Backend,Python,FastAPI,SQLAlchemy ORM,Database,SQL (PostgreSQL)
Other Tools Pydantic,Uvicorn


Design notes:

items.quantity represents inventory stock.  cart_items.quantity represents how many units a user wants to purchase.
if a user is not active th UI can call them with the get user with ID but not email.

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


services/ primarly helper functons and serves level code

services/item_s
primarly focas on items and the oreder preosses.
where cart_services focas is on identifying usersers and carts.



/(psycopg_models.py and psyc_order for order and orderitem)
psycopg models are in thes files.

sqlAmodels and (ordermodels for orders and orderItems)
this is where ORM.SQLAlchemy models are created.


