/*
╔══════════════════════════════════════════════════════════════════╗
║          FILE 1 — TẠO DATABASE & CÁC BẢNG (ĐƠN GIẢN)           ║
║  Chạy file này TRƯỚC TIÊN khi setup lần đầu hoặc reset lại DB  ║
║  ✅ Đã xóa các bậc thành viên, điểm tích lũy, discount         ║
║  ✅ Đã xóa giảm giá giờ sáng và tăng giá cuối tuần             ║
╚══════════════════════════════════════════════════════════════════╝
*/

USE master;
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = 'CinemaDB')
BEGIN
    ALTER DATABASE CinemaDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE CinemaDB;
    PRINT N'✅ Đã xóa database CinemaDB cũ!';
END
GO

CREATE DATABASE CinemaDB;
GO
PRINT N'✅ Đã tạo database CinemaDB mới!';
GO

USE CinemaDB;
GO

-- ============================================================
-- 1. BẢNG MOVIES — Phim
-- ============================================================
CREATE TABLE Movies (
    movie_id     INT           PRIMARY KEY IDENTITY(1,1),
    title        NVARCHAR(200) NOT NULL,
    genre        NVARCHAR(50),
    duration     INT           CHECK (duration > 0 AND duration <= 600),
    rating       DECIMAL(2,1)  CHECK (rating >= 0 AND rating <= 10),
    director     NVARCHAR(100),
    release_date DATE
);
GO
PRINT N'✅ Bảng Movies';
GO

-- ============================================================
-- 2. BẢNG SCREENS — Phòng chiếu
-- ============================================================
CREATE TABLE Screens (
    screen_id   INT          PRIMARY KEY IDENTITY(1,1),
    screen_name NVARCHAR(50) NOT NULL,
    total_seats INT          CHECK (total_seats > 0 AND total_seats <= 500)
);
GO
PRINT N'✅ Bảng Screens';
GO

-- ============================================================
-- 3. BẢNG SEATS — Ghế ngồi
-- ============================================================
CREATE TABLE Seats (
    seat_id     INT          PRIMARY KEY IDENTITY(1,1),
    screen_id   INT          NOT NULL,
    seat_number VARCHAR(10)  NOT NULL,
    row_label   VARCHAR(5)   NOT NULL,
    seat_type   NVARCHAR(20) CHECK (seat_type IN ('VIP','Standard','Couple')) DEFAULT 'Standard',
    base_price  DECIMAL(10,2) CHECK (base_price > 0 AND base_price <= 1000000),
    FOREIGN KEY (screen_id) REFERENCES Screens(screen_id) ON DELETE CASCADE,
    CONSTRAINT UQ_Seat UNIQUE (screen_id, seat_number, row_label)
);
GO
PRINT N'✅ Bảng Seats';
GO

-- ============================================================
-- 4. BẢNG CUSTOMERS — Khách hàng (đơn giản)
-- ============================================================
CREATE TABLE Customers (
    customer_id       INT           PRIMARY KEY IDENTITY(1,1),
    full_name         NVARCHAR(100) NOT NULL,
    phone             VARCHAR(15)   NOT NULL,
    registration_date DATETIME      DEFAULT GETDATE(),
    CONSTRAINT UQ_Customers_Phone UNIQUE (phone),  -- SĐT là duy nhất
    CONSTRAINT CK_Phone CHECK (LEN(phone) = 10 AND phone LIKE '0[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]')
);
GO
PRINT N'✅ Bảng Customers';
GO

-- ============================================================
-- 5. BẢNG SHOWTIMES — Suất chiếu
-- ============================================================
CREATE TABLE Showtimes (
    showtime_id INT           PRIMARY KEY IDENTITY(1,1),
    movie_id    INT           NOT NULL,
    screen_id   INT           NOT NULL,
    show_date   DATE          NOT NULL,
    show_time   TIME          NOT NULL,
    base_price  DECIMAL(10,2) CHECK (base_price > 0 AND base_price <= 1000000) DEFAULT 100000,
    FOREIGN KEY (movie_id)  REFERENCES Movies(movie_id)  ON DELETE CASCADE,
    FOREIGN KEY (screen_id) REFERENCES Screens(screen_id) ON DELETE CASCADE,
    CONSTRAINT UQ_Showtime UNIQUE (screen_id, show_date, show_time)
);
GO
PRINT N'✅ Bảng Showtimes';
GO

-- ============================================================
-- 6. BẢNG EMPLOYEES — Nhân viên
-- ============================================================
CREATE TABLE Employees (
    employee_id   INT           PRIMARY KEY IDENTITY(1,1),
    full_name     NVARCHAR(150) NOT NULL,
    position      NVARCHAR(100),
    phone         VARCHAR(15),
    email         VARCHAR(100),
    hire_date     DATE          DEFAULT GETDATE(),
    salary        DECIMAL(12,2) CHECK (salary > 0),
    password_hash VARCHAR(64)   NOT NULL DEFAULT '123456',
    is_active     BIT           DEFAULT 1
);
GO
PRINT N'✅ Bảng Employees';
GO

-- ============================================================
-- 7. BẢNG BOOKINGS — Đơn đặt vé
-- ============================================================
CREATE TABLE Bookings (
    booking_id     INT           PRIMARY KEY IDENTITY(1,1),
    customer_id    INT           NOT NULL,
    showtime_id    INT           NOT NULL,
    employee_id    INT           NULL,
    booking_date   DATETIME      DEFAULT GETDATE(),
    total_seats    INT           CHECK (total_seats > 0 AND total_seats <= 10),
    total_amount   DECIMAL(10,2) CHECK (total_amount >= 0),
    booking_status NVARCHAR(20)  CHECK (booking_status IN ('Pending','Confirmed','Cancelled')) DEFAULT 'Pending',
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)  ON DELETE CASCADE,
    FOREIGN KEY (showtime_id) REFERENCES Showtimes(showtime_id)  ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)  ON DELETE SET NULL
);
GO
PRINT N'✅ Bảng Bookings';
GO

-- ============================================================
-- 8. BẢNG BOOKING_DETAILS — Chi tiết ghế trong đơn
-- ============================================================
CREATE TABLE Booking_Details (
    detail_id   INT           PRIMARY KEY IDENTITY(1,1),
    booking_id  INT           NOT NULL,
    seat_id     INT           NOT NULL,
    seat_price  DECIMAL(10,2) CHECK (seat_price > 0),
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id)    REFERENCES Seats(seat_id)
);
GO
PRINT N'✅ Bảng Booking_Details';
GO

-- ============================================================
-- 9. BẢNG FOOD_ITEMS — Đồ ăn uống
-- ============================================================
CREATE TABLE Food_Items (
    food_id   INT           PRIMARY KEY IDENTITY(1,1),
    food_name NVARCHAR(200) NOT NULL,
    category  NVARCHAR(50),
    price     DECIMAL(10,2) CHECK (price > 0)
);
GO
PRINT N'✅ Bảng Food_Items';
GO

-- ============================================================
-- 10. BẢNG BOOKING_FOOD — Đồ ăn trong đơn đặt vé
-- ============================================================
CREATE TABLE Booking_Food (
    booking_food_id INT           PRIMARY KEY IDENTITY(1,1),
    booking_id      INT           NOT NULL,
    food_id         INT           NOT NULL,
    quantity        INT           CHECK (quantity > 0),
    unit_price      DECIMAL(10,2),
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id)   ON DELETE CASCADE,
    FOREIGN KEY (food_id)    REFERENCES Food_Items(food_id)
);
GO
PRINT N'✅ Bảng Booking_Food';
GO

-- ============================================================
-- 11. BẢNG PAYMENTS — Thanh toán
-- ============================================================
CREATE TABLE Payments (
    payment_id     INT           PRIMARY KEY IDENTITY(1,1),
    booking_id     INT           NOT NULL UNIQUE,
    payment_date   DATETIME      DEFAULT GETDATE(),
    amount         DECIMAL(10,2) CHECK (amount >= 0),
    payment_status NVARCHAR(20)  CHECK (payment_status IN ('Pending','Paid','Refunded')) DEFAULT 'Pending',
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id) ON DELETE CASCADE
);
GO
PRINT N'✅ Bảng Payments';
GO

PRINT N'';
PRINT N'╔════════════════════════════════════════════════════╗';
PRINT N'║  ✅ FILE 1 HOÀN THÀNH — 11 bảng đã tạo xong      ║';
PRINT N'║  ✅ Đã xóa các bậc thành viên và điểm tích lũy    ║';
PRINT N'║  ✅ Đã xóa giảm giá giờ sáng và tăng giá cuối tuần ║';
PRINT N'╚════════════════════════════════════════════════════╝';
GO