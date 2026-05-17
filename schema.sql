DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS food_categories;
DROP TABLE IF EXISTS restaurant;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS foodtype;
DROP TABLE IF EXISTS dishes;
DROP TABLE IF EXISTS media;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS contact_admin;
DROP TABLE IF EXISTS contact_restaurant;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  usertype TINYINT NOT NULL DEFAULT 0,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  isblocked INTEGER NOT NULL DEFAULT 0,
  purchased INTEGER NOT NULL DEFAULT 0,
  last_order TEXT
);

CREATE TABLE restaurant (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  restaurant_name TEXT UNIQUE NOT NULL,
  usertype TINYINT NOT NULL DEFAULT 1,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  isblocked INTEGER NOT NULL DEFAULT 0,
  sold INTEGER NOT NULL DEFAULT 0,
  last_order TEXT
);

CREATE TABLE food_categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category TEXT UNIQUE NOT NULL
);

CREATE TABLE reservations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  restaurant TEXT NOT NULL,
  full_name TEXT NOT NULL,
  number TEXT NOT NULL,
  date TEXT NOT NULL,
  time TEXT NOT NULL,
  party_size INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS foodtype(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  food_type TEXT UNIQUE NOT NULL
);

CREATE TABLE dishes (
  id INTEGER PRIMARY KEY,
  res_id INTEGER NOT NULL,
  dish_name TEXT NOT NULL,
  cuisine_type TEXT NOT NULL,
  description TEXT NOT NULL,
  price REAL NOT NULL,
  image BLOB NOT NULL,
  dietary_preference TEXT NOT NULL,
  rating FLOAT NOT NULL DEFAULT 0, 
  reviews INTEGER NOT NULL DEFAULT 0;
  FOREIGN KEY (res_id) REFERENCES restaurant(id)
);

CREATE TABLE media(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  res_id INTEGER NOT NULL,
  image BLOB NOT NULL,
  video BLOB NOT NULL,
  description TEXT NOT NULL,
  add_info TEXT NOT NULL,
  terms TEXT NOT NULL,
  FOREIGN KEY (res_id) REFERENCES restaurant(id)
);

CREATE TABLE cart(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  res_id INTEGER NOT NULL,
  image BLOB NOT NULL,
  title TEXT NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 1,
  price INTEGER NOT NULL,
  total INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (res_id) REFERENCES restaurant(id)
);

CREATE TABLE contact_admin (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  receipient_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  subject TEXT NOT NULL,
  message TEXT NOT NULL,
  message_type TEXT NOT NULL,
  date TEXT NOT NULL,
  FOREIGN KEY (receipient_id) REFERENCES user(usertype)
);

CREATE TABLE contact_restaurant (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  receipient_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  subject TEXT NOT NULL,
  message TEXT NOT NULL,
  message_type TEXT NOT NULL,
  date TEXT NOT NULL,
  FOREIGN KEY (receipient_id) REFERENCES restaurant(id)
);