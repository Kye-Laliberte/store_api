# Store Interface Frontend

React + Vite frontend application for the Store Interface project.

The frontend provides the user interface for browsing products, managing shopping carts, and interacting with the backend API. It communicates with the FastAPI backend through REST API requests.
---
# Tech Stack

* React (Vite)
* React Router
* JavaScript
* Fetch API (async/await)

---
# Setup

Install dependencies:

```bash
cd frontend
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

# Application Structure

```
frontend/
│
├── src/
│   ├── api/
│   │   ├── cartClient.js
│   │   ├── itemClient.js
│   │   ├── orderClient.js
│   │   └── userClient.js
│   │
│   ├── components/
│   │   ├── cart_components.jsx
│   │   └── UserWidget.jsx
│   │
│   ├── pages/
│   │   └── CartPage.jsx
│   │
│   ├── App.jsx
│   └── app.css
```

---

# API Communication

The frontend uses API client files to organize requests to the FastAPI backend.

## API Clients

### cartClient.js

Handles cart-related requests:

* `addToCart()`
* `viewCart()`
* `addCart()`

### itemClient.js

Handles inventory requests:

* `getItem()`
* `getAllItems()`

### orderClient.js

Reserved for order-related API requests.

### userClient.js

Handles user requests:

* Email login
* User lookup

---

# Components

## Cart Components

### cart_components.jsx

Handles cart display and user interaction.

Responsibilities:

* Display cart items
* Add items to cart
* Update cart interface

### UserWidget.jsx

Handles user identification.

Current functionality:

* User login through email or ID
* Maintains user state after refresh
* Connects users to their cart

---

# Pages

## CartPage.jsx

Main store page.

Features:

* Displays available inventory
* Displays the user's current cart
* Allows users to add items
* Refreshes data to keep inventory and cart information current
--
# Application Flow

```
React UI
    |
    v
API Client Functions
    |
    v
FastAPI Backend
```
The frontend is responsible for:

* User interaction
* Displaying data
* Sending requests

The backend is responsible for:

* Validation
* Business logic
* Inventory updates
* Database operations
---
# Future Improvements

* Complete order interface
* Improved authentication UI
* Product search/filtering
* Better loading and error states
* More reusable UI components

```
```
