from flask import Flask, request, jsonify, send_from_directory
import pyodbc
import random
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

# --------------------------------
# DATABASE CONNECTION
# --------------------------------

conn = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=BERNARD\\SQLEXPRESS01;"
    "Database=SunforgeMarkets;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()


# --------------------------------
# SERVE FRONTEND HTML
# --------------------------------

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


@app.route('/create-portfolio')
def create_portfolio_page():
    return send_from_directory('.', 'create-portfolio.html')


@app.route('/view-portfolio')
def view_portfolio_page():
    return send_from_directory('.', 'view-portfolio.html')


# --------------------------------
# USER AUTHENTICATION
# --------------------------------

@app.route('/api/login', methods=['POST'])
def login():

    data = request.json
    username = data['username']
    email = data['email']

    cursor.execute(
        "SELECT * FROM Customer WHERE Username=? AND Email=?",
        username,
        email
    )

    user = cursor.fetchone()

    if user:
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid login"}), 401


# --------------------------------
# CREATE PORTFOLIO
# --------------------------------

@app.route('/api/create_portfolio', methods=['POST'])
def create_portfolio():

    data = request.json

    name = data['name']
    username = data['username']
    email = data['email']

    cursor.execute("""
        INSERT INTO Customer (FullName, Username, Email)
        VALUES (?, ?, ?)
    """, name, username, email)

    conn.commit()

    cursor.execute(
        "SELECT CustomerId FROM Customer WHERE Username=?",
        username
    )

    customer = cursor.fetchone()
    customer_id = customer[0]

    cursor.execute(
        "INSERT INTO Portfolio (CustomerId) VALUES (?)",
        customer_id
    )

    conn.commit()

    cursor.execute(
        "SELECT PortfolioId FROM Portfolio WHERE CustomerId=?",
        customer_id
    )

    portfolio = cursor.fetchone()
    portfolio_id = portfolio[0]

    cursor.execute(
        "INSERT INTO CashAccount (PortfolioId, Balance) VALUES (?,0)",
        portfolio_id
    )

    conn.commit()

    return jsonify({"message": "Portfolio created successfully"})


# --------------------------------
# VIEW PORTFOLIO
# --------------------------------

@app.route('/api/view_portfolio/<username>')
def view_portfolio(username):

    cursor.execute("""
        SELECT Customer.FullName,
               CashAccount.Balance
        FROM Customer
        JOIN Portfolio
            ON Customer.CustomerId = Portfolio.CustomerId
        JOIN CashAccount
            ON Portfolio.PortfolioId = CashAccount.PortfolioId
        WHERE Customer.Username = ?
    """, username)

    result = cursor.fetchone()

    if result:
        return jsonify({
            "name": result[0],
            "balance": float(result[1])
        })

    return jsonify({"message": "Portfolio not found"})


# --------------------------------
# BUY STOCK
# --------------------------------

@app.route('/api/buy_stock', methods=['POST'])
def buy_stock():

    data = request.json

    portfolio_id = data['portfolio_id']
    stock_id = data['stock_id']
    quantity = data['quantity']

    if not market_open():
        return jsonify({"message": "Market is closed"}), 400

    cursor.execute("""
        INSERT INTO Orders
        (PortfolioId, StockId, OrderType, Quantity)
        VALUES (?, ?, 'BUY', ?)
    """, portfolio_id, stock_id, quantity)

    conn.commit()

    return jsonify({"message": "Buy order created"})


# --------------------------------
# SELL STOCK
# --------------------------------

@app.route('/api/sell_stock', methods=['POST'])
def sell_stock():

    data = request.json

    portfolio_id = data['portfolio_id']
    stock_id = data['stock_id']
    quantity = data['quantity']

    if not market_open():
        return jsonify({"message": "Market is closed"}), 400

    cursor.execute("""
        INSERT INTO Orders
        (PortfolioId, StockId, OrderType, Quantity)
        VALUES (?, ?, 'SELL', ?)
    """, portfolio_id, stock_id, quantity)

    conn.commit()

    return jsonify({"message": "Sell order created"})


# --------------------------------
# ADMIN CREATE STOCK
# --------------------------------

@app.route('/api/create_stock', methods=['POST'])
def create_stock():

    data = request.json

    name = data['name']
    ticker = data['ticker']
    volume = data['volume']
    price = data['price']

    cursor.execute("""
        INSERT INTO Stock
        (CompanyName, Ticker, TotalVolume, CurrentPrice)
        VALUES (?, ?, ?, ?)
    """, name, ticker, volume, price)

    conn.commit()

    return jsonify({"message": "Stock created"})


# --------------------------------
# MARKET HOURS CHECK
# --------------------------------

def market_open():

    now = datetime.now()

    cursor.execute("""
        SELECT OpenTime, CloseTime
        FROM MarketHours
        WHERE DayOfWeek = DATENAME(WEEKDAY, GETDATE())
    """)

    hours = cursor.fetchone()

    if not hours:
        return True

    open_time = datetime.strptime(hours[0], "%H:%M").time()
    close_time = datetime.strptime(hours[1], "%H:%M").time()

    return open_time <= now.time() <= close_time


# --------------------------------
# RANDOM STOCK PRICE GENERATOR
# --------------------------------

@app.route('/api/update_prices')
def update_prices():

    cursor.execute(
        "SELECT StockId, CurrentPrice FROM Stock"
    )

    stocks = cursor.fetchall()

    for stock in stocks:

        change = random.uniform(-2, 2)
        new_price = stock[1] + change

        cursor.execute("""
            UPDATE Stock
            SET CurrentPrice=?
            WHERE StockId=?
        """, new_price, stock[0])

    conn.commit()

    return jsonify({"message": "Prices updated"})


# --------------------------------
# RUN SERVER
# --------------------------------

if __name__ == '__main__':
    app.run(debug=True)