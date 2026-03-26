/*
╔══════════════════════════════════════════════════════════════════╗
║     FILE 3 — PROCEDURES, FUNCTIONS (ĐƠN GIẢN)                   ║
║  Chạy file này SAU file 01 và 02                                ║
║  ✅ Đã xóa các discount, bậc thành viên, điểm tích lũy          ║
║  ✅ Đã xóa giảm giá giờ sáng và tăng giá cuối tuần             ║
╚══════════════════════════════════════════════════════════════════╝
*/

USE CinemaDB;
GO

-- ============================================================
-- FUNCTIONS
-- ============================================================

-- 1. Tính giá vé theo loại ghế (chỉ dựa vào base_price của ghế)
DROP FUNCTION IF EXISTS fn_TinhGiaVe;
GO

CREATE FUNCTION fn_TinhGiaVe(
    @seat_id INT
)
RETURNS DECIMAL(10,2) AS
BEGIN
    DECLARE @price DECIMAL(10,2);
    
    -- Lấy giá từ bảng Seats
    SELECT @price = base_price 
    FROM Seats 
    WHERE seat_id = @seat_id;
    
    RETURN @price;
END;
GO

-- 2. Danh sách ghế còn trống của suất chiếu
DROP FUNCTION IF EXISTS fn_KiemTraGheTrong;
GO

CREATE FUNCTION fn_KiemTraGheTrong(@showtime_id INT)
RETURNS TABLE AS RETURN (
    SELECT s.seat_id, s.seat_number, s.row_label, s.seat_type, s.base_price
    FROM Seats s
    WHERE s.screen_id = (SELECT screen_id FROM Showtimes WHERE showtime_id = @showtime_id)
    AND   s.seat_id NOT IN (
        SELECT bd.seat_id
        FROM Booking_Details bd
        JOIN Bookings b ON bd.booking_id = b.booking_id
        WHERE b.showtime_id = @showtime_id
        AND   b.booking_status != 'Cancelled'
    )
);
GO

-- 3. Đếm ghế đã đặt của suất chiếu
DROP FUNCTION IF EXISTS fn_DemGheDaDat;
GO

CREATE FUNCTION fn_DemGheDaDat(@showtime_id INT)
RETURNS INT AS
BEGIN
    DECLARE @count INT;
    SELECT @count = COUNT(bd.seat_id)
    FROM Booking_Details bd
    JOIN Bookings b ON bd.booking_id = b.booking_id
    WHERE b.showtime_id = @showtime_id
    AND   b.booking_status != 'Cancelled';
    RETURN ISNULL(@count,0);
END;
GO

-- 4. Tổng doanh thu theo ngày
DROP FUNCTION IF EXISTS fn_TinhTongDoanhThuTheoNgay;
GO

CREATE FUNCTION fn_TinhTongDoanhThuTheoNgay(@date DATE)
RETURNS DECIMAL(18,2) AS
BEGIN
    DECLARE @revenue DECIMAL(18,2);
    SELECT @revenue = SUM(amount)
    FROM Payments
    WHERE CAST(payment_date AS DATE) = @date
    AND   payment_status = 'Paid';
    RETURN ISNULL(@revenue,0);
END;
GO

PRINT N'✅ Tất cả Functions đã tạo xong';
GO

-- ============================================================
-- PROCEDURES
-- ============================================================

-- 1. Thêm phim mới
DROP PROCEDURE IF EXISTS sp_ThemPhimMoi;
GO

CREATE PROCEDURE sp_ThemPhimMoi
    @title        NVARCHAR(200),
    @genre        NVARCHAR(50),
    @duration     INT,
    @rating       DECIMAL(2,1) = NULL,
    @director     NVARCHAR(100),
    @release_date DATE         = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF @title IS NULL OR LEN(RTRIM(@title))=0
        BEGIN RAISERROR(N'Tên phim không được để trống!',16,1); RETURN; END
    IF @duration IS NULL OR @duration<=0 OR @duration>600
        BEGIN RAISERROR(N'Thời lượng phải từ 1–600 phút!',16,1); RETURN; END

    INSERT INTO Movies(title,genre,duration,rating,director,release_date)
    VALUES(@title,@genre,@duration,@rating,@director,@release_date);
    PRINT N'✅ Thêm phim thành công: ' + @title;
END;
GO

-- 2. Thêm suất chiếu
DROP PROCEDURE IF EXISTS sp_ThemSuatChieu;
GO

CREATE PROCEDURE sp_ThemSuatChieu
    @movie_id   INT,
    @screen_id  INT,
    @show_date  DATE,
    @show_time  TIME,
    @base_price DECIMAL(10,2) = 100000
AS
BEGIN
    SET NOCOUNT ON;
    IF NOT EXISTS (SELECT 1 FROM Movies WHERE movie_id=@movie_id)
        BEGIN RAISERROR(N'❌ Không tìm thấy phim!',16,1); RETURN; END
    IF NOT EXISTS (SELECT 1 FROM Screens WHERE screen_id=@screen_id)
        BEGIN RAISERROR(N'❌ Không tìm thấy phòng chiếu!',16,1); RETURN; END
    IF @show_date < CAST(GETDATE() AS DATE)
        BEGIN RAISERROR(N'❌ Ngày chiếu không được là quá khứ!',16,1); RETURN; END
    IF EXISTS (SELECT 1 FROM Showtimes
               WHERE screen_id=@screen_id AND show_date=@show_date AND show_time=@show_time)
        BEGIN RAISERROR(N'❌ Đã có suất chiếu vào thời gian này!',16,1); RETURN; END

    INSERT INTO Showtimes(movie_id,screen_id,show_date,show_time,base_price)
    VALUES(@movie_id,@screen_id,@show_date,@show_time,@base_price);
    PRINT N'✅ Thêm suất chiếu thành công! ID: ' + CAST(SCOPE_IDENTITY() AS NVARCHAR);
END;
GO

-- 3. Thêm khách hàng mới
DROP PROCEDURE IF EXISTS sp_ThemKhachHang;
GO

CREATE PROCEDURE sp_ThemKhachHang
    @full_name NVARCHAR(100),
    @phone     VARCHAR(15)
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @full_name IS NULL OR LEN(RTRIM(@full_name))=0
        BEGIN RAISERROR(N'Tên khách hàng không được để trống!',16,1); RETURN; END
    
    -- Kiểm tra số điện thoại: phải đúng 10 số và bắt đầu bằng 0
    IF @phone IS NULL OR LEN(@phone) != 10
        BEGIN RAISERROR(N'SĐT phải có đúng 10 số!',16,1); RETURN; END
    
    IF LEFT(@phone, 1) != '0'
        BEGIN RAISERROR(N'SĐT phải bắt đầu bằng số 0!',16,1); RETURN; END
    
    IF @phone LIKE '%[^0-9]%'
        BEGIN RAISERROR(N'SĐT chỉ được chứa chữ số!',16,1); RETURN; END
    
    IF EXISTS (SELECT 1 FROM Customers WHERE phone = @phone)
    BEGIN
        RAISERROR(N'❌ Số điện thoại %s đã được đăng ký!',16,1, @phone);
        RETURN;
    END
    
    INSERT INTO Customers(full_name, phone)
    VALUES(@full_name, @phone);
    
    PRINT N'✅ Thêm khách hàng thành công! ID: ' + CAST(SCOPE_IDENTITY() AS NVARCHAR);
END;
GO

-- 4. Tạo đơn đặt vé
DROP PROCEDURE IF EXISTS sp_TaoDonDatVe;
GO

CREATE PROCEDURE sp_TaoDonDatVe
    @customer_name NVARCHAR(100),
    @customer_phone VARCHAR(15),
    @showtime_id INT,
    @seat_ids    VARCHAR(MAX),
    @employee_id INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @customer_id INT;
    DECLARE @existing_name NVARCHAR(100);
    
    -- Kiểm tra số điện thoại: phải đúng 10 số và bắt đầu bằng 0
    IF LEN(@customer_phone) != 10
    BEGIN
        RAISERROR(N'❌ Số điện thoại phải có đúng 10 số!',16,1);
        RETURN;
    END
    
    IF LEFT(@customer_phone, 1) != '0'
    BEGIN
        RAISERROR(N'❌ Số điện thoại phải bắt đầu bằng số 0!',16,1);
        RETURN;
    END
    
    -- Kiểm tra chỉ chứa số
    IF @customer_phone LIKE '%[^0-9]%'
    BEGIN
        RAISERROR(N'❌ Số điện thoại chỉ được chứa chữ số!',16,1);
        RETURN;
    END
    
    -- Kiểm tra khách hàng đã tồn tại chưa
    SELECT @customer_id = customer_id, @existing_name = full_name 
    FROM Customers 
    WHERE phone = @customer_phone;
    
    IF @customer_id IS NOT NULL
    BEGIN
        -- Nếu SĐT đã tồn tại, kiểm tra xem tên có khớp không
        IF @existing_name != @customer_name
        BEGIN
            RAISERROR(N'❌ Số điện thoại %s đã được đăng ký cho khách hàng "%s". Không thể đặt vé với tên "%s"!', 
                      16, 1, @customer_phone, @existing_name, @customer_name);
            RETURN;
        END
        PRINT N'✅ Khách hàng đã tồn tại: ' + @customer_name;
    END
    ELSE
    BEGIN
        -- Tạo khách hàng mới
        INSERT INTO Customers(full_name, phone)
        VALUES(@customer_name, @customer_phone);
        SET @customer_id = SCOPE_IDENTITY();
        PRINT N'✅ Đã tạo khách hàng mới: ' + @customer_name;
    END

    -- Validate suất chiếu
    IF NOT EXISTS (SELECT 1 FROM Showtimes WHERE showtime_id=@showtime_id)
    BEGIN RAISERROR(N'❌ Suất chiếu không tồn tại!',16,1); RETURN; END

    IF @seat_ids IS NULL OR LEN(RTRIM(@seat_ids))=0
    BEGIN RAISERROR(N'❌ Danh sách ghế không được trống!',16,1); RETURN; END

    -- Parse seat IDs
    DECLARE @SeatTable TABLE (seat_id INT);
    INSERT INTO @SeatTable(seat_id)
    SELECT CAST(value AS INT) FROM STRING_SPLIT(@seat_ids,',');

    DECLARE @total_seats INT = (SELECT COUNT(*) FROM @SeatTable);
    IF @total_seats=0 OR @total_seats>10
    BEGIN RAISERROR(N'❌ Số ghế phải từ 1–10!',16,1); RETURN; END

    DECLARE @screen_id INT = (SELECT screen_id FROM Showtimes WHERE showtime_id=@showtime_id);

    -- Kiểm tra ghế thuộc phòng
    IF EXISTS (SELECT 1 FROM @SeatTable st
               WHERE NOT EXISTS (SELECT 1 FROM Seats s
                                 WHERE s.seat_id=st.seat_id AND s.screen_id=@screen_id))
    BEGIN RAISERROR(N'❌ Có ghế không thuộc phòng chiếu này!',16,1); RETURN; END

    -- Kiểm tra ghế chưa bị đặt
    IF EXISTS (SELECT 1 FROM @SeatTable st
               JOIN Booking_Details bd ON st.seat_id=bd.seat_id
               JOIN Bookings b ON bd.booking_id=b.booking_id
               WHERE b.showtime_id=@showtime_id AND b.booking_status!='Cancelled')
    BEGIN RAISERROR(N'❌ Có ghế đã được đặt! Vui lòng chọn ghế khác.',16,1); RETURN; END

    -- Mở transaction
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Tính tổng tiền (dựa vào base_price của từng ghế)
        DECLARE @total_amount DECIMAL(10,2)=0;
        DECLARE @seat_id INT, @seat_price DECIMAL(10,2);
        DECLARE seat_cursor CURSOR FOR
            SELECT seat_id FROM @SeatTable;
        OPEN seat_cursor;
        FETCH NEXT FROM seat_cursor INTO @seat_id;
        WHILE @@FETCH_STATUS=0 BEGIN
            SET @seat_price = dbo.fn_TinhGiaVe(@seat_id);
            SET @total_amount = @total_amount + @seat_price;
            FETCH NEXT FROM seat_cursor INTO @seat_id;
        END
        CLOSE seat_cursor; DEALLOCATE seat_cursor;

        -- Insert Booking
        INSERT INTO Bookings(customer_id,showtime_id,employee_id,total_seats,total_amount,booking_status)
        VALUES(@customer_id,@showtime_id,@employee_id,@total_seats,@total_amount,'Pending');
        DECLARE @new_booking_id INT = SCOPE_IDENTITY();

        -- Insert Booking_Details
        DECLARE detail_cursor CURSOR FOR
            SELECT seat_id FROM @SeatTable;
        OPEN detail_cursor;
        FETCH NEXT FROM detail_cursor INTO @seat_id;
        WHILE @@FETCH_STATUS=0 BEGIN
            SET @seat_price = dbo.fn_TinhGiaVe(@seat_id);
            INSERT INTO Booking_Details(booking_id,seat_id,seat_price)
            VALUES(@new_booking_id,@seat_id,@seat_price);
            FETCH NEXT FROM detail_cursor INTO @seat_id;
        END
        CLOSE detail_cursor; DEALLOCATE detail_cursor;

        COMMIT TRANSACTION;
        PRINT N'✅ Tạo đơn thành công! Booking ID: ' + CAST(@new_booking_id AS NVARCHAR);
        PRINT N'   Tổng ghế: ' + CAST(@total_seats AS NVARCHAR);
        PRINT N'   Tổng tiền: ' + FORMAT(@total_amount,'N0') + N' VNĐ';

    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT>0 ROLLBACK TRANSACTION;
        DECLARE @Err NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR(@Err,16,1);
    END CATCH
END;
GO

-- 5. Xác nhận đơn đặt vé
DROP PROCEDURE IF EXISTS sp_XacNhanDonDatVe;
GO

CREATE PROCEDURE sp_XacNhanDonDatVe
    @booking_id INT
AS
BEGIN
    SET NOCOUNT ON;
    IF NOT EXISTS (SELECT 1 FROM Bookings WHERE booking_id=@booking_id)
        BEGIN RAISERROR(N'❌ Không tìm thấy đơn đặt vé!',16,1); RETURN; END
    DECLARE @cur NVARCHAR(20);
    SELECT @cur=booking_status FROM Bookings WHERE booking_id=@booking_id;
    IF @cur != 'Pending'
        BEGIN RAISERROR(N'❌ Đơn đã được xác nhận hoặc đã hủy!',16,1); RETURN; END

    BEGIN TRANSACTION;
    BEGIN TRY
        UPDATE Bookings SET booking_status='Confirmed' WHERE booking_id=@booking_id;
        COMMIT TRANSACTION;
        PRINT N'✅ Xác nhận thành công! Booking ID: ' + CAST(@booking_id AS NVARCHAR);
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT>0 ROLLBACK;
        DECLARE @err1 NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR(@err1,16,1);
    END CATCH
END;
GO

-- 6. Hủy đơn đặt vé
DROP PROCEDURE IF EXISTS sp_HuyDonDatVe;
GO

CREATE PROCEDURE sp_HuyDonDatVe
    @booking_id INT,
    @reason     NVARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF NOT EXISTS (SELECT 1 FROM Bookings WHERE booking_id=@booking_id)
        BEGIN RAISERROR(N'❌ Không tìm thấy đơn!',16,1); RETURN; END
    DECLARE @cur NVARCHAR(20);
    SELECT @cur=booking_status FROM Bookings WHERE booking_id=@booking_id;
    IF @cur='Cancelled'
        BEGIN RAISERROR(N'❌ Đơn đã bị hủy trước đó!',16,1); RETURN; END

    BEGIN TRANSACTION;
    BEGIN TRY
        UPDATE Bookings SET booking_status='Cancelled' WHERE booking_id=@booking_id;
        COMMIT TRANSACTION;
        PRINT N'✅ Hủy đơn thành công! Booking ID: ' + CAST(@booking_id AS NVARCHAR);
        IF @reason IS NOT NULL PRINT N'   Lý do: ' + @reason;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT>0 ROLLBACK;
        DECLARE @err2 NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR(@err2,16,1);
    END CATCH
END;
GO

-- 7. Thanh toán
DROP PROCEDURE IF EXISTS sp_ThanhToan;
GO

CREATE PROCEDURE sp_ThanhToan
    @booking_id INT
AS
BEGIN
    DECLARE @ticket DECIMAL(10,2), @food DECIMAL(10,2), @total DECIMAL(10,2);
    SELECT @ticket = total_amount FROM Bookings WHERE booking_id = @booking_id;
    SELECT @food = SUM(quantity * unit_price) FROM Booking_Food WHERE booking_id = @booking_id;
    SET @food = ISNULL(@food, 0);
    SET @total = @ticket + @food;

    INSERT INTO Payments(booking_id, amount, payment_status)
    VALUES(@booking_id, @total, 'Paid');
    PRINT N'✅ Thanh toán xong. Tổng: ' + FORMAT(@total,'N0') + N' VNĐ';
END;
GO

-- 8. Đăng nhập nhân viên
DROP PROCEDURE IF EXISTS sp_DangNhapNhanVien;
GO

CREATE PROCEDURE sp_DangNhapNhanVien
    @employee_id  INT,
    @password     VARCHAR(64)
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM Employees WHERE employee_id = @employee_id)
    BEGIN
        RAISERROR(N'❌ Mã nhân viên không tồn tại!', 16, 1);
        RETURN;
    END

    IF NOT EXISTS (SELECT 1 FROM Employees
                   WHERE employee_id = @employee_id AND is_active = 1)
    BEGIN
        RAISERROR(N'❌ Tài khoản đã bị vô hiệu hóa!', 16, 1);
        RETURN;
    END

    IF NOT EXISTS (SELECT 1 FROM Employees
                   WHERE employee_id = @employee_id AND password_hash = @password)
    BEGIN
        RAISERROR(N'❌ Mật khẩu không đúng!', 16, 1);
        RETURN;
    END

    SELECT employee_id, full_name, position, phone, email
    FROM Employees
    WHERE employee_id = @employee_id;
END;
GO

-- 9. Đổi mật khẩu nhân viên
DROP PROCEDURE IF EXISTS sp_DoiMatKhau;
GO

CREATE PROCEDURE sp_DoiMatKhau
    @employee_id  INT,
    @old_password VARCHAR(64),
    @new_password VARCHAR(64)
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM Employees
                   WHERE employee_id = @employee_id AND password_hash = @old_password)
    BEGIN
        RAISERROR(N'❌ Mật khẩu cũ không đúng!', 16, 1);
        RETURN;
    END

    IF LEN(@new_password) < 4
    BEGIN
        RAISERROR(N'❌ Mật khẩu mới phải có ít nhất 4 ký tự!', 16, 1);
        RETURN;
    END

    UPDATE Employees SET password_hash = @new_password WHERE employee_id = @employee_id;
    PRINT N'✅ Đổi mật khẩu thành công!';
END;
GO

-- 10. Xóa phim
DROP PROCEDURE IF EXISTS sp_XoaPhim;
GO

CREATE PROCEDURE sp_XoaPhim
    @movie_id INT
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM Movies WHERE movie_id = @movie_id)
    BEGIN
        RAISERROR(N'❌ Không tìm thấy phim!', 16, 1);
        RETURN;
    END

    IF EXISTS (
        SELECT 1 FROM Bookings b
        JOIN Showtimes sh ON b.showtime_id = sh.showtime_id
        WHERE sh.movie_id = @movie_id
        AND b.booking_status IN ('Confirmed', 'Pending')
    )
    BEGIN
        RAISERROR(N'❌ Không thể xóa phim đang có vé đặt!', 16, 1);
        RETURN;
    END

    DELETE FROM Movies WHERE movie_id = @movie_id;
    PRINT N'✅ Đã xóa phim!';
END;
GO

-- 11. Sa thải nhân viên
DROP PROCEDURE IF EXISTS sp_SaThaiNhanVien;
GO

CREATE PROCEDURE sp_SaThaiNhanVien
    @employee_id     INT,
    @manager_id      INT
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (
        SELECT 1 FROM Employees
        WHERE employee_id = @manager_id
        AND position = N'Quản lý'
        AND is_active = 1
    )
    BEGIN
        RAISERROR(N'❌ Chỉ Quản lý mới có quyền sa thải nhân viên!', 16, 1);
        RETURN;
    END

    IF NOT EXISTS (SELECT 1 FROM Employees WHERE employee_id = @employee_id)
    BEGIN
        RAISERROR(N'❌ Không tìm thấy nhân viên!', 16, 1);
        RETURN;
    END

    IF @employee_id = @manager_id
    BEGIN
        RAISERROR(N'❌ Không thể tự sa thải chính mình!', 16, 1);
        RETURN;
    END

    UPDATE Employees SET is_active = 0 WHERE employee_id = @employee_id;
    PRINT N'✅ Đã sa thải nhân viên ID: ' + CAST(@employee_id AS NVARCHAR);
END;
GO

-- 12. Doanh thu theo tháng
DROP PROCEDURE IF EXISTS sp_DoanhThuTheoThang;
GO

CREATE PROCEDURE sp_DoanhThuTheoThang
    @year        INT,
    @month       INT = NULL,
    @employee_id INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    WITH FoodTotal AS (
        SELECT 
            booking_id,
            SUM(quantity * unit_price) AS tien_do_an
        FROM Booking_Food
        GROUP BY booking_id
    )
    SELECT
        YEAR(b.booking_date)        AS nam,
        MONTH(b.booking_date)       AS thang,
        e.full_name                 AS nhan_vien,
        COUNT(DISTINCT b.booking_id) AS so_don,
        SUM(b.total_seats)           AS so_ve,
        SUM(b.total_amount)          AS tien_ve,
        ISNULL(SUM(ft.tien_do_an), 0) AS tien_do_an,
        SUM(b.total_amount) + ISNULL(SUM(ft.tien_do_an), 0) AS tong_doanh_thu
    FROM Bookings b
    JOIN Employees e ON b.employee_id = e.employee_id
    LEFT JOIN FoodTotal ft ON b.booking_id = ft.booking_id
    WHERE b.booking_status = 'Confirmed'
    AND YEAR(b.booking_date) = @year
    AND (@month IS NULL OR MONTH(b.booking_date) = @month)
    AND (@employee_id IS NULL OR b.employee_id = @employee_id)
    GROUP BY YEAR(b.booking_date), MONTH(b.booking_date), e.full_name
    ORDER BY nam, thang, nhan_vien;
END;
GO

-- 13. Thống kê vé nhân viên bán được
DROP PROCEDURE IF EXISTS sp_ThongKeVeNhanVien;
GO

CREATE PROCEDURE sp_ThongKeVeNhanVien
    @year  INT,
    @month INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    WITH FoodTotal AS (
        SELECT 
            booking_id,
            SUM(quantity * unit_price) AS tien_do_an
        FROM Booking_Food
        GROUP BY booking_id
    )
    SELECT
        e.employee_id,
        e.full_name        AS nhan_vien,
        e.position         AS chuc_vu,
        COUNT(DISTINCT b.booking_id) AS so_don,
        SUM(b.total_seats)           AS so_ve_ban,
        SUM(b.total_amount)          AS tien_ve,
        ISNULL(SUM(ft.tien_do_an), 0) AS tien_do_an
    FROM Bookings b
    JOIN Employees e ON b.employee_id = e.employee_id
    LEFT JOIN FoodTotal ft ON b.booking_id = ft.booking_id
    WHERE b.booking_status = 'Confirmed'
    AND YEAR(b.booking_date) = @year
    AND (@month IS NULL OR MONTH(b.booking_date) = @month)
    GROUP BY e.employee_id, e.full_name, e.position
    ORDER BY so_ve_ban DESC;
END;
GO

-- 14. Khách đặt vé theo phim
DROP PROCEDURE IF EXISTS sp_KhachDatVeTheoPhim;
GO

CREATE PROCEDURE sp_KhachDatVeTheoPhim
    @year  INT,
    @month INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        m.title                          AS ten_phim,
        m.genre                          AS the_loai,
        c.full_name                      AS khach_hang,
        c.phone                          AS so_dien_thoai,
        b.booking_id                     AS ma_don,
        b.booking_date                   AS thoi_gian_dat,
        b.total_seats                    AS so_ve,
        b.total_amount                   AS tien_ve,
        sh.show_date                     AS ngay_chieu,
        sh.show_time                     AS gio_chieu,
        sc.screen_name                   AS phong_chieu,
        b.booking_status                 AS trang_thai
    FROM Bookings b
    JOIN Customers c  ON b.customer_id  = c.customer_id
    JOIN Showtimes sh ON b.showtime_id  = sh.showtime_id
    JOIN Movies m     ON sh.movie_id    = m.movie_id
    JOIN Screens sc   ON sh.screen_id   = sc.screen_id
    WHERE b.booking_status = 'Confirmed'
    AND   YEAR(b.booking_date) = @year
    AND   (@month IS NULL OR MONTH(b.booking_date) = @month)
    ORDER BY m.title, b.booking_date DESC;
END;
GO

PRINT N'✅ Tất cả Procedures đã tạo xong';
GO

PRINT N'';
PRINT N'╔══════════════════════════════════════════════════════════════╗';
PRINT N'║  ✅ FILE 3 HOÀN THÀNH — Đã xóa discount và bậc thành viên   ║';
PRINT N'║  ✅ Đã xóa giảm giá giờ sáng và tăng giá cuối tuần         ║';
PRINT N'╚══════════════════════════════════════════════════════════════╝';
GO