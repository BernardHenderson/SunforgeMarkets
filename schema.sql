-- =========================================
-- CUSTOMER TABLE
-- =========================================
CREATE TABLE Customer (
    CustomerId INT IDENTITY(1,1) PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Email VARCHAR(100) NOT NULL
);


-- =========================================
-- PORTFOLIO TABLE
-- =========================================
CREATE TABLE Portfolio (
    PortfolioId INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL,
    FOREIGN KEY (CustomerId) REFERENCES Customer(CustomerId)
);


-- =========================================
-- CASH ACCOUNT TABLE
-- =========================================
CREATE TABLE CashAccount (
    CashAccountId INT IDENTITY(1,1) PRIMARY KEY,
    PortfolioId INT NOT NULL,
    Balance DECIMAL(12,2) DEFAULT 0,
    FOREIGN KEY (PortfolioId) REFERENCES Portfolio(PortfolioId)
);


-- =========================================
-- STOCK TABLE
-- =========================================
CREATE TABLE Stock (
    StockId INT IDENTITY(1,1) PRIMARY KEY,
    CompanyName VARCHAR(100) NOT NULL,
    Ticker VARCHAR(10) UNIQUE NOT NULL,
    TotalVolume INT,
    CurrentPrice DECIMAL(10,2)
);


-- =========================================
-- HOLDING TABLE
-- =========================================
CREATE TABLE Holding (
    HoldingId INT IDENTITY(1,1) PRIMARY KEY,
    PortfolioId INT NOT NULL,
    StockId INT NOT NULL,
    Quantity INT DEFAULT 0,
    FOREIGN KEY (PortfolioId) REFERENCES Portfolio(PortfolioId),
    FOREIGN KEY (StockId) REFERENCES Stock(StockId)
);


-- =========================================
-- ORDERS TABLE
-- =========================================
CREATE TABLE Orders (
    OrderId INT IDENTITY(1,1) PRIMARY KEY,
    PortfolioId INT NOT NULL,
    StockId INT NOT NULL,
    OrderType VARCHAR(10) CHECK (OrderType IN ('BUY','SELL')),
    Quantity INT NOT NULL,
    Status VARCHAR(20) DEFAULT 'PENDING',
    DateCreated DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (PortfolioId) REFERENCES Portfolio(PortfolioId),
    FOREIGN KEY (StockId) REFERENCES Stock(StockId)
);


-- =========================================
-- TRANSACTIONS TABLE
-- =========================================
CREATE TABLE Transactions (
    TransactionId INT IDENTITY(1,1) PRIMARY KEY,
    PortfolioId INT NOT NULL,
    StockId INT NOT NULL,
    Quantity INT NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    TransactionDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (PortfolioId) REFERENCES Portfolio(PortfolioId),
    FOREIGN KEY (StockId) REFERENCES Stock(StockId)
);


-- =========================================
-- MARKET HOURS TABLE
-- =========================================
CREATE TABLE MarketHours (
    MarketHoursId INT IDENTITY(1,1) PRIMARY KEY,
    DayOfWeek VARCHAR(20),
    OpenTime VARCHAR(10),
    CloseTime VARCHAR(10)
);