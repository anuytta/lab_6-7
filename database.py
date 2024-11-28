import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import shutil

os.chdir('/Users/annacernega/Desktop/Education/web/site1')

app = Flask(__name__)
app.secret_key = 'some_secret_key'  # для сесій, зокрема для кошика
app.config['UPLOAD_FOLDER'] = 'static/images' 

def get_db_connection():
    conn = sqlite3.connect('store.db')
    conn.row_factory = sqlite3.Row
    return conn

# Підключення до бази даних
conn = sqlite3.connect('store.db')
cursor = conn.cursor()



# Створення таблиць
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image TEXT,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories (id)
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    address TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    address TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

conn.commit()


def add_product(name, description, price, image, category_id):
    conn = sqlite3.connect('store.db')  # Відкриваємо з'єднання
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, description, price, image, category_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, description, price, image, category_id))
    conn.commit()
    conn.close()  # Закриваємо з'єднання

def add_product_console():
    name = input("Введіть назву товару: ")
    description = input("Введіть опис товару: ")
    price = float(input("Введіть ціну товару: "))
    image = input("Введіть шлях до зображення товару (наприклад, static/images/test.jpeg): ")

    print("Виберіть категорію товару:")
    print("1. Обличчя")
    print("2. Волосся")
    print("3. Тіло")
    
    category_id = input("Введіть номер категорії (1-3): ")
    
    # Перевірка на валідність введення категорії
    if category_id not in ['1', '2', '3']:
        print("Невірний номер категорії. Спробуйте знову.")
        return

    category_id = int(category_id)

    # Перевірка, чи існує файл зображення
    if not os.path.isfile(image):
        print(f"Фото {image} не знайдено за вказаним шляхом.")
        return  # Завершуємо функцію, якщо файл не знайдений
    
    # Отримуємо назву файлу із шляху
    image_filename = os.path.basename(image)
    
    # Вказуємо шлях до папки для збереження фото
    destination_folder = 'static/images'
    
    # Формуємо шлях до місця, куди треба скопіювати файл
    destination = os.path.join(destination_folder, image_filename)
    
    # Перевіряємо, чи існує папка для збереження
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)  # Створюємо папку, якщо її немає

    # Перевірка, чи файл вже є в цільовій папці
    if os.path.exists(destination):
        print(f"Фото {image_filename} вже існує в папці {destination_folder}.")
    else:
        # Копіюємо файл у папку проекту
        try:
            shutil.copy(image, destination)  # Копіюємо файл з вказаного шляху
            print(f"Фото {image_filename} успішно додано!")
        except FileNotFoundError:
            print(f"Фото {image_filename} не знайдено за вказаним шляхом: {image}")
            return  # Завершуємо функцію, якщо файл не знайдений

    # Додаємо товар у базу даних
    add_product(name, description, price, image_filename, category_id)
    print("Товар успішно додано!")



# Додавання клієнта
def add_customer(name, email, phone, address):
    cursor.execute('''
    INSERT INTO customers (name, email, phone, address)
    VALUES (?, ?, ?, ?)
    ''', (name, email, address))
    conn.commit()

# Додавання замовлення
def add_order(customer_id, product_id, quantity, address):
    order_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    INSERT INTO orders (customer_id, product_id, quantity, order_date, address)
    VALUES (?, ?, ?, ?, ?)
    ''', (customer_id, product_id, quantity, order_date, address))
    conn.commit()

# Отримання всіх продуктів
def get_all_products():
    cursor.execute('SELECT * FROM products')
    return cursor.fetchall()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/brand')
def brand():
    return render_template('brand.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/order_placed')
def order_placed():
    return render_template('order_placed.html')

@app.route('/present')
def present():
    return render_template('present.html')


@app.route('/catalog')
def catalog():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return render_template('catalog.html', products=products, categories=categories)


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    return redirect(url_for('catalog'))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    conn = get_db_connection()
    products = [conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone() for product_id in cart]
    conn.close()
    # Фільтруємо продукти, які не знайдені
    products = [product for product in products if product is not None]
    return render_template('cart.html', products=products)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        customer_name = request.form['name']
        customer_email = request.form['email']
        customer_address = request.form['address']
        cart = session.get('cart', [])

        conn = get_db_connection()

        # Перевіряємо, чи клієнт з цією електронною поштою вже існує
        existing_customer = conn.execute('SELECT id FROM customers WHERE email = ?', (customer_email,)).fetchone()

        if existing_customer:
            # Якщо клієнт існує, використовуємо його ID
            customer_id = existing_customer['id']
        else:
            # Якщо клієнт не існує, додаємо нового
            conn.execute('INSERT INTO customers (name, email, address) VALUES (?, ?, ?)',
                         (customer_name, customer_email, customer_address))
            customer_id = conn.execute('SELECT id FROM customers WHERE email = ?', (customer_email,)).fetchone()['id']

        for product_id in cart:
            conn.execute('INSERT INTO orders (customer_id, product_id, quantity, order_date, address) VALUES (?, ?, 1, datetime("now"), ?)',
                         (customer_id, product_id, customer_address))
        
        conn.commit()
        conn.close()

        # Очистка кошика після оформлення замовлення
        session.pop('cart', None)

    return render_template('checkout.html')













def get_categories():
    with sqlite3.connect('store.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        return categories
    
# Маршрут для відображення сторінки категорії
@app.route('/category/<int:category_id>')
def category_page(category_id):
    products = get_products_by_category(category_id)
    return render_template('category_page.html', products=products)

# Функція для отримання товарів за категорією
def get_products_by_category(category_id):
    with sqlite3.connect('store.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE category_id = ?", (category_id,))
        products = cursor.fetchall()
        return products
    
@app.route('/catalog/category/<int:category_id>')
def category_products(category_id):
    conn = get_db_connection()

    # Отримати назву категорії
    category = conn.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()

    if not category:
        conn.close()
        return "Категорію не знайдено", 404

    # Отримати всі товари цієї категорії
    products = conn.execute('SELECT * FROM products WHERE category_id = ?', (category_id,)).fetchall()
    conn.close()

    # Повернути шаблон з товарами
    return render_template('category_products.html', category=category, products=products)



# if __name__ == "__main__":
#     app.run(debug=True)
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)



# def show_menu():
#     while True:
#         print("\n1. Додати товар")
#         print("2. Вийти")
#         choice = input("Виберіть дію (1/2): ")

#         if choice == '1':
#              add_product_console()
#         elif choice == '2':
#              print("До побачення!")
#              break
#         else:
#              print("Невірний вибір, спробуйте ще раз.")

# if __name__ == "__main__":
#      show_menu()
