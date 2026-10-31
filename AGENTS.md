# AGENTS & CODING CONTEXT: ECO-LOOP PLATFORM

## 1. PROJECT OVERVIEW
ECO-LOOP is an e-commerce platform dedicated to sustainable fashion, recycled outdoor gear, and circular re-commerce (trade-in/re-wear program).
- Domain: Green E-Commerce, ESG Lifestyle, Circular Economy.
- Core Persona: Environmentally conscious shoppers, outdoor lovers, Gen Z & Millennials.

## 2. TECH STACK SPECIFICATION
- Backend: Python (FastAPI) or Node.js (Express / NestJS)
- Database: MySQL 8.0+ or PostgreSQL
- ORM / Migration: SQLAlchemy + Alembic (Python) OR Prisma (Node.js)
- Frontend: HTML5/CSS3/Vanilla JS (Bootstrap 5 / TailwindCSS) OR React / Next.js
- Authentication: JWT (JSON Web Tokens), bcrypt for password hashing
- Validation: Pydantic v2 (Python) or Zod (TypeScript)

## 3. CORE ARCHITECTURAL PRINCIPLES
- Layered Architecture: Controller/Router -> Service -> Repository/Model.
- Restful API Conventions: Standard HTTP methods (GET, POST, PUT, DELETE), JSON responses with consistent wrappers:
  `{ "success": true, "data": ..., "message": "..." }`
- Responsive UI: Mobile-first approach, fully responsive on Chrome, Firefox, Safari, Edge.
- Clean Code: Use descriptive variable names in English, add concise docstrings, keep functions under 40 lines where feasible.

## 4. DATABASE ENTITIES & RELATIONSHIPS
1. Users (id, full_name, email, password_hash, role [customer, admin], phone, address, created_at)
2. Categories (id, name, slug, parent_id [nullable, max 2 levels], description, status)
3. Products (id, category_id, name, code, slug, price, discount_price, material_eco_type, stock_quantity, description, content_detail, is_active, created_at)
4. ProductImages (id, product_id, image_url, is_thumbnail)
5. Orders (id, user_id, order_code, total_amount, discount_amount, final_amount, status [pending, confirmed, shipping, completed, cancelled], payment_method, shipping_address, created_at)
6. OrderItems (id, order_id, product_id, quantity, unit_price, subtotal)
7. TradeIns (id, user_id, item_description, condition_grade, contact_phone, pickup_address, status [pending, approved, collected, rejected], voucher_issued)
8. Articles (id, category_type [news, event, eco_guide], title, slug, short_summary, content, image_url, views, is_published, created_at)
9. Contacts (id, full_name, email, phone, subject, message, status [new, resolved], created_at)

## 5. BUSINESS RULES & CONSTRAINTS
- Product hierarchy must NOT exceed 2 levels (Category -> Subcategory).
- Soft deletion / Hidden status is required for Products, Categories, and Articles (`is_active` or `is_published` flags).
- Form inputs must be validated strictly on both client-side and server-side.
- The system must support guest cart sessions and authenticated user checkouts.
- Any calculation regarding discount vouchers must ensure the final amount never falls below 0.