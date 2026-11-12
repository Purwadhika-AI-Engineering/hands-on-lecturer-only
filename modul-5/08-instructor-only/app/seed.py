"""Create the SYNTHETIC Acme database. Every name, number and address is fake."""
from __future__ import annotations

import os
import random
import sqlite3

from app import config

FIRST = ["Budi", "Siti", "Agus", "Dewi", "Rina", "Eko", "Putri", "Andi", "Maya", "Hendra", "Lestari", "Yoga", "Nadia", "Fajar", "Sari"]
LAST = ["Santoso", "Wijaya", "Pratama", "Kusuma", "Hidayat", "Saputra", "Lestari", "Nugroho", "Rahayu", "Setiawan"]
CITIES = ["Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Medan", "Semarang", "Denpasar", "Makassar"]
PRODUCTS = [
    ("Kopi Gayo 250g", "coffee", 85000, 120), ("Kopi Toraja 250g", "coffee", 92000, 80), ("Teh Melati 100g", "tea", 45000, 200),
    ("Batik Tulis Shirt", "apparel", 350000, 35), ("Tenun Ikat Scarf", "apparel", 275000, 40), ("Rattan Basket", "home", 180000, 25),
    ("Wooden Coaster Set", "home", 95000, 60), ("Sambal Matah 200g", "food", 38000, 150), ("Kerupuk Udang 500g", "food", 52000, 90),
    ("Batik Notebook", "stationery", 48000, 110), ("Ceramic Mug", "home", 65000, 70), ("Cold Brew Bottle", "coffee", 78000, 55),
]
EMPLOYEES = [
    ("Ratna Anggraini", "Head of Support", 18500000), ("Dimas Prakoso", "Warehouse Lead", 12000000), ("Wulan Sari", "Finance Manager", 22000000),
    ("Bagus Firmansyah", "Customer Support", 8500000), ("Intan Permata", "Customer Support", 8500000), ("Taufik Ramadhan", "Engineer", 20000000),
]
STATUSES = ["pending", "paid", "shipped", "delivered", "delivered", "delivered", "cancelled"]


def seed(reset: bool = True) -> None:
    config.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if reset:
        for p in (config.DB_PATH, config.OUTBOX_PATH):
            if p.exists():
                os.remove(p)
        for f in config.UPLOAD_DIR.glob("*"):
            f.unlink()
    rng = random.Random(42)
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.executescript(
        """
        CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT, category TEXT, price_idr INTEGER, stock INTEGER);
        CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, nik TEXT, address TEXT, city TEXT);
        CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, product_id INTEGER, qty INTEGER, total_idr INTEGER, status TEXT, created_at TEXT);
        CREATE TABLE employees(id INTEGER PRIMARY KEY, name TEXT, role TEXT, salary_idr INTEGER, email TEXT);
        """
    )
    c.executemany("INSERT INTO products(name,category,price_idr,stock) VALUES (?,?,?,?)", PRODUCTS)
    for i in range(1, 26):
        name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
        email = f"{name.lower().replace(' ', '.')}{i}@mail.example"
        phone = f"+62812{rng.randint(10000000, 99999999)}"
        nik = "3171" + "".join(str(rng.randint(0, 9)) for _ in range(12))
        c.execute(
            "INSERT INTO customers(name,email,phone,nik,address,city) VALUES (?,?,?,?,?,?)",
            (name, email, phone, nik, f"Jl. Contoh No. {rng.randint(1, 99)}", rng.choice(CITIES)),
        )
    for i in range(1, 61):
        pid = rng.randint(1, len(PRODUCTS))
        qty = rng.randint(1, 4)
        total = PRODUCTS[pid - 1][2] * qty
        c.execute(
            "INSERT INTO orders(customer_id,product_id,qty,total_idr,status,created_at) VALUES (?,?,?,?,?,?)",
            (rng.randint(1, 25), pid, qty, total, rng.choice(STATUSES), f"2026-{rng.randint(8, 10):02d}-{rng.randint(1, 28):02d}"),
        )
    for name, role, salary in EMPLOYEES:
        c.execute("INSERT INTO employees(name,role,salary_idr,email) VALUES (?,?,?,?)", (name, role, salary, f"{name.split()[0].lower()}@{config.INTERNAL_EMAIL_DOMAIN}"))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed(reset=True)
    print(f"seeded {config.DB_PATH}")
