/*
╔══════════════════════════════════════════════════════════════════╗
║          FILE 2 — DỮ LIỆU MẪU (INSERT DATA) - ĐƠN GIẢN         ║
║  Chạy file này SAU file 01_TaoDB_Simple.sql                    ║
╚══════════════════════════════════════════════════════════════════╝
*/

USE CinemaDB;
GO

-- ============================================================
-- SECTION A — PHIM
-- ============================================================
PRINT N'--- Thêm phim ---';

INSERT INTO Movies (title, genre, duration, rating, director, release_date) VALUES
(N'Avatar: The Way of Water', N'Sci-Fi', 192, 8.5, N'James Cameron', '2022-12-16'),
(N'The Batman', N'Action', 176, 8.2, N'Matt Reeves', '2022-03-04'),
(N'Oppenheimer', N'Biography', 180, 8.8, N'Christopher Nolan', '2023-07-21'),
(N'Dune: Part Two', N'Sci-Fi', 166, 8.7, N'Denis Villeneuve', '2024-03-01'),
(N'Deadpool 3', N'Action', 127, 9.0, N'Shawn Levy', '2024-07-26'),
(N'Inside Out 2', N'Animation', 100, 8.9, N'Kelsey Mann', '2024-06-14');

PRINT N'✅ Phim đã thêm xong';
GO

-- ============================================================
-- SECTION B — PHÒNG CHIẾU
-- ============================================================
PRINT N'--- Thêm phòng chiếu ---';

INSERT INTO Screens (screen_name, total_seats) VALUES
(N'Phòng Chiếu 1', 80);

PRINT N'✅ Phòng chiếu đã thêm xong';
GO

-- ============================================================
-- SECTION C — TẠO GHẾ (8 hàng x 10 cột = 80 ghế)
-- ============================================================
PRINT N'--- Tạo ghế ---';

DECLARE @sid INT = 1, @r INT = 1, @c INT, @cnt INT = 0;

WHILE @r <= 8
BEGIN
    SET @c = 1;
    WHILE @c <= 10
    BEGIN
        INSERT INTO Seats (screen_id, seat_number, row_label, seat_type, base_price) 
        VALUES (
            @sid,
            CHAR(64 + @r) + CAST(@c AS VARCHAR),
            CHAR(64 + @r),
            CASE 
                WHEN @r IN (4,5) THEN 'VIP'   -- D và E là hàng 4,5
                WHEN @r >= 7 THEN 'Couple' 
                ELSE 'Standard' 
            END,
            CASE 
                WHEN @r IN (4,5) THEN 130000   -- VIP giá 130000
                WHEN @r >= 7 THEN 150000 
                ELSE 90000 
            END,
        );
        SET @cnt = @cnt + 1;
        SET @c = @c + 1;
    END
    SET @r = @r + 1;
END

PRINT N'✅ Đã tạo ' + CAST(@cnt AS NVARCHAR) + N' ghế cho phòng chiếu';
GO

-- ============================================================
-- SECTION D — SUẤT CHIẾU
-- ============================================================
PRINT N'--- Thêm suất chiếu ---';

DECLARE @today DATE = CAST(GETDATE() AS DATE);

-- Suất chiếu cho 7 ngày tới
INSERT INTO Showtimes (movie_id, screen_id, show_date, show_time, base_price) VALUES
-- Ngày 1
(1, 1, @today, '09:00:00', 100000),
(1, 1, @today, '14:00:00', 100000),
(3, 1, @today, '19:00:00', 100000),

-- Ngày 2
(2, 1, DATEADD(DAY, 1, @today), '10:00:00', 100000),
(2, 1, DATEADD(DAY, 1, @today), '15:00:00', 100000),
(4, 1, DATEADD(DAY, 1, @today), '20:00:00', 100000),

-- Ngày 3
(3, 1, DATEADD(DAY, 2, @today), '09:30:00', 100000),
(3, 1, DATEADD(DAY, 2, @today), '14:30:00', 100000),
(1, 1, DATEADD(DAY, 2, @today), '19:30:00', 100000),

-- Ngày 4
(4, 1, DATEADD(DAY, 3, @today), '10:30:00', 100000),
(4, 1, DATEADD(DAY, 3, @today), '15:30:00', 100000),
(2, 1, DATEADD(DAY, 3, @today), '20:30:00', 100000),

-- Ngày 5
(5, 1, DATEADD(DAY, 4, @today), '11:00:00', 100000),
(5, 1, DATEADD(DAY, 4, @today), '16:00:00', 100000),
(6, 1, DATEADD(DAY, 4, @today), '21:00:00', 100000),

-- Ngày 6
(6, 1, DATEADD(DAY, 5, @today), '08:00:00', 100000),
(6, 1, DATEADD(DAY, 5, @today), '13:00:00', 100000),
(5, 1, DATEADD(DAY, 5, @today), '18:00:00', 100000),

-- Ngày 7
(1, 1, DATEADD(DAY, 6, @today), '09:00:00', 100000),
(2, 1, DATEADD(DAY, 6, @today), '14:00:00', 100000),
(3, 1, DATEADD(DAY, 6, @today), '19:00:00', 100000);

PRINT N'✅ Suất chiếu đã thêm xong';
GO

-- ============================================================
-- SECTION E — ĐỒ ĂN & NƯỚC UỐNG
-- ============================================================
PRINT N'--- Thêm đồ ăn & nước ---';

INSERT INTO Food_Items (food_name, category, price) VALUES
(N'Bắp rang Caramel (S)', N'Snack', 35000),
(N'Bắp rang Caramel (M)', N'Snack', 45000),
(N'Bắp rang Caramel (L)', N'Snack', 55000),
(N'Bắp rang Cheese (S)',  N'Snack', 35000),
(N'Bắp rang Cheese (M)',  N'Snack', 45000),
(N'Bắp rang Cheese (L)',  N'Snack', 55000),
(N'Bắp rang Mix (S)', N'Snack', 40000),
(N'Bắp rang Mix (M)', N'Snack', 50000),
(N'Bắp rang Mix (L)', N'Snack', 60000),
(N'Pepsi',                N'Drink', 30000),
(N'Coca-Cola',            N'Drink', 30000),
(N'Fanta Cam',            N'Drink', 30000),
(N'7UP',                  N'Drink', 30000),
(N'Combo 1 (Bắp M + Nước)', N'Combo', 80000),
(N'Combo 2 (Bắp L + 2 Nước)', N'Combo', 120000);

PRINT N'✅ Đồ ăn đã thêm xong';
GO

-- ============================================================
-- SECTION F — NHÂN VIÊN
-- ============================================================
PRINT N'--- Thêm nhân viên ---';

INSERT INTO Employees (full_name, position, phone, email, salary, password_hash, is_active) VALUES
(N'Nguyễn Thanh Bình', N'Quản lý',  '0908888888', 'manager@cinema.vn',  20000000, 'admin123', 1),
(N'Lê Minh Tú',        N'Nhân viên', '0907777777', 'cashier@cinema.vn',  10000000, 'tu123',    1),
(N'Trần Hoàng Nam',    N'Nhân viên', '0906666666', 'tech@cinema.vn',     12000000, 'nam123',   1);

PRINT N'✅ Nhân viên đã thêm xong';
GO

PRINT N'';
PRINT N'╔════════════════════════════════════════════════════════╗';
PRINT N'║  ✅ FILE 2 HOÀN THÀNH — Dữ liệu mẫu đã insert xong  ║';
PRINT N'╚════════════════════════════════════════════════════════╝';
GO