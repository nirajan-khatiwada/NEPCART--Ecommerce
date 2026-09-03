# NepCart

NepCart is a full-featured, monolithic e-commerce web application built with Django and Bootstrap. It provides an end-to-end shopping workflow including user authentication with token verification, category and product browsing, variation selection, a session-persisted shopping cart, transactional order processing, customer account dashboards, and automated email status notifications.

---

## Architectural Overview

The application follows Django's model-view-template (MVT) architecture with decoupled functional apps:

- **account**: Custom user model (`Account`) replacing Django's default user, supporting email-based authentication, user profiles, account activation tokens, and secure password reset workflows.
- **category**: Hierarchical product taxonomy and slug generation.
- **product**: Inventory definitions, pricing (original price and sale price), stock tracking, popularity and featured flags, and media management.
- **store**: Public storefront catalog, category filtering, product variation management (colors, sizes), and detail page rendering.
- **cart**: Session-based and authenticated cart item persistence, quantity increments, subtotal calculations, and taxes.
- **order**: Checkout workflows, order generation, address capture, payment recording, automated invoice generation, and post-save order status notification signals.
- **dashbord**: Customer account management, order history inspection, address books, and password updates.
- **search**: Multi-field catalog querying across product titles and descriptions.

---

## Technical Specifications

- **Language**: Python 3.10+ (configured for Python 3.12)
- **Framework**: Django 4.2 (LTS)
- **Database**: SQLite (default development) / PostgreSQL (production-ready via `psycopg2-binary`)
- **Frontend**: Django Templates, Bootstrap 4, jQuery, Font Awesome
- **Admin Interface**: Django Admin customized with `django-jazzmin`
- **Image Processing**: Pillow
- **WSGI Server**: Gunicorn

---

## System Requirements

- Python 3.10 or higher
- pip (Python package installer)
- virtualenv or venv
- Git

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nirajan-khatiwada/NEPCART--Ecommerce.git
cd NEPCART--Ecommerce
```

### 2. Create and Activate a Virtual Environment

On Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate
```

On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables Configuration

Copy the example environment template to create a local `.env` file:

```bash
cp .env.example .env
```

Configure the following variables in `.env`:

```ini
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database Configuration (leave empty or unset for SQLite)
DATABASE_URL=

# Email Settings (for user activation and order notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin Access)

```bash
python manage.py createsuperuser
```

### 7. Seed Initial Catalog Data (Optional)

The repository includes a seeding script that populates realistic categories, products, stock levels, and demo images:

```bash
python seed_database.py
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

The application will be accessible at: `http://127.0.0.1:8000/`  
The admin dashboard is accessible at: `http://127.0.0.1:8000/admin/`

---

## Key Functional Modules

### Authentication and Account Security
- Custom user model with email as the unique login identifier.
- Email verification required on registration via base64 encoded UID and cryptographically signed token.
- Secure password reset flow utilizing Django's `default_token_generator`.

### Product Catalog and Variations
- Structured categories with automatic slug generation for search engine friendly URLs.
- Product inventory tracking with automatic out-of-stock indicators.
- Multi-dimensional product variations supporting color and size selections per item.

### Shopping Cart
- Unauthenticated guest carts tracked via browser session cookies (`session_key`).
- Automatic cart migration from guest session to authenticated user account upon login.
- Dynamic subtotal, tax, and grand total calculations via context processors.

### Orders and Checkout
- Structured multi-step checkout capturing shipping address, contact details, and payment options.
- Unique order number generation with timestamp encoding.
- Django post-save signals dispatching automated order confirmation and status update emails.

---

## Project Structure

```text
NEPCART--Ecommerce/
|-- account/             # User authentication, profiles, registration tokens
|-- asset/               # Brand assets and design resources
|-- cart/                # Cart model, session handling, quantity updates
|-- category/            # Product category definitions and slugs
|-- dashbord/            # User profile dashboard and order views
|-- ecommerce/           # Project configuration, settings, routing, WSGI
|-- media/               # User-uploaded content (products, categories)
|-- order/               # Order pipeline, payments, invoices, signals
|-- product/             # Product models, pricing, inventory
|-- search/              # Search views and keyword query logic
|-- static/              # CSS, JavaScript, and vendor assets
|-- store/               # Store catalog views, variations, reviews
|-- templates/           # Global templates, email templates, includes
|-- .env.example         # Environment template
|-- manage.py            # Django CLI management entrypoint
|-- requirements.txt     # Python dependency lockfile
|-- runtime.txt          # Python runtime specification
`-- seed_database.py     # Database population utility
```

---

## Testing and Quality Verification

Verify Django system configuration and model consistency:

```bash
python manage.py check
```

Execute automated test suite:

```bash
python manage.py test
```

---

## Author

**Nirajan Khatiwada**  
Email: nirajankhatiwada29@gmail.com  
GitHub: [nirajan-khatiwada](https://github.com/nirajan-khatiwada)
