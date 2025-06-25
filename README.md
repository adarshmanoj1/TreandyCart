# 🛒 TrendyCart

TrendyCart is a feature-rich, full-stack e-commerce platform built using Django. It offers users a seamless shopping experience with features like product browsing, wishlist and cart management, order tracking, and admin/delivery partner dashboards. The frontend is styled to resemble leading platforms like Flipkart, Amazon, and Meesho.


## ✨ Features

- ✅ User authentication with OTP login simulation
- 🛍️ Product listings with filters (Category, Price, Brand, Rating)
- ❤️ Wishlist with toggle functionality
- 🛒 Cart management with add/remove support
- 🔄 Order placement and tracking
- 📦 Custom admin dashboard
- 🚚 Delivery partner system with custom login and order status updates
- 🌙 Dark-themed, responsive UI with animations

## 🛠️ Tech Stack

- **Backend:** Django, SQLite
- **Frontend:** HTML5, CSS3, Bootstrap, JavaScript
- **Auth:** Simulated OTP Login
- **Database:** SQLite (can be upgraded)

---
## ⚙️ Setup Instructions(bash)

### 1. Clone the repository 
git clone https://github.com/your-username/TrendyCart.git
cd TrendyCart

2. Create and activate virtual environment

python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Run migrations

python manage.py makemigrations
python manage.py migrate

5. Create superuser

python manage.py createsuperuser

6. Run development server

python manage.py runserver

🔐 Login Credentials
Admin Dashboard:
Visit /admin or custom admin route
Delivery Partner:
Login at /staff-login/ after registering through /staff-register/

📝 Notes
This project uses simulated OTPs for development.
Admin can assign delivery partners to orders.
Order status updates reflect in the user tracking page.
