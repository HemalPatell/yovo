# 🌿 YOVO — Your Old, Valued Once More

> A modern, startup-grade marketplace for buying and selling second-hand clothes and books.

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.x-green)](https://djangoproject.com)
[![Channels](https://img.shields.io/badge/Channels-4.x-orange)](https://channels.readthedocs.io)

---

## 📂 Project Structure

```
yovo/
├── manage.py
├── requirements.txt
├── Procfile                    # Render/Railway deployment
├── runtime.txt                 # Python version for Render
├── .env.example                # Environment variable template
│
├── yovo_project/               # Django project core
│   ├── __init__.py
│   ├── settings.py             # Main settings (dev + prod)
│   ├── urls.py                 # Root URL config
│   ├── asgi.py                 # ASGI + Channels config
│   └── wsgi.py                 # WSGI fallback
│
├── marketplace/                # Main app
│   ├── models.py               # Item, Cart, CartItem, Message, Profile
│   ├── views.py                # All views
│   ├── forms.py                # All forms
│   ├── urls.py                 # App URL patterns
│   ├── admin.py                # Admin configuration
│   ├── consumers.py            # WebSocket consumer (chat)
│   ├── routing.py              # WebSocket URL routing
│   ├── context_processors.py   # Cart count injector
│   ├── signals.py              # Auto-create Profile on User creation
│   ├── apps.py
│   └── templates/
│       └── marketplace/
│           ├── home.html       # Landing + Browse page
│           ├── login.html
│           ├── register.html
│           ├── dashboard.html
│           ├── item_detail.html
│           ├── post_item.html
│           ├── cart.html
│           ├── checkout.html
│           ├── chat.html       # Real-time chat UI
│           └── user_profile.html
│
├── templates/
│   └── base.html               # Base template (navbar, footer, toasts)
│
├── static/
│   ├── css/
│   │   └── main.css            # Full design system (~1100 lines)
│   └── js/
│       ├── main.js             # Theme, scroll reveal, navbar, UX
│       └── chat.js             # WebSocket chat client
│
├── staticfiles/                # Created by collectstatic
└── media/                      # User uploads (items, avatars)
```

---

## ⚡ Quick Start (Local Development)

### 1. Clone & setup environment

```bash
git clone <your-repo>
cd yovo

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY at minimum
```

### 3. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create superuser

```bash
python manage.py createsuperuser
```

### 5. Collect static files

```bash
python manage.py collectstatic --noinput
```

### 6. Run the development server

```bash
# Uses Daphne (ASGI) — supports WebSocket chat
python manage.py runserver

# OR with Daphne explicitly:
daphne -p 8000 yovo_project.asgi:application
```

Visit: **http://localhost:8000**  
Admin: **http://localhost:8000/admin**

---

## 🗄️ Database

### Development (SQLite — default)
No setup needed. Just run migrations.

### Production (PostgreSQL)

```bash
# Install locally
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql

postgres=# CREATE DATABASE yovo_db;
postgres=# CREATE USER yovo_user WITH PASSWORD 'strongpassword';
postgres=# GRANT ALL PRIVILEGES ON DATABASE yovo_db TO yovo_user;
postgres=# \q
```

Set in `.env`:
```
DATABASE_URL=postgres://yovo_user:strongpassword@localhost:5432/yovo_db
```

---

## 🔌 Django Channels (Real-Time Chat)

### Development
Uses `InMemoryChannelLayer` — no extra setup.

### Production (Redis required)

```bash
pip install channels-redis
```

Set `REDIS_URL` in `.env` and update `CHANNEL_LAYERS` in `settings.py`:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [config('REDIS_URL')]},
    }
}
```

---

## ☁️ Deployment Guide

---

### 🚂 Railway (Recommended — easiest)

**Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
railway login
```

**Step 2: Create project**
```bash
railway init
```

**Step 3: Add PostgreSQL**
```
Railway Dashboard → + New → Database → PostgreSQL
```
Railway auto-injects `DATABASE_URL`.

**Step 4: Add Redis** (for WebSocket in production)
```
Railway Dashboard → + New → Database → Redis
```

**Step 5: Set environment variables**

In Railway Dashboard → Variables:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.railway.app
DATABASE_URL=<auto-injected>
REDIS_URL=<auto-injected>
```

**Step 6: Deploy**
```bash
railway up
```

**Step 7: Run migrations on Railway**
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py collectstatic --noinput
```

---

### 🎨 Render Deployment

**Step 1: Push to GitHub**
```bash
git init && git add . && git commit -m "Initial commit"
git remote add origin https://github.com/yourname/yovo.git
git push -u origin main
```

**Step 2: Create Web Service on Render**
- Go to https://render.com → New → Web Service
- Connect your GitHub repo
- Set:
  - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
  - Start Command: `daphne -b 0.0.0.0 -p $PORT yovo_project.asgi:application`

**Step 3: Add PostgreSQL**
- Render Dashboard → New → PostgreSQL
- Copy `Internal Database URL` into env vars as `DATABASE_URL`

**Step 4: Environment Variables on Render**
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.onrender.com
DATABASE_URL=<from PostgreSQL service>
```

**Step 5: Redis** (optional, for production chat)
- Render → New → Redis
- Set `REDIS_URL` env var

---

## 🔑 Key Environment Variables

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `yovo.com,www.yovo.com` |
| `DATABASE_URL` | PostgreSQL URL | `postgres://user:pass@host/db` |
| `REDIS_URL` | Redis URL (for prod chat) | `redis://localhost:6379` |

---

## ✨ Features Overview

| Feature | Status |
|---|---|
| User Registration & Login | ✅ |
| User Dashboard | ✅ |
| Post Items (Clothes/Books) | ✅ |
| Browse & Filter Items | ✅ |
| Location-based filtering | ✅ |
| Shopping Cart | ✅ |
| Checkout (simulation) | ✅ |
| Real-time WebSocket Chat | ✅ |
| Dark / Light Mode | ✅ |
| Scroll reveal animations | ✅ |
| Responsive design | ✅ |
| Admin panel | ✅ |
| Whitenoise static serving | ✅ |
| Production-ready settings | ✅ |

---

## 🛡️ Admin Panel

Visit `/admin/` and log in with your superuser credentials.

Features:
- Manage all Items (search by title, seller, location)
- Filter by category and sold status
- Manage Carts, Messages, User Profiles
- Mark items as sold from list view

---

## 🧪 Generate Sample Data

```python
# Run in Django shell: python manage.py shell
from django.contrib.auth.models import User
from marketplace.models import Item

# Create test user
u = User.objects.create_user('testuser', 'test@test.com', 'password123')

# Create items
Item.objects.create(title='Vintage Jacket', price=799, category='clothes', location='mumbai', seller=u, description='Great condition Levi\'s jacket from the 90s.')
Item.objects.create(title='The Alchemist', price=120, category='books', location='bangalore', seller=u, description='Paulo Coelho classic. Read once.')
```

---

## 📱 Pages

| URL | Page |
|---|---|
| `/` | Home — Hero + Browse |
| `/item/<id>/` | Item Detail |
| `/item/post/` | Post New Item |
| `/auth/login/` | Login |
| `/auth/register/` | Register |
| `/auth/logout/` | Logout |
| `/dashboard/` | User Dashboard |
| `/cart/` | Shopping Cart |
| `/cart/checkout/` | Checkout |
| `/chat/<item_id>/<user_id>/` | Real-time Chat |
| `/user/<username>/` | Public Profile |
| `/admin/` | Admin Panel |
