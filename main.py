import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# KẾT NỐI DATABASE
# ─────────────────────────────────────────────
def get_connection():
    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;DATABASE=CinemaDB;'
        'Trusted_Connection=yes;TrustServerCertificate=yes;'
    )
    return pyodbc.connect(conn_str)

# ─────────────────────────────────────────────
# MÀU SẮC
# ─────────────────────────────────────────────
BG           = "#0D0D1A"
CARD         = "#16162A"
CARD2        = "#1E1E35"
ACCENT       = "#E50914"
ACCENT2      = "#FF6B35"
GREEN        = "#00C853"
GRAY         = "#8888AA"
WHITE        = "#F0F0FF"
BORDER       = "#2A2A45"
SEAT_FREE    = "#1E3A5F"
SEAT_TAKEN   = "#4A1010"
SEAT_SELECTED= "#E50914"
SEAT_VIP     = "#2A1F4A"
SEAT_VIP_SEL = "#9B59B6"
SEAT_COUPLE  = "#1A3A2A"
SEAT_COUPLE_SEL = "#00C853"

IS_MANAGER = lambda pos: pos == "Quản lý"

# ═══════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════
class CinemaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 CinemaDB — Hệ Thống Đặt Vé")
        self.root.geometry("1150x780")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.selected_movie   = None
        self.selected_show    = None
        self.selected_seats   = []
        self.food_order       = []
        self.current_employee = None
        
        self._build_login_screen()
    
    # ═══════════════════════════════════════════════════════
    # LOGIN
    # ═══════════════════════════════════════════════════════
    def _build_login_screen(self):
        for w in self.root.winfo_children(): w.destroy()
        self.root.configure(bg=BG)

        center = tk.Frame(self.root, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="🎬", bg=BG, fg=ACCENT,
                 font=("Arial", 52)).pack(pady=(0, 4))
        tk.Label(center, text="CINEMA BOOKING SYSTEM",
                 bg=BG, fg=WHITE, font=("Georgia", 22, "bold")).pack()
        tk.Label(center, text="Đăng nhập để tiếp tục",
                 bg=BG, fg=GRAY, font=("Arial", 11)).pack(pady=(4, 20))

        card = tk.Frame(center, bg=CARD,
                        highlightbackground=ACCENT, highlightthickness=2)
        card.pack(ipadx=50, ipady=10)

        tk.Label(card, text="ĐĂNG NHẬP NHÂN VIÊN",
                 bg=CARD, fg=ACCENT, font=("Arial", 12, "bold")).pack(pady=(22, 16))

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT employee_id, full_name, position FROM Employees WHERE is_active=1")
            hints = cur.fetchall()
            conn.close()
            hint_text = "  |  ".join(f"ID {e[0]}: {e[1]} ({e[2]})" for e in hints)
            tk.Label(card, text=hint_text, bg=CARD, fg=GRAY,
                     font=("Arial", 8), wraplength=400).pack(pady=(0, 8))
        except:
            pass

        f1 = tk.Frame(card, bg=CARD); f1.pack(pady=6)
        tk.Label(f1, text="Mã Nhân Viên:", bg=CARD, fg=GRAY,
                 font=("Arial", 10), width=14, anchor="w").pack(side="left")
        self._login_id = tk.Entry(f1, font=("Arial", 12), width=18,
                                   bg=CARD2, fg=WHITE, insertbackground=WHITE,
                                   relief="flat", highlightthickness=1,
                                   highlightbackground=BORDER, highlightcolor=ACCENT)
        self._login_id.pack(side="left", ipady=6)
        self._login_id.insert(0, "1")

        f2 = tk.Frame(card, bg=CARD); f2.pack(pady=6)
        tk.Label(f2, text="Mật Khẩu:", bg=CARD, fg=GRAY,
                 font=("Arial", 10), width=14, anchor="w").pack(side="left")
        self._login_pw = tk.Entry(f2, font=("Arial", 12), width=18,
                                   bg=CARD2, fg=WHITE, insertbackground=WHITE,
                                   relief="flat", show="●",
                                   highlightthickness=1,
                                   highlightbackground=BORDER, highlightcolor=ACCENT)
        self._login_pw.pack(side="left", ipady=6)
        self._show_pw = tk.BooleanVar(value=False)
        def toggle_pw():
            self._login_pw.config(show="" if self._show_pw.get() else "●")
        tk.Checkbutton(f2, text="Hiện", variable=self._show_pw,
                       bg=CARD, fg=GRAY, selectcolor=CARD2,
                       activebackground=CARD, font=("Arial", 9),
                       command=toggle_pw).pack(side="left")

        self._login_err = tk.Label(card, text="", bg=CARD, fg=ACCENT, font=("Arial", 9))
        self._login_err.pack()

        def do_login(event=None):
            try:
                eid = int(self._login_id.get())
            except ValueError:
                self._login_err.config(text="⚠ Mã nhân viên phải là số!"); return
            pw = self._login_pw.get()
            if not pw:
                self._login_err.config(text="⚠ Vui lòng nhập mật khẩu!"); return
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("{CALL sp_DangNhapNhanVien (?, ?)}", (eid, pw))
                result = cur.fetchone()
                conn.close()
                if result:
                    self.current_employee = result
                    self._build_ui()
                else:
                    self._login_err.config(text="⚠ Đăng nhập thất bại!")
            except Exception as e:
                msg = str(e)
                if "không tồn tại" in msg:
                    self._login_err.config(text="⚠ Mã nhân viên không tồn tại!")
                elif "Mật khẩu" in msg:
                    self._login_err.config(text="⚠ Mật khẩu không đúng!")
                elif "vô hiệu" in msg:
                    self._login_err.config(text="⚠ Tài khoản đã bị vô hiệu hóa!")
                else:
                    self._login_err.config(text=f"⚠ {msg[:60]}")

        tk.Button(card, text="  ĐĂNG NHẬP  →",
                  bg=ACCENT, fg=WHITE, font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2", padx=24, pady=10,
                  command=do_login).pack(pady=(10, 24))

        self._login_pw.bind("<Return>", do_login)
        self._login_id.bind("<Return>", lambda e: self._login_pw.focus())
        self._login_id.focus()

        tk.Button(center, text="🔑 Đổi mật khẩu",
                  bg=BG, fg=GRAY, font=("Arial", 9),
                  relief="flat", cursor="hand2",
                  command=self._change_password_dialog).pack(pady=(8, 0))

    def _change_password_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Đổi Mật Khẩu")
        dlg.geometry("360x320")
        dlg.configure(bg=CARD)
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text="🔑  ĐỔI MẬT KHẨU", bg=CARD, fg=GREEN,
                 font=("Arial", 13, "bold")).pack(pady=(20, 16))

        fields = [("Mã Nhân Viên:", "eid"),
                  ("Mật Khẩu Cũ:", "old"),
                  ("Mật Khẩu Mới:", "new"),
                  ("Xác Nhận Mới:", "confirm")]
        entries = {}
        for label, key in fields:
            f = tk.Frame(dlg, bg=CARD); f.pack(pady=5)
            tk.Label(f, text=label, bg=CARD, fg=WHITE,
                     font=("Arial", 10), width=16, anchor="w").pack(side="left")
            e = tk.Entry(f, font=("Arial", 11), width=16,
                         bg=CARD2, fg=WHITE, insertbackground=WHITE,
                         relief="flat", show="" if key == "eid" else "●")
            e.pack(side="left", ipady=5)
            entries[key] = e

        err_lbl = tk.Label(dlg, text="", bg=CARD, fg=ACCENT, font=("Arial", 9))
        err_lbl.pack()

        def do_change():
            try: eid = int(entries["eid"].get())
            except: err_lbl.config(text="⚠ Mã NV phải là số!"); return
            old_pw = entries["old"].get()
            new_pw = entries["new"].get()
            confirm = entries["confirm"].get()
            if new_pw != confirm:
                err_lbl.config(text="⚠ Mật khẩu mới không khớp!"); return
            if len(new_pw) < 4:
                err_lbl.config(text="⚠ Mật khẩu mới phải ≥ 4 ký tự!"); return
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("{CALL sp_DoiMatKhau (?, ?, ?)}", (eid, old_pw, new_pw))
                conn.commit(); conn.close()
                messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!")
                dlg.destroy()
            except Exception as e:
                err_lbl.config(text=f"⚠ {str(e)[:60]}")

        tk.Button(dlg, text="Xác Nhận Đổi", bg=GREEN, fg="black",
                  font=("Arial", 11, "bold"), relief="flat",
                  padx=16, pady=8, command=do_change).pack(pady=(6, 0))

    # ═══════════════════════════════════════════════════════
    # MAIN UI
    # ═══════════════════════════════════════════════════════
    def _build_ui(self):
        for w in self.root.winfo_children(): w.destroy()
        emp = self.current_employee
        is_mgr = IS_MANAGER(emp[2])

        # Header
        hdr = tk.Frame(self.root, bg=ACCENT, height=56)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="🎬  CINEMA BOOKING SYSTEM",
                 bg=ACCENT, fg=WHITE, font=("Georgia", 18, "bold")).pack(side="left", padx=20)
        tk.Label(hdr, text=f"👤 {emp[1]}  |  {emp[2]}",
                 bg=ACCENT, fg=WHITE, font=("Arial", 10)).pack(side="right", padx=10)
        tk.Button(hdr, text="Đổi NV", bg="#C0080F", fg=WHITE,
                  font=("Arial", 9), relief="flat",
                  command=self._build_login_screen).pack(side="right", padx=(0, 6), pady=10)

        # Step bar
        self.step_frame = tk.Frame(self.root, bg=CARD, height=44)
        self.step_frame.pack(fill="x"); self.step_frame.pack_propagate(False)
        self.step_labels = []
        steps = ["① Chọn Phim", "② Suất Chiếu", "③ Chọn Ghế", "④ Bắp & Nước", "⑤ Xác Nhận"]
        for s in steps:
            lbl = tk.Label(self.step_frame, text=s, bg=CARD, fg=GRAY,
                           font=("Arial", 10, "bold"), padx=18, pady=10)
            lbl.pack(side="left")
            self.step_labels.append(lbl)

        if is_mgr:
            mgr_frame = tk.Frame(self.step_frame, bg=CARD)
            mgr_frame.pack(side="right", padx=10, pady=6)
            tk.Button(mgr_frame, text="📊 Quản Lý & Thống Kê",
                      bg=CARD2, fg=GREEN, font=("Arial", 10, "bold"),
                      relief="flat", padx=14,
                      command=self._show_management).pack(side="left", padx=2)
            tk.Button(mgr_frame, text="➕ Thêm Suất Chiếu",
                      bg=CARD2, fg=ACCENT2, font=("Arial", 10, "bold"),
                      relief="flat", padx=14,
                      command=self._add_showtime_dialog).pack(side="left", padx=2)

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill="both", expand=True)
        self.bottom = tk.Frame(self.root, bg=CARD2, height=54)
        self.bottom.pack(fill="x", side="bottom"); self.bottom.pack_propagate(False)

        self._show_step(0)

    def _highlight_step(self, idx):
        for i, lbl in enumerate(self.step_labels):
            if i == idx:   lbl.config(fg=ACCENT, bg=CARD2)
            elif i < idx:  lbl.config(fg=GREEN,  bg=CARD)
            else:          lbl.config(fg=GRAY,   bg=CARD)

    def _clear_content(self):
        for w in self.content.winfo_children(): w.destroy()
        for w in self.bottom.winfo_children(): w.destroy()

    def _show_step(self, idx):
        self._highlight_step(idx)
        self._clear_content()
        [self._page_movies, self._page_showtimes,
         self._page_seats, self._page_food, self._page_confirm][idx]()

    # ═══════════════════════════════════════════════════════
    # BƯỚC 1 — CHỌN PHIM
    # ═══════════════════════════════════════════════════════
    def _page_movies(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        header = tk.Frame(self.content, bg=BG)
        header.pack(fill="x", padx=30, pady=(18, 8))
        tk.Label(header, text="Chọn Phim", bg=BG, fg=WHITE,
                 font=("Georgia", 15, "bold")).pack(side="left")

        if IS_MANAGER(self.current_employee[2]):
            tk.Button(header, text="＋ Thêm Phim Mới",
                      bg=GREEN, fg="black", font=("Arial", 10, "bold"),
                      relief="flat", cursor="hand2",
                      command=self._add_movie_dialog).pack(side="right")

        frame = tk.Frame(self.content, bg=BG)
        frame.pack(fill="both", expand=True, padx=30)

        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT movie_id, title, genre, duration, rating, director
                FROM Movies ORDER BY movie_id DESC
            """)
            self.movies = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e)); return

        cols = 3
        for idx, m in enumerate(self.movies):
            r, c = divmod(idx, cols)
            card = tk.Frame(frame, bg=CARD, cursor="hand2",
                            highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=r, column=c, padx=12, pady=12, sticky="nsew", ipadx=14, ipady=12)
            frame.grid_columnconfigure(c, weight=1)

            tk.Label(card, text=m[1], bg=CARD, fg=WHITE,
                     font=("Arial", 13, "bold"), wraplength=220, justify="left").pack(anchor="w", pady=(6, 2))
            tk.Label(card, text=f"🎭 {m[2]}  •  ⏱ {m[3]} phút", bg=CARD, fg=GRAY,
                     font=("Arial", 9)).pack(anchor="w")
            tk.Label(card, text=f"🎬 {m[5] if m[5] else 'Chưa cập nhật'}", bg=CARD, fg=GRAY,
                     font=("Arial", 9)).pack(anchor="w")
            star = "★" * int(m[4]) + "☆" * (10 - int(m[4])) if m[4] else ""
            tk.Label(card, text=f"⭐ {m[4]}  {star[:5]}", bg=CARD, fg=GREEN,
                     font=("Arial", 10)).pack(anchor="w", pady=(4, 0))

            btn_row = tk.Frame(card, bg=CARD); btn_row.pack(anchor="e", pady=(10, 0))
            tk.Button(btn_row, text="Chọn →",
                      bg=ACCENT, fg=WHITE, font=("Arial", 10, "bold"),
                      relief="flat", cursor="hand2",
                      command=lambda mv=m: self._select_movie(mv)).pack(side="left")

            if IS_MANAGER(self.current_employee[2]):
                tk.Button(btn_row, text="🗑",
                          bg=CARD2, fg=GRAY, font=("Arial", 10),
                          relief="flat", cursor="hand2",
                          command=lambda mv=m: self._delete_movie(mv)).pack(side="left", padx=(6, 0))

    def _select_movie(self, movie):
        self.selected_movie = movie
        self.selected_show = None
        self.selected_seats = []
        self._show_step(1)

    def _add_movie_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Thêm Phim Mới")
        dlg.geometry("450x520")
        dlg.configure(bg=CARD)
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text="＋  THÊM PHIM MỚI", bg=CARD, fg=GREEN,
                 font=("Arial", 13, "bold")).pack(pady=(20, 14))

        fields = [
            ("Tên phim:*", "title", ""),
            ("Thể loại:*", "genre", "Action"),
            ("Thời lượng (phút):*", "duration", "120"),
            ("Điểm (0-10):", "rating", "8.0"),
            ("Đạo diễn:*", "director", ""),
            ("Ngày ra mắt (YYYY-MM-DD):", "release", datetime.now().strftime("%Y-%m-%d")),
        ]
        entries = {}
        for label, key, default in fields:
            f = tk.Frame(dlg, bg=CARD); f.pack(pady=6)
            tk.Label(f, text=label, bg=CARD, fg=WHITE,
                     font=("Arial", 10), width=20, anchor="w").pack(side="left")
            e = tk.Entry(f, font=("Arial", 11), width=22,
                         bg=CARD2, fg=WHITE, insertbackground=WHITE, relief="flat")
            e.insert(0, default)
            e.pack(side="left", ipady=5)
            entries[key] = e

        err_lbl = tk.Label(dlg, text="", bg=CARD, fg=ACCENT, font=("Arial", 9))
        err_lbl.pack(pady=5)

        def do_add():
            # Validate required fields
            title = entries["title"].get().strip()
            genre = entries["genre"].get().strip()
            director = entries["director"].get().strip()
            
            if not title:
                err_lbl.config(text="⚠ Tên phim không được để trống!")
                return
            if not genre:
                err_lbl.config(text="⚠ Thể loại không được để trống!")
                return
            if not director:
                err_lbl.config(text="⚠ Đạo diễn không được để trống!")
                return
            
            try:
                duration = int(entries["duration"].get())
                if duration <= 0 or duration > 600:
                    err_lbl.config(text="⚠ Thời lượng phải từ 1-600 phút!")
                    return
            except:
                err_lbl.config(text="⚠ Thời lượng phải là số!")
                return
            
            rating = entries["rating"].get()
            rating_val = None
            if rating:
                try:
                    rating_val = float(rating)
                    if rating_val < 0 or rating_val > 10:
                        err_lbl.config(text="⚠ Điểm phải từ 0-10!")
                        return
                except:
                    err_lbl.config(text="⚠ Điểm phải là số!")
                    return
            
            release = entries["release"].get()
            if release and release.strip():
                try:
                    datetime.strptime(release, "%Y-%m-%d")
                except:
                    err_lbl.config(text="⚠ Ngày ra mắt phải đúng định dạng YYYY-MM-DD!")
                    return
            else:
                release = None
            
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("{CALL sp_ThemPhimMoi (?, ?, ?, ?, ?, ?)}",
                            (title, genre, duration, rating_val, director, release))
                conn.commit(); conn.close()
                messagebox.showinfo("Thành công", f"Đã thêm phim: {title}")
                dlg.destroy()
                self._page_movies()
            except Exception as e:
                err_lbl.config(text=f"⚠ {str(e)[:80]}")

        tk.Button(dlg, text="✅ Thêm Phim", bg=GREEN, fg="black",
                  font=("Arial", 11, "bold"), relief="flat",
                  padx=16, pady=8, command=do_add).pack(pady=(8, 0))
        
        tk.Label(dlg, text="* Bắt buộc", bg=CARD, fg=GRAY, font=("Arial", 8)).pack(pady=(10, 5))

    def _delete_movie(self, movie):
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn muốn xóa phim '{movie[1]}'?\n\n"
            "• Nếu phim có vé đặt → sẽ không cho xóa"
        )
        if not confirm: return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("{CALL sp_XoaPhim (?)}", (movie[0],))
            conn.commit(); conn.close()
            messagebox.showinfo("Thành công", f"Đã xóa phim '{movie[1]}'!")
            self._page_movies()
        except Exception as e:
            msg = str(e)
            if "vé đặt" in msg:
                messagebox.showerror("Không thể xóa", "❌ Phim này đang có vé đặt!\nKhông được phép xóa.")
            else:
                messagebox.showerror("Lỗi", msg)

    # ═══════════════════════════════════════════════════════
    # THÊM SUẤT CHIẾU
    # ═══════════════════════════════════════════════════════
    def _add_showtime_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Thêm Suất Chiếu Mới")
        dlg.geometry("450x480")
        dlg.configure(bg=CARD)
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text="➕  THÊM SUẤT CHIẾU", bg=CARD, fg=ACCENT2,
                 font=("Arial", 13, "bold")).pack(pady=(20, 14))

        # Load movies
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT movie_id, title FROM Movies ORDER BY title")
            movies = cur.fetchall()
            conn.close()
        except:
            movies = []
        
        # Load screens
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT screen_id, screen_name FROM Screens")
            screens = cur.fetchall()
            conn.close()
        except:
            screens = []
        
        # Movie selection
        f1 = tk.Frame(dlg, bg=CARD); f1.pack(pady=8)
        tk.Label(f1, text="Phim:*", bg=CARD, fg=WHITE,
                 font=("Arial", 10), width=15, anchor="w").pack(side="left")
        movie_var = tk.StringVar()
        movie_combo = ttk.Combobox(f1, textvariable=movie_var, width=25, state="readonly")
        movie_combo['values'] = [f"{m[0]} - {m[1]}" for m in movies]
        movie_combo.pack(side="left", ipady=3)
        
        # Screen selection
        f2 = tk.Frame(dlg, bg=CARD); f2.pack(pady=8)
        tk.Label(f2, text="Phòng chiếu:*", bg=CARD, fg=WHITE,
                 font=("Arial", 10), width=15, anchor="w").pack(side="left")
        screen_var = tk.StringVar()
        screen_combo = ttk.Combobox(f2, textvariable=screen_var, width=25, state="readonly")
        screen_combo['values'] = [f"{s[0]} - {s[1]}" for s in screens]
        screen_combo.pack(side="left", ipady=3)
        
        # Date
        f3 = tk.Frame(dlg, bg=CARD); f3.pack(pady=8)
        tk.Label(f3, text="Ngày chiếu:*", bg=CARD, fg=WHITE,
                 font=("Arial", 10), width=15, anchor="w").pack(side="left")
        date_entry = tk.Entry(f3, font=("Arial", 11), width=25,
                              bg=CARD2, fg=WHITE, insertbackground=WHITE, relief="flat")
        date_entry.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        date_entry.pack(side="left", ipady=5)
        
        # Time
        f4 = tk.Frame(dlg, bg=CARD); f4.pack(pady=8)
        tk.Label(f4, text="Giờ chiếu:*", bg=CARD, fg=WHITE,
                 font=("Arial", 10), width=15, anchor="w").pack(side="left")
        time_combo = ttk.Combobox(f4, width=25, state="readonly")
        time_combo['values'] = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", 
                                "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"]
        time_combo.set("19:00")
        time_combo.pack(side="left", ipady=3)
        
        # Price
        f5 = tk.Frame(dlg, bg=CARD); f5.pack(pady=8)
        tk.Label(f5, text="Giá vé (VNĐ):*", bg=CARD, fg=WHITE,
                 font=("Arial", 10), width=15, anchor="w").pack(side="left")
        price_entry = tk.Entry(f5, font=("Arial", 11), width=25,
                               bg=CARD2, fg=WHITE, insertbackground=WHITE, relief="flat")
        price_entry.insert(0, "100000")
        price_entry.pack(side="left", ipady=5)
        
        err_lbl = tk.Label(dlg, text="", bg=CARD, fg=ACCENT, font=("Arial", 9))
        err_lbl.pack(pady=5)
        
        def do_add():
            # Validate
            if not movie_var.get():
                err_lbl.config(text="⚠ Vui lòng chọn phim!")
                return
            if not screen_var.get():
                err_lbl.config(text="⚠ Vui lòng chọn phòng chiếu!")
                return
            
            try:
                movie_id = int(movie_var.get().split(" - ")[0])
                screen_id = int(screen_var.get().split(" - ")[0])
                show_date = date_entry.get().strip()
                show_time = time_combo.get()
                base_price = int(price_entry.get())
                
                if not show_date:
                    err_lbl.config(text="⚠ Vui lòng nhập ngày chiếu!")
                    return
                
                # Validate date
                try:
                    datetime.strptime(show_date, "%Y-%m-%d")
                except:
                    err_lbl.config(text="⚠ Ngày chiếu phải đúng định dạng YYYY-MM-DD!")
                    return
                
                if base_price <= 0 or base_price > 1000000:
                    err_lbl.config(text="⚠ Giá vé phải từ 1-1,000,000 VNĐ!")
                    return
                
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("{CALL sp_ThemSuatChieu (?, ?, ?, ?, ?)}",
                            (movie_id, screen_id, show_date, show_time, base_price))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Thành công", f"Đã thêm suất chiếu:\n"
                                    f"Phim: {movie_var.get()}\n"
                                    f"Ngày: {show_date} {show_time}\n"
                                    f"Giá: {base_price:,} VNĐ")
                dlg.destroy()
                
            except Exception as e:
                err_lbl.config(text=f"⚠ {str(e)[:80]}")
        
        tk.Button(dlg, text="✅ Thêm Suất Chiếu", bg=ACCENT2, fg="white",
                  font=("Arial", 11, "bold"), relief="flat",
                  padx=16, pady=8, command=do_add).pack(pady=(15, 8))
        
        tk.Label(dlg, text="* Bắt buộc", bg=CARD, fg=GRAY, font=("Arial", 8)).pack()

    # ═══════════════════════════════════════════════════════
    # BƯỚC 2 — SUẤT CHIẾU
    # ═══════════════════════════════════════════════════════
    def _page_showtimes(self):
        tk.Label(self.content,
                 text=f"Suất Chiếu — {self.selected_movie[1]}",
                 bg=BG, fg=WHITE, font=("Georgia", 15, "bold")
                 ).pack(anchor="w", padx=30, pady=(18, 10))
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT s.showtime_id, s.show_date, s.show_time,
                       sc.screen_name, s.base_price,
                       dbo.fn_DemGheDaDat(s.showtime_id) AS booked,
                       sc.total_seats
                FROM Showtimes s
                JOIN Screens sc ON s.screen_id = sc.screen_id
                WHERE s.movie_id = ?
                ORDER BY s.show_date, s.show_time
            """, (self.selected_movie[0],))
            shows = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e)); return

        if not shows:
            tk.Label(self.content, text="Không có suất chiếu nào.",
                     bg=BG, fg=GRAY, font=("Arial", 12)).pack(pady=30)
        else:
            dates = {}
            for s in shows:
                dates.setdefault(str(s[1]), []).append(s)

            canvas = tk.Canvas(self.content, bg=BG, highlightthickness=0)
            scroll = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
            inner = tk.Frame(canvas, bg=BG)
            inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=inner, anchor="nw")
            canvas.configure(yscrollcommand=scroll.set)
            canvas.pack(side="left", fill="both", expand=True, padx=30)
            scroll.pack(side="right", fill="y")

            for date_str, day_shows in dates.items():
                tk.Label(inner, text=f"📅  {date_str}", bg=BG, fg=GREEN,
                         font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 4))
                row_f = tk.Frame(inner, bg=BG); row_f.pack(fill="x")
                for sh in day_shows:
                    avail = sh[6] - sh[5]
                    color = GREEN if avail > 10 else (ACCENT2 if avail > 0 else GRAY)
                    card = tk.Frame(row_f, bg=CARD,
                                    highlightbackground=BORDER, highlightthickness=1,
                                    cursor="hand2")
                    card.pack(side="left", padx=8, pady=4, ipadx=14, ipady=10)
                    tk.Label(card, text=str(sh[2])[:5], bg=CARD, fg=WHITE,
                             font=("Arial", 18, "bold")).pack()
                    tk.Label(card, text=sh[3], bg=CARD, fg=GRAY, font=("Arial", 9)).pack()
                    tk.Label(card, text=f"{avail} ghế trống", bg=CARD, fg=color, font=("Arial", 9)).pack()
                    tk.Label(card, text=f"{int(sh[4]):,} VNĐ", bg=CARD, fg=GREEN, font=("Arial", 10, "bold")).pack()
                    if avail > 0:
                        tk.Button(card, text="Chọn", bg=ACCENT, fg=WHITE,
                                  font=("Arial", 9, "bold"), relief="flat",
                                  command=lambda s=sh: self._select_show(s)).pack(pady=(6, 0))
                    else:
                        tk.Label(card, text="Hết chỗ", bg=CARD, fg=GRAY, font=("Arial", 9)).pack()

        tk.Button(self.bottom, text="← Quay lại", bg=CARD2, fg=GRAY,
                  font=("Arial", 10), relief="flat",
                  command=lambda: self._show_step(0)).pack(side="left", padx=20, pady=10)

    def _select_show(self, show):
        self.selected_show = show
        self.selected_seats = []
        self._show_step(2)

    # ═══════════════════════════════════════════════════════
    # BƯỚC 3 — CHỌN GHẾ
    # ═══════════════════════════════════════════════════════
    def _page_seats(self):
        sh = self.selected_show
        tk.Label(self.content,
                 text=f"Sơ Đồ Ghế  —  {sh[3]}  |  {str(sh[2])[:5]}  |  {str(sh[1])}",
                 bg=BG, fg=WHITE, font=("Georgia", 13, "bold")
                 ).pack(anchor="w", padx=30, pady=(14, 4))

        leg = tk.Frame(self.content, bg=BG); leg.pack(anchor="w", padx=30, pady=(0, 8))
        for color, label in [(SEAT_FREE, "Standard"), (SEAT_VIP, "VIP"),
                              (SEAT_COUPLE, "Couple"), (SEAT_TAKEN, "Đã đặt"), (SEAT_SELECTED, "Đang chọn")]:
            tk.Frame(leg, bg=color, width=16, height=16).pack(side="left", padx=(0, 4))
            tk.Label(leg, text=label, bg=BG, fg=GRAY, font=("Arial", 8)).pack(side="left", padx=(0, 14))

        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT s.seat_id, s.seat_number, s.row_label, s.seat_type, s.base_price
                FROM Seats s JOIN Screens sc ON s.screen_id=sc.screen_id
                JOIN Showtimes sh ON sh.screen_id=sc.screen_id
                WHERE sh.showtime_id=? 
                ORDER BY s.row_label, CAST(SUBSTRING(s.seat_number, 2, LEN(s.seat_number)-1) AS INT)
            """, (sh[0],))
            all_seats = cur.fetchall()
            cur.execute("""
                SELECT bd.seat_id FROM Booking_Details bd
                JOIN Bookings b ON bd.booking_id=b.booking_id
                WHERE b.showtime_id=? AND b.booking_status!='Cancelled'
            """, (sh[0],))
            taken_ids = {r[0] for r in cur.fetchall()}
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e)); return

        rows = {}
        for s in all_seats:
            rows.setdefault(s[2], []).append(s)
        for row_label in rows:
            rows[row_label].sort(key=lambda x: int(x[1].replace(row_label, "")))

        outer = tk.Frame(self.content, bg=BG); outer.pack(fill="both", expand=True, padx=30)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vscroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        hscroll = ttk.Scrollbar(outer, orient="horizontal", command=canvas.xview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        vscroll.pack(side="right", fill="y")
        hscroll.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        tk.Label(inner, text="═══════════  MÀN HÌNH  ═══════════",
                 bg=CARD2, fg=ACCENT2, font=("Arial", 10, "bold"),
                 padx=20, pady=6).pack(pady=(0, 12))

        self._seat_btns = {}
        for row_label in sorted(rows.keys()):
            row_frame = tk.Frame(inner, bg=BG); row_frame.pack(pady=2)
            tk.Label(row_frame, text=row_label, bg=BG, fg=GRAY,
                     font=("Arial", 9, "bold"), width=2).pack(side="left", padx=(0, 8))
            for seat in rows[row_label]:
                seat_id, seat_num, _, seat_type, base_price = seat
                is_taken = seat_id in taken_ids
                if is_taken:     bg_c = SEAT_TAKEN; state = "disabled"
                elif seat_type == "VIP":    bg_c = SEAT_VIP;    state = "normal"
                elif seat_type == "Couple": bg_c = SEAT_COUPLE; state = "normal"
                else:            bg_c = SEAT_FREE;   state = "normal"
                label_text = seat_num.replace(row_label, "")
                btn = tk.Button(row_frame,
                                text=label_text if not is_taken else "✕",
                                width=3, height=1,
                                bg=bg_c, fg=WHITE if not is_taken else "#663333",
                                font=("Arial", 7, "bold"),
                                relief="flat", bd=0, state=state,
                                cursor="hand2" if not is_taken else "arrow",
                                command=lambda s=seat: self._toggle_seat(s))
                btn.pack(side="left", padx=1)
                self._seat_btns[seat_id] = (btn, seat, bg_c)

        self.seat_info_lbl = tk.Label(self.bottom,
                                       text="Chưa chọn ghế nào", bg=CARD2, fg=GRAY, font=("Arial", 10))
        self.seat_info_lbl.pack(side="left", padx=20)
        tk.Button(self.bottom, text="← Quay lại", bg=CARD2, fg=GRAY,
                  font=("Arial", 10), relief="flat",
                  command=lambda: self._show_step(1)).pack(side="left", padx=10, pady=10)
        self.btn_next_seats = tk.Button(self.bottom, text="Tiếp: Bắp & Nước →",
                                         bg=GRAY, fg=WHITE, font=("Arial", 10, "bold"),
                                         relief="flat", state="disabled",
                                         command=lambda: self._show_step(3))
        self.btn_next_seats.pack(side="right", padx=20, pady=10)

    def _toggle_seat(self, seat):
        seat_id = seat[0]
        btn, seat_data, orig_bg = self._seat_btns[seat_id]
        already = [s for s in self.selected_seats if s[0] == seat_id]
        
        if already:
            self.selected_seats.remove(already[0])
            btn.config(bg=orig_bg)
        else:
            if len(self.selected_seats) >= 10:
                messagebox.showwarning("Giới hạn", "Chỉ đặt tối đa 10 ghế!")
                return
            # Chỉ lấy 5 phần tử đầu tiên của seat (vì seat có 5 phần tử)
            new_seat = (seat[0], seat[1], seat[2], seat[3], seat[4])
            self.selected_seats.append(new_seat)
            sel_color = SEAT_VIP_SEL if seat[3] == "VIP" else SEAT_COUPLE_SEL if seat[3] == "Couple" else SEAT_SELECTED
            btn.config(bg=sel_color)
        
        if self.selected_seats:
            total = sum(s[4] for s in self.selected_seats)
            names = ", ".join(s[1] for s in self.selected_seats)
            self.seat_info_lbl.config(text=f"Ghế: {names}  |  Tạm tính: {int(total):,} VNĐ", fg=WHITE)
            self.btn_next_seats.config(bg=ACCENT, state="normal")
        else:
            self.seat_info_lbl.config(text="Chưa chọn ghế nào", fg=GRAY)
            self.btn_next_seats.config(bg=GRAY, state="disabled")

    # ═══════════════════════════════════════════════════════
    # BƯỚC 4 — BẮP & NƯỚC
    # ═══════════════════════════════════════════════════════
    def _page_food(self):
        tk.Label(self.content, text="Bắp Rang & Nước Uống",
            bg=BG, fg=WHITE, font=("Georgia", 15, "bold")).pack(anchor="w", padx=30, pady=(18, 4))
        tk.Label(self.content, text="(Bước này không bắt buộc — có thể bỏ qua)",
            bg=BG, fg=GRAY, font=("Arial", 9)).pack(anchor="w", padx=30, pady=(0, 12))

        main = tk.Frame(self.content, bg=BG); main.pack(fill="both", expand=True, padx=30)
        for i in range(3): main.grid_columnconfigure(i, weight=1)

        # BẮP RANG
        self._popcorn_var  = tk.StringVar(value="none")
        self._popcorn_size = tk.StringVar(value="M")
        self._popcorn_qty  = tk.IntVar(value=1)

        pf = tk.LabelFrame(main, text="🍿  BẮP RANG", bg=CARD, fg=GREEN,
                        font=("Arial", 11, "bold"), padx=14, pady=14)
        pf.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        for val, label, price in [("none",     "Không mua",    "—"),
                                ("caramel", "🍯 Caramel", "45,000"),
                                ("cheese",  "🧀 Cheese",  "45,000"),
                                ("mix",     "🎨 Mix",     "50,000")]:
            f = tk.Frame(pf, bg=CARD); f.pack(anchor="w", pady=3)
            tk.Radiobutton(f, variable=self._popcorn_var, value=val,
                        bg=CARD, fg=WHITE, selectcolor=ACCENT, activebackground=CARD,
                        font=("Arial", 10)).pack(side="left")
            tk.Label(f, text=label, bg=CARD, fg=WHITE, font=("Arial", 10)).pack(side="left")
            if price != "—":
                tk.Label(f, text=f"  {price} VNĐ", bg=CARD, fg=GREEN, font=("Arial", 9)).pack(side="left")

        tk.Label(pf, text="Cỡ:", bg=CARD, fg=GRAY, font=("Arial", 9)).pack(anchor="w", pady=(10, 2))
        sf = tk.Frame(pf, bg=CARD); sf.pack(anchor="w")
        for s in ["S", "M", "L"]:
            tk.Radiobutton(sf, text=s, variable=self._popcorn_size, value=s,
                        bg=CARD, fg=WHITE, selectcolor=ACCENT2, activebackground=CARD,
                            font=("Arial", 10, "bold")).pack(side="left", padx=6)

        qf_pop = tk.Frame(pf, bg=CARD); qf_pop.pack(anchor="w", pady=(10, 0))
        tk.Label(qf_pop, text="Số lượng:", bg=CARD, fg=GRAY, font=("Arial", 9)).pack(side="left")
        tk.Spinbox(qf_pop, from_=1, to=10, textvariable=self._popcorn_qty,
                width=4, font=("Arial", 10), bg=CARD2, fg=WHITE,
                buttonbackground=CARD2).pack(side="left", padx=6)

        # NƯỚC UỐNG
        self._drink_vars = {}
        self._drink_qtys = {}

        df = tk.LabelFrame(main, text="🥤  NƯỚC UỐNG", bg=CARD, fg="#00BFFF",
                            font=("Arial", 11, "bold"), padx=14, pady=14)
        df.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        for val, label in [("pepsi",  "🟦 Pepsi"),
                            ("coca",   "🟥 Coca-Cola"),
                            ("fanta",  "🟠 Fanta Cam"),
                            ("7up",    "🟩 7UP")]:
            f = tk.Frame(df, bg=CARD); f.pack(anchor="w", pady=3)
            var = tk.IntVar(value=0); self._drink_vars[val] = var
            tk.Checkbutton(f, variable=var, bg=CARD, fg=WHITE, selectcolor=ACCENT,
                            activebackground=CARD).pack(side="left")
            tk.Label(f, text=label, bg=CARD, fg=WHITE, font=("Arial", 10)).pack(side="left")
            tk.Label(f, text="  30,000 VNĐ", bg=CARD, fg=GREEN, font=("Arial", 9)).pack(side="left")

            qf_d = tk.Frame(df, bg=CARD); qf_d.pack(anchor="w", padx=24, pady=(0, 4))
            tk.Label(qf_d, text="SL:", bg=CARD, fg=GRAY, font=("Arial", 8)).pack(side="left")
            qty_var = tk.IntVar(value=1); self._drink_qtys[val] = qty_var
            tk.Spinbox(qf_d, from_=1, to=10, textvariable=qty_var,
                    width=4, font=("Arial", 9), bg=CARD2, fg=WHITE,
                    buttonbackground=CARD2).pack(side="left", padx=4)

        # COMBO
        self._combo_var = tk.IntVar(value=0)
        cf = tk.LabelFrame(main, text="🎁  COMBO", bg=CARD, fg=GREEN,
                            font=("Arial", 11, "bold"), padx=14, pady=14)
        cf.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        tk.Label(cf, text="Combo 1:\n1 Bắp + 1 Nước", bg=CARD, fg=WHITE,
                font=("Arial", 10), justify="left").pack(anchor="w")
        tk.Label(cf, text="80,000 VNĐ", bg=CARD, fg=GREEN, font=("Arial", 14, "bold")).pack(anchor="w", pady=4)
        f = tk.Frame(cf, bg=CARD); f.pack(anchor="w", pady=6)
        tk.Checkbutton(f, variable=self._combo_var, bg=CARD, fg=WHITE,
                    selectcolor=GREEN, activebackground=CARD).pack(side="left")
        tk.Label(f, text="Thêm Combo 1", bg=CARD, fg=WHITE, font=("Arial", 10, "bold")).pack(side="left")
        qf = tk.Frame(cf, bg=CARD); qf.pack(anchor="w")
        tk.Label(qf, text="Số lượng:", bg=CARD, fg=GRAY, font=("Arial", 9)).pack(side="left")
        self._combo_qty = tk.Spinbox(qf, from_=1, to=10, width=4, font=("Arial", 10),
                                    bg=CARD2, fg=WHITE, buttonbackground=CARD2)
        self._combo_qty.pack(side="left", padx=6)

        # BOTTOM BAR
        tk.Button(self.bottom, text="← Quay lại", bg=CARD2, fg=GRAY,
                font=("Arial", 10), relief="flat",
                command=lambda: self._show_step(2)).pack(side="left", padx=20, pady=10)
        tk.Button(self.bottom, text="Bỏ qua →", bg=CARD2, fg=GRAY,
                font=("Arial", 10), relief="flat",
                command=lambda: self._show_step(4)).pack(side="left", padx=6, pady=10)
        tk.Button(self.bottom, text="Tiếp: Xem Vé →",
                bg=ACCENT, fg=WHITE, font=("Arial", 10, "bold"),
                relief="flat", command=self._collect_food_and_next).pack(side="right", padx=20, pady=10)

    def _collect_food_and_next(self):
        self.food_order = []
    
        # Giá mapping tạm (khớp với DB)
        popcorn_prices = {
            ("caramel", "S"): 35000,
            ("caramel", "M"): 45000,
            ("caramel", "L"): 55000,
            ("cheese", "S"): 35000,
            ("cheese", "M"): 45000,
            ("cheese", "L"): 55000,
            ("mix", "S"): 40000,
            ("mix", "M"): 50000,
            ("mix", "L"): 60000,
        }
        drink_prices = {
            "pepsi": 30000,
            "coca": 30000,
            "fanta": 30000,
            "7up": 30000,
        }

        # Bắp rang
        pc = self._popcorn_var.get()
        if pc != "none":
            size = self._popcorn_size.get()
            qty = int(self._popcorn_qty.get())
            food_names = {
                ("caramel", "S"): "Bắp rang Caramel (S)",
                ("caramel", "M"): "Bắp rang Caramel (M)",
                ("caramel", "L"): "Bắp rang Caramel (L)",
                ("cheese", "S"): "Bắp rang Cheese (S)",
                ("cheese", "M"): "Bắp rang Cheese (M)",
                ("cheese", "L"): "Bắp rang Cheese (L)",
                ("mix", "S"): "Bắp rang Mix (S)",
                ("mix", "M"): "Bắp rang Mix (M)",
                ("mix", "L"): "Bắp rang Mix (L)",
            }
            food_name = food_names.get((pc, size))
            price = popcorn_prices.get((pc, size), 0)
            if food_name:
                self.food_order.append((None, food_name, qty, price))

        # Nước uống
        drink_names = {
            "pepsi": "Pepsi",
            "coca": "Coca-Cola",
            "fanta": "Fanta Cam",
            "7up": "7UP"
        }
        for drink, var in self._drink_vars.items():
            if var.get():
                qty = int(self._drink_qtys[drink].get())
                food_name = drink_names.get(drink)
                price = drink_prices.get(drink, 0)
                if food_name:
                    self.food_order.append((None, food_name, qty, price))

        # Combo
        if self._combo_var.get():
            qty = int(self._combo_qty.get())
            self.food_order.append((None, "Combo 1 (Bắp M + Nước)", qty, 80000))

        self._show_step(4)

    # ═══════════════════════════════════════════════════════
    # BƯỚC 5 — XÁC NHẬN
    # ═══════════════════════════════════════════════════════
    def _page_confirm(self):
        canvas = tk.Canvas(self.content, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        inner  = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scroll.pack(side="right", fill="y")

        ticket = tk.Frame(inner, bg=CARD, highlightbackground=ACCENT, highlightthickness=2)
        ticket.pack(padx=60, pady=20, fill="x")
        tk.Frame(ticket, bg=ACCENT).pack(fill="x")
        th = tk.Frame(ticket, bg=ACCENT); th.pack(fill="x")
        tk.Label(th, text="🎬  THÔNG TIN VÉ XEM PHIM",
                bg=ACCENT, fg=WHITE, font=("Georgia", 14, "bold"), pady=10).pack()

        body = tk.Frame(ticket, bg=CARD); body.pack(fill="x", padx=30, pady=20)
        sh   = self.selected_show
        mv   = self.selected_movie

        def row(label, value, val_color=WHITE):
            f = tk.Frame(body, bg=CARD); f.pack(fill="x", pady=3)
            tk.Label(f, text=label, bg=CARD, fg=GRAY,
                    font=("Arial", 10), width=18, anchor="w").pack(side="left")
            tk.Label(f, text=value, bg=CARD, fg=val_color, font=("Arial", 10, "bold")).pack(side="left")

        row("Phim:",        mv[1])
        row("Thể loại:",    mv[2], GRAY)
        row("Thời lượng:",  f"{mv[3]} phút", GRAY)
        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=8)
        row("Phòng chiếu:", sh[3], ACCENT2)
        row("Ngày chiếu:",  str(sh[1]), GREEN)
        row("Giờ chiếu:",   str(sh[2])[:5], GREEN)
        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=8)
        
        ticket_total = 0
        seat_display = []
        for seat in self.selected_seats:
            price = seat[4]  # base_price
            ticket_total += price
            seat_display.append(f"{seat[1]}({seat[3]})")
        
        row("Ghế đã chọn:", "  ".join(seat_display), GREEN)
        row("Tiền vé:", f"{int(ticket_total):,} VNĐ", GREEN)

        food_total = 0
        if self.food_order:
            tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=8)
            tk.Label(body, text="Đồ ăn & nước:", bg=CARD, fg=GRAY, font=("Arial", 10)).pack(anchor="w")
            for _, name, qty, price in self.food_order:
                f = tk.Frame(body, bg=CARD); f.pack(fill="x", padx=20)
                tk.Label(f, text=f"  • {name} x{qty}", bg=CARD, fg=WHITE, font=("Arial", 10)).pack(side="left")
                tk.Label(f, text=f"{int(price*qty):,} VNĐ", bg=CARD, fg=GREEN, font=("Arial", 10)).pack(side="right")
                food_total += price * qty
            row("Tiền đồ ăn:", f"{int(food_total):,} VNĐ", ACCENT2)

        tk.Frame(body, bg=ACCENT, height=2).pack(fill="x", pady=10)
        
        grand = ticket_total + food_total
        row("Tổng tiền:", f"{int(grand):,} VNĐ", WHITE)

        # THÔNG TIN KHÁCH HÀNG
        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=8)
        tk.Label(body, text="👤  THÔNG TIN KHÁCH HÀNG",
                bg=CARD, fg=GREEN, font=("Arial", 11, "bold")).pack(anchor="w", pady=(4, 8))

        f_name = tk.Frame(body, bg=CARD); f_name.pack(fill="x", pady=4)
        tk.Label(f_name, text="Họ và tên: *", bg=CARD, fg=GRAY,
                font=("Arial", 10), width=18, anchor="w").pack(side="left")
        self._customer_name_entry = tk.Entry(f_name, font=("Arial", 11), width=30,
                                            bg=CARD2, fg=WHITE, insertbackground=WHITE, relief="flat",
                                            highlightthickness=1,
                                            highlightbackground=BORDER, highlightcolor=ACCENT)
        self._customer_name_entry.pack(side="left", ipady=5)

        f_phone = tk.Frame(body, bg=CARD); f_phone.pack(fill="x", pady=4)
        tk.Label(f_phone, text="Số điện thoại: *", bg=CARD, fg=GRAY,
                font=("Arial", 10), width=18, anchor="w").pack(side="left")
        self._customer_phone_entry = tk.Entry(f_phone, font=("Arial", 11), width=30,
                                             bg=CARD2, fg=WHITE, insertbackground=WHITE, relief="flat",
                                             highlightthickness=1,
                                             highlightbackground=BORDER, highlightcolor=ACCENT)
        self._customer_phone_entry.pack(side="left", ipady=5)

        tk.Button(self.bottom, text="← Quay lại", bg=CARD2, fg=GRAY,
                font=("Arial", 10), relief="flat",
                command=lambda: self._show_step(3)).pack(side="left", padx=20, pady=10)
        tk.Button(self.bottom, text="✅  XÁC NHẬN & ĐẶT VÉ",
                bg=GREEN, fg="black", font=("Arial", 12, "bold"),
                relief="flat", cursor="hand2",
                command=self._book_now).pack(side="right", padx=20, pady=10)

    # ═══════════════════════════════════════════════════════
    # ĐẶT VÉ
    # ═══════════════════════════════════════════════════════
    def _book_now(self):
        name = self._customer_name_entry.get().strip()
        phone = self._customer_phone_entry.get().strip()

        if not name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập họ tên khách hàng!")
            return

        if not phone:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập số điện thoại!")
            return

        if len(phone) != 10:
            messagebox.showwarning("Số điện thoại không hợp lệ", 
                                   "Số điện thoại phải có đúng 10 số!\nVí dụ: 0912345678")
            return

        if phone[0] != '0':
            messagebox.showwarning("Số điện thoại không hợp lệ", 
                                   "Số điện thoại phải bắt đầu bằng số 0!\nVí dụ: 0912345678")
            return

        if not phone.isdigit():
            messagebox.showwarning("Số điện thoại không hợp lệ", 
                                   "Số điện thoại chỉ được chứa chữ số!")
            return

        if not self.selected_seats:
            messagebox.showwarning("Chưa chọn ghế", "Vui lòng chọn ghế trước khi đặt vé!")
            return

        sid = self.selected_show[0]
        seats = ",".join(str(s[0]) for s in self.selected_seats)
        eid = self.current_employee[0]

        try:
            conn = get_connection()
            cur = conn.cursor()

            # Tạo đơn đặt vé
            cur.execute("{CALL sp_TaoDonDatVe (?, ?, ?, ?, ?)}", 
                        (name, phone, sid, seats, eid))

            conn.commit()

            # Lấy booking_id vừa tạo
            cur.execute("""
                SELECT TOP 1 b.booking_id 
                FROM Bookings b
                WHERE b.customer_id = (SELECT customer_id FROM Customers WHERE phone = ?)
                ORDER BY b.booking_date DESC
            """, (phone,))

            result = cur.fetchone()
            if not result:
                cur.execute("SELECT TOP 1 booking_id FROM Bookings ORDER BY booking_id DESC")
                result = cur.fetchone()

            if not result:
                raise Exception("Không tìm thấy booking_id sau khi tạo đơn!")

            booking_id = result[0]

            # Thêm đồ ăn vào đơn - Lấy đúng food_id và giá từ DB
            for _, food_name, qty, _ in self.food_order:
                cur.execute("SELECT food_id, price FROM Food_Items WHERE food_name = ?", (food_name,))
                food = cur.fetchone()
                if food:
                    food_id, price = food
                    cur.execute(
                        "INSERT INTO Booking_Food (booking_id, food_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                        (booking_id, food_id, qty, price)
                    )
                else:
                    print(f"Warning: Không tìm thấy món: {food_name}")

            conn.commit()

            # Xác nhận đơn
            cur.execute("{CALL sp_XacNhanDonDatVe (?)}", (booking_id,))
            conn.commit()

            # Thanh toán
            cur.execute("{CALL sp_ThanhToan (?)}", (booking_id,))
            conn.commit()

            conn.close()

            ticket_total = sum(s[4] for s in self.selected_seats)

            # Tính lại tổng tiền đồ ăn từ DB để hiển thị chính xác
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT SUM(quantity * unit_price) as food_total
                FROM Booking_Food
                WHERE booking_id = ?
            """, (booking_id,))
            food_result = cur.fetchone()
            food_total = food_result[0] if food_result and food_result[0] else 0
            conn.close()

            grand_total = ticket_total + food_total

            msg = f"✅ ĐẶT VÉ THÀNH CÔNG!\n\n"
            msg += f"Mã đơn: {booking_id}\n"
            msg += f"Khách hàng: {name}\n"
            msg += f"SĐT: {phone}\n"
            msg += f"Phim: {self.selected_movie[1]}\n"
            msg += f"Suất: {self.selected_show[1]} {str(self.selected_show[2])[:5]}\n"
            msg += f"Ghế: {', '.join(s[1] for s in self.selected_seats)}\n"
            msg += f"\n💰 Tổng tiền: {int(grand_total):,} VNĐ"

            messagebox.showinfo("Thành công", msg)

            # Reset và quay lại màn hình chọn phim
            self.selected_movie = None
            self.selected_show = None
            self.selected_seats = []
            self.food_order = []
            self._show_step(0)

        except Exception as e:
            error_msg = str(e)

            if "đã được đăng ký cho khách hàng" in error_msg:
                import re
                match = re.search(r'"([^"]+)"', error_msg)
                if match:
                    existing_name = match.group(1)
                    messagebox.showerror("Lỗi", 
                        f"❌ Số điện thoại {phone} đã được đăng ký cho khách hàng \"{existing_name}\".\n\n"
                        f"Không thể đặt vé với tên \"{name}\"!\n\n"
                        f"Vui lòng sử dụng đúng tên đã đăng ký hoặc số điện thoại khác.")
                else:
                    messagebox.showerror("Lỗi", f"❌ {error_msg}")
            elif "ghế đã được đặt" in error_msg:
                messagebox.showerror("Lỗi", "❌ Có ghế đã được đặt! Vui lòng chọn lại.")
                self._show_step(2)
            elif "10 số" in error_msg:
                messagebox.showerror("Lỗi", "❌ Số điện thoại phải có đúng 10 số!")
            elif "bắt đầu bằng số 0" in error_msg:
                messagebox.showerror("Lỗi", "❌ Số điện thoại phải bắt đầu bằng số 0!")
            elif "chứa chữ số" in error_msg:
                messagebox.showerror("Lỗi", "❌ Số điện thoại chỉ được chứa chữ số!")
            else:
                messagebox.showerror("Lỗi", f"❌ Đặt vé thất bại:\n{error_msg}")
    
    # ═══════════════════════════════════════════════════════
    # QUẢN LÝ & THỐNG KÊ (giữ nguyên từ file trước)
    # ═══════════════════════════════════════════════════════
    def _show_management(self):
        self._highlight_step(-1)
        self._clear_content()

        filter_bar = tk.Frame(self.content, bg=CARD2)
        filter_bar.pack(fill="x")
        tk.Label(filter_bar, text="📊  THỐNG KÊ & QUẢN LÝ",
                 bg=CARD2, fg=GREEN, font=("Arial", 13, "bold")).pack(side="left", padx=20, pady=10)

        import datetime
        now = datetime.datetime.now()
        tk.Label(filter_bar, text="Năm:", bg=CARD2, fg=WHITE, font=("Arial", 10)).pack(side="left", padx=(20, 4))
        self._stat_year = tk.IntVar(value=now.year)
        tk.Spinbox(filter_bar, from_=2020, to=2030, textvariable=self._stat_year,
                   width=6, font=("Arial", 10)).pack(side="left")
        tk.Label(filter_bar, text="Tháng:", bg=CARD2, fg=WHITE, font=("Arial", 10)).pack(side="left", padx=(14, 4))
        self._stat_month = tk.StringVar(value=str(now.month))
        ttk.Combobox(filter_bar, textvariable=self._stat_month,
                     values=["Tất cả"] + [str(i) for i in range(1, 13)],
                     state="readonly", width=8, font=("Arial", 10)).pack(side="left")
        tk.Button(filter_bar, text="🔍 Xem", bg=ACCENT, fg=WHITE,
                  font=("Arial", 10, "bold"), relief="flat",
                  command=self._load_stats).pack(side="left", padx=14, pady=8)

        tk.Button(filter_bar, text="🎬  ← Quay Lại Đặt Vé",
                  bg=GREEN, fg="black", font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2",
                  command=lambda: self._show_step(0)).pack(side="right", padx=20, pady=8)

        nb = ttk.Notebook(self.content)
        nb.pack(fill="both", expand=True, padx=10, pady=6)

        self._tab_revenue   = ttk.Frame(nb)
        self._tab_ve_nv     = ttk.Frame(nb)
        self._tab_khach     = ttk.Frame(nb)
        self._tab_employees = ttk.Frame(nb)

        nb.add(self._tab_revenue,   text="  💰 Doanh Thu  ")
        nb.add(self._tab_ve_nv,     text="  🎫 Vé NV Bán Được  ")
        nb.add(self._tab_khach,     text="  👥 Khách Đặt Vé  ")
        nb.add(self._tab_employees, text="  👤 Quản Lý Nhân Viên  ")

        self._load_stats()
        self._build_employee_tab()

    def _load_stats(self):
        year = self._stat_year.get()
        m_str = self._stat_month.get()
        month = None if m_str == "Tất cả" else int(m_str)

        try:
            conn = get_connection(); cur = conn.cursor()

            for w in self._tab_revenue.winfo_children(): w.destroy()
            cur.execute("{CALL sp_DoanhThuTheoThang (?, ?, ?)}", (year, month, None))
            rows = cur.fetchall()
            self._make_table(
                self._tab_revenue,
                ["Năm", "Tháng", "Nhân Viên", "Số Đơn", "Số Vé", "Tiền Vé (VNĐ)", "Tiền Đồ Ăn (VNĐ)", "Tổng (VNĐ)"],
                [[str(r[0]), str(r[1]), r[2], str(r[3]), str(r[4]),
                  f"{int(r[5]):,}", f"{int(r[6]):,}", f"{int(r[7]):,}"] for r in rows],
                col_widths=[60, 70, 160, 80, 70, 140, 150, 140],
                total_col=7
            )

            for w in self._tab_ve_nv.winfo_children(): w.destroy()
            cur.execute("{CALL sp_ThongKeVeNhanVien (?, ?)}", (year, month))
            rows = cur.fetchall()
            if rows:
                pod = tk.Frame(self._tab_ve_nv, bg=BG); pod.pack(fill="x", padx=20, pady=10)
                medals = ["🥇", "🥈", "🥉"]
                for i, r in enumerate(rows[:3]):
                    c = tk.Frame(pod, bg=CARD,
                                 highlightbackground=GREEN if i == 0 else BORDER,
                                 highlightthickness=2 if i == 0 else 1)
                    c.pack(side="left", padx=10, ipadx=16, ipady=10)
                    tk.Label(c, text=medals[i], bg=CARD, font=("Arial", 20)).pack()
                    tk.Label(c, text=r[1], bg=CARD, fg=WHITE, font=("Arial", 11, "bold")).pack()
                    tk.Label(c, text=r[2], bg=CARD, fg=GRAY, font=("Arial", 9)).pack()
                    tk.Label(c, text=f"{r[3]} đơn  •  {r[4]} vé", bg=CARD, fg=ACCENT2, font=("Arial", 9)).pack()
                    tk.Label(c, text=f"Vé: {int(r[5]):,} VNĐ", bg=CARD, fg=GREEN, font=("Arial", 10, "bold")).pack()
                    tk.Label(c, text=f"ĐA: {int(r[6]):,} VNĐ", bg=CARD, fg=ACCENT2, font=("Arial", 9)).pack()
            self._make_table(
                self._tab_ve_nv,
                ["#", "Nhân Viên", "Chức Vụ", "Số Đơn", "Số Vé", "Tiền Vé (VNĐ)", "Tiền Đồ Ăn (VNĐ)"],
                [[str(i+1), r[1], r[2], str(r[3]), str(r[4]),
                  f"{int(r[5]):,}", f"{int(r[6]):,}"] for i, r in enumerate(rows)],
                col_widths=[40, 180, 120, 80, 80, 150, 160]
            )

            for w in self._tab_khach.winfo_children(): w.destroy()
            cur.execute("{CALL sp_KhachDatVeTheoPhim (?, ?)}", (year, month))
            rows = cur.fetchall()
            self._make_table(
                self._tab_khach,
                ["Phim", "Thể Loại", "Khách Hàng", "SĐT", "Mã ĐH",
                 "Thời Gian Đặt", "Số Vé", "Tiền Vé", "Ngày Chiếu", "Giờ", "Phòng", "Trạng Thái"],
                [[r[0], r[1], r[2], r[3], str(r[4]),
                  str(r[5])[:16], str(r[6]), f"{int(r[7]):,}",
                  str(r[8]), str(r[9])[:5], r[10], r[11]] for r in rows],
                col_widths=[180, 90, 150, 110, 60, 140, 60, 110, 100, 60, 130, 100]
            )

            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi thống kê", str(e))

    def _build_employee_tab(self):
        for w in self._tab_employees.winfo_children(): w.destroy()

        top = tk.Frame(self._tab_employees, bg=BG)
        top.pack(fill="x", padx=16, pady=10)
        tk.Label(top, text="Danh Sách Nhân Viên", bg=BG, fg=GREEN,
                 font=("Arial", 11, "bold")).pack(side="left")
        tk.Button(top, text="＋ Thêm Nhân Viên", bg=GREEN, fg="black",
                  font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._add_employee_dialog).pack(side="right")

        frame = tk.Frame(self._tab_employees, bg=BG)
        frame.pack(fill="both", expand=True, padx=16, pady=4)

        cols = ("ID", "Họ Tên", "Chức Vụ", "SĐT", "Email", "Ngày VL", "Lương", "Trạng Thái")
        tree = ttk.Treeview(frame, columns=[str(i) for i in range(len(cols))],
                            show="headings", height=12, selectmode="browse")
        style = ttk.Style()
        style.configure("Treeview", background=CARD, foreground=WHITE,
                        fieldbackground=CARD, rowheight=28, font=("Arial", 9))
        style.configure("Treeview.Heading", background=CARD2, foreground=GREEN,
                        font=("Arial", 9, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)])

        widths = [50, 180, 100, 110, 180, 100, 120, 90]
        for i, (h, w) in enumerate(zip(cols, widths)):
            tree.heading(str(i), text=h)
            tree.column(str(i), width=w, anchor="center")

        tree.tag_configure("active",   background=CARD)
        tree.tag_configure("inactive", background="#2A1010", foreground=GRAY)
        tree.tag_configure("manager",  background="#1A1A30", foreground=GREEN)

        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT employee_id, full_name, position, phone, email,
                       hire_date, salary, is_active
                FROM Employees ORDER BY is_active DESC, position, full_name
            """)
            emps = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e)); return

        for r in emps:
            status = "Đang làm" if r[7] else "Đã nghỉ"
            tag = "inactive" if not r[7] else ("manager" if r[2] == "Quản lý" else "active")
            tree.insert("", "end",
                        values=(r[0], r[1], r[2], r[3], r[4],
                                str(r[5])[:10], f"{int(r[6]):,}", status),
                        tags=(tag,))

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        frame.grid_rowconfigure(0, weight=1); frame.grid_columnconfigure(0, weight=1)

        def fire_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn nhân viên cần sa thải!")
                return
            vals = tree.item(sel[0])["values"]
            emp_id, emp_name, emp_status = vals[0], vals[1], vals[7]
            if emp_status == "Đã nghỉ":
                messagebox.showinfo("Thông báo", f"{emp_name} đã nghỉ việc rồi!")
                return
            confirm = messagebox.askyesno("Xác nhận",
                                          f"Sa thải nhân viên '{emp_name}'?\nHành động này không thể hoàn tác!")
            if not confirm: return
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("{CALL sp_SaThaiNhanVien (?, ?)}",
                            (emp_id, self.current_employee[0]))
                conn.commit(); conn.close()
                messagebox.showinfo("Thành công", f"Đã sa thải {emp_name}!")
                self._build_employee_tab()
            except Exception as e:
                msg = str(e)
                if "chính mình" in msg:
                    messagebox.showerror("Lỗi", "❌ Không thể tự sa thải chính mình!")
                else:
                    messagebox.showerror("Lỗi", msg)

        tk.Button(self._tab_employees, text="🔴 Sa Thải Nhân Viên Đã Chọn",
                  bg="#8B0000", fg=WHITE, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2",
                  command=fire_selected).pack(pady=(6, 10))

    def _add_employee_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Thêm Nhân Viên")
        dlg.geometry("400x420")
        dlg.configure(bg=CARD)
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text="＋  THÊM NHÂN VIÊN", bg=CARD, fg=GREEN,
                 font=("Arial", 13, "bold")).pack(pady=(20, 14))

        fields = [("Họ tên:*", "name", ""),
                  ("SĐT:*", "phone", "0900000000"),
                  ("Email:", "email", "nv@cinema.vn"),
                  ("Lương:*", "salary", "10000000"),
                  ("Mật khẩu:*", "pw", "123456")]
        entries = {}
        for label, key, default in fields:
            f = tk.Frame(dlg, bg=CARD); f.pack(pady=4)
            tk.Label(f, text=label, bg=CARD, fg=WHITE,
                     font=("Arial", 10), width=14, anchor="w").pack(side="left")
            e = tk.Entry(f, font=("Arial", 11), width=20,
                         bg=CARD2, fg=WHITE, insertbackground=WHITE, relief="flat")
            e.insert(0, default)
            e.pack(side="left", ipady=5)
            entries[key] = e

        tk.Label(dlg, text="Chức vụ:*", bg=CARD, fg=WHITE, font=("Arial", 10)).pack()
        pos_var = tk.StringVar(value="Nhân viên")
        pf = tk.Frame(dlg, bg=CARD); pf.pack()
        for p in ["Nhân viên", "Quản lý"]:
            tk.Radiobutton(pf, text=p, variable=pos_var, value=p,
                           bg=CARD, fg=WHITE, selectcolor=ACCENT,
                           activebackground=CARD, font=("Arial", 10)).pack(side="left", padx=12)

        err_lbl = tk.Label(dlg, text="", bg=CARD, fg=ACCENT, font=("Arial", 9))
        err_lbl.pack()

        def do_add():
            name = entries["name"].get().strip()
            phone = entries["phone"].get().strip()
            salary = entries["salary"].get().strip()
            pw = entries["pw"].get()
            
            if not name:
                err_lbl.config(text="⚠ Họ tên không được để trống!")
                return
            if not phone or len(phone) < 10:
                err_lbl.config(text="⚠ SĐT phải có ít nhất 10 số!")
                return
            try:
                salary_val = float(salary)
                if salary_val <= 0:
                    err_lbl.config(text="⚠ Lương phải lớn hơn 0!")
                    return
            except:
                err_lbl.config(text="⚠ Lương phải là số!")
                return
            if not pw or len(pw) < 4:
                err_lbl.config(text="⚠ Mật khẩu phải có ít nhất 4 ký tự!")
                return
            
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("""
                    INSERT INTO Employees(full_name, position, phone, email, salary, password_hash, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (name, pos_var.get(), phone, entries["email"].get(), salary_val, pw))
                conn.commit(); conn.close()
                messagebox.showinfo("Thành công", f"Đã thêm nhân viên: {name}")
                dlg.destroy()
                self._build_employee_tab()
            except Exception as e:
                err_lbl.config(text=f"⚠ {str(e)[:80]}")

        tk.Button(dlg, text="✅ Thêm", bg=GREEN, fg="black",
                  font=("Arial", 11, "bold"), relief="flat",
                  padx=16, pady=8, command=do_add).pack(pady=(8, 0))
        
        tk.Label(dlg, text="* Bắt buộc", bg=CARD, fg=GRAY, font=("Arial", 8)).pack()

    def _make_table(self, parent, headers, rows, col_widths, total_col=None):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=6)

        cols = [str(i) for i in range(len(headers))]
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                            height=12, selectmode="browse")

        style = ttk.Style()
        style.configure("Treeview", background=CARD, foreground=WHITE,
                        fieldbackground=CARD, rowheight=28, font=("Arial", 9))
        style.configure("Treeview.Heading", background=CARD2,
                        foreground=GREEN, font=("Arial", 9, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)])

        for i, (h, w) in enumerate(zip(headers, col_widths)):
            tree.heading(str(i), text=h)
            tree.column(str(i), width=w, minwidth=w, anchor="center")

        tree.tag_configure("odd",  background=CARD)
        tree.tag_configure("even", background="#1A1A30")

        total = 0
        for ri, row in enumerate(rows):
            tag = "odd" if ri % 2 == 0 else "even"
            tree.insert("", "end", values=row, tags=(tag,))
            if total_col is not None:
                try: total += int(row[total_col].replace(",", ""))
                except: pass

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1); frame.grid_columnconfigure(0, weight=1)

        if total_col is not None and rows:
            tk.Label(parent, text=f"Tổng: {total:,} VNĐ",
                     bg=BG, fg=GREEN, font=("Arial", 10, "bold")).pack(anchor="e", padx=20, pady=4)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = CinemaApp(root)
    root.mainloop()

