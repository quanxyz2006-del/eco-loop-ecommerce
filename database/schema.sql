-- ECO-LOOP initial schema for MySQL 8.0+
CREATE DATABASE IF NOT EXISTS eco_loop
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE eco_loop;

CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(150) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin', 'customer') NOT NULL DEFAULT 'customer',
  phone VARCHAR(20) NULL,
  address TEXT NULL,
  green_points INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE categories (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  slug VARCHAR(150) NOT NULL UNIQUE,
  parent_id INT NULL,
  description TEXT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id)
) ENGINE=InnoDB;

CREATE TABLE products (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  category_id INT NOT NULL,
  name VARCHAR(255) NOT NULL,
  code VARCHAR(50) NOT NULL UNIQUE,
  slug VARCHAR(255) NOT NULL UNIQUE,
  price DECIMAL(12,2) NOT NULL,
  discount_price DECIMAL(12,2) NULL,
  material_eco_type VARCHAR(100) NULL,
  co2_saved_kg FLOAT NOT NULL DEFAULT 0,
  stock_quantity INT NOT NULL DEFAULT 0,
  description TEXT NULL,
  content_detail LONGTEXT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id),
  CONSTRAINT chk_products_price CHECK (price >= 0),
  CONSTRAINT chk_products_discount CHECK (discount_price IS NULL OR (discount_price >= 0 AND discount_price <= price)),
  CONSTRAINT chk_products_stock CHECK (stock_quantity >= 0)
) ENGINE=InnoDB;

CREATE TABLE product_images (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  image_url VARCHAR(500) NOT NULL,
  is_thumbnail BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT fk_product_images_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE orders (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  full_name VARCHAR(150) NOT NULL,
  order_code VARCHAR(50) NOT NULL UNIQUE,
  total_amount DECIMAL(12,2) NOT NULL,
  discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
  final_amount DECIMAL(12,2) NOT NULL,
  payment_method ENUM('cod', 'bank_transfer') NOT NULL DEFAULT 'cod',
  status ENUM('pending', 'confirmed', 'shipping', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
  shipping_address TEXT NOT NULL,
  phone VARCHAR(20) NOT NULL,
  note TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_orders_created_at (created_at),
  INDEX idx_orders_status (status)
) ENGINE=InnoDB;

CREATE TABLE order_items (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(12,2) NOT NULL,
  subtotal DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id),
  CONSTRAINT chk_order_items_quantity CHECK (quantity > 0)
) ENGINE=InnoDB;

CREATE TABLE trade_ins (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  full_name VARCHAR(150) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  item_description TEXT NOT NULL,
  condition_grade ENUM('like_new', 'good', 'fair', 'worn_out') NOT NULL,
  pickup_address TEXT NOT NULL,
  status ENUM('pending', 'approved', 'collected', 'rejected') NOT NULL DEFAULT 'pending',
  voucher_code VARCHAR(50) NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_trade_ins_user FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_trade_ins_status_created (status, created_at)
) ENGINE=InnoDB;

CREATE TABLE articles (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  slug VARCHAR(255) NOT NULL UNIQUE,
  category_type ENUM('news', 'event', 'eco_guide') NOT NULL DEFAULT 'news',
  short_summary VARCHAR(500) NULL,
  content LONGTEXT NOT NULL,
  image_url VARCHAR(500) NULL,
  source_url VARCHAR(500) NULL,
  views INT NOT NULL DEFAULT 0,
  is_published BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_articles_published_created (is_published, created_at)
) ENGINE=InnoDB;

CREATE TABLE contacts (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(150) NOT NULL,
  email VARCHAR(150) NOT NULL,
  phone VARCHAR(20) NULL,
  content TEXT NOT NULL,
  status ENUM('new', 'read', 'replied') NOT NULL DEFAULT 'new',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_contacts_status_created (status, created_at)
) ENGINE=InnoDB;
