# 🛒 GreatKart - Professional Django E-Commerce Platform

GreatKart is a high-performance, full-featured E-commerce solution built using the **Django Web Framework**. This project demonstrates an end-to-end implementation of a modern online store, focusing on scalability, security, and user experience.

## 🚀 Key Features Implemented

### 👤 User Authentication & Security
* **Custom User Model**: Extended Django's default User model for flexible authentication (using Email instead of Username).
* **Account Activation**: Secure registration flow with email verification links.
* **Security**: Robust "Forgot Password" and password reset functionality using secure tokens.

### 📦 Product & Category Management
* **Dynamic Catalog**: Organized products by categories with SEO-friendly slugs.
* **Product Variations**: Advanced logic to handle multiple variations (e.g., Color and Size) for a single product.
* **Inventory Tracking**: Real-time "Out of Stock" labels based on database stock levels.

### 🛒 Shopping Cart System
* **Sophisticated Logic**: Supports guest carts (session-based) and persistent carts for logged-in users.
* **Variation Grouping**: Smartly groups identical items with the same variations in the cart.
* **Calculations**: Automated Tax and Total Price calculations.

### 🔍 User Experience (UX)
* **Search Functionality**: Efficient keyword-based product search.
* **Pagination**: Optimized loading of product lists using Django Paginator.
* **Responsive Design**: Fully mobile-responsive UI built with Bootstrap.

## 🛠️ Technology Stack
* **Backend**: Python 3.x, Django 5.x 🐍
* **Frontend**: HTML5, CSS3, Bootstrap 4/5 🎨
* **Database**: SQLite3 (Development) 🗄️
* **Version Control**: Git & GitHub 🐙

## 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/mdpatel007/greatkart-django.git](https://github.com/mdpatel007/greatkart-django.git)
   cd greatkart-django

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies:**
    ```bash
   pip install -r requirement.txt
   
4. **Run Migrations:**
   ```bash
   python manage.py migrate
   
5. **Start the Server:**
   ```bash
   python manage.py runserver

Developed with ❤️ by mdpatel007
