import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from datetime import datetime, timedelta

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SuperPOSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SUPER_POS - CarOps Auto")
        self.geometry("1300x820")
        
        self.init_db()
        self.cart = []
        self.setup_ui()

    def init_db(self):
        self.conn = sqlite3.connect("super_pos.db")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                part_name TEXT,
                car_models TEXT,
                engine_types TEXT,
                years TEXT,
                prix_achat REAL,
                prix_vente REAL,
                stock INTEGER
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_vente TEXT,
                total_vente REAL,
                total_profit REAL,
                methode_paiement TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT,
                phone TEXT,
                address TEXT,
                footer_text TEXT
            )
        ''')
        
        self.cursor.execute("SELECT COUNT(*) FROM settings")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO settings (store_name, phone, address, footer_text) 
                VALUES (?, ?, ?, ?)
            ''', ("CarOps Auto", "0700000000", "شارع فلاح عيسى، باتنة", "شكراً لزيارتكم - نترقب عودتكم"))
            self.conn.commit()

        self.conn.commit()

    def get_settings(self):
        self.cursor.execute("SELECT store_name, phone, address, footer_text FROM settings LIMIT 1")
        res = self.cursor.fetchone()
        if res:
            return {"store_name": res[0], "phone": res[1], "address": res[2], "footer_text": res[3]}
        return {"store_name": "CarOps Auto", "phone": "0000000000", "address": "باتنة، الجزائر", "footer_text": "شكراً لزيارتكم"}

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # الشريط الجانبي
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1e1e2e")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        title_lbl = ctk.CTkLabel(self.sidebar, text="SUPER_POS\nCarOps Auto", font=("Arial", 20, "bold"), text_color="#89b4fa")
        title_lbl.pack(pady=25)

        self.btn_pos = ctk.CTkButton(self.sidebar, text="🛒 نقطة البيع", font=("Arial", 14, "bold"), 
                                     fg_color="#313244", hover_color="#45475a", anchor="w", command=self.show_pos_tab)
        self.btn_pos.pack(pady=8, padx=15, fill="x")

        self.btn_products = ctk.CTkButton(self.sidebar, text="📦 المنتجات والمخزون", font=("Arial", 14, "bold"), 
                                          fg_color="#313244", hover_color="#45475a", anchor="w", command=self.show_products_tab)
        self.btn_products.pack(pady=8, padx=15, fill="x")

        self.btn_reports = ctk.CTkButton(self.sidebar, text="📊 التقارير", font=("Arial", 14, "bold"), 
                                         fg_color="#313244", hover_color="#45475a", anchor="w", command=self.show_reports_tab)
        self.btn_reports.pack(pady=8, padx=15, fill="x")

        self.btn_settings = ctk.CTkButton(self.sidebar, text="⚙️ الإعدادات", font=("Arial", 14, "bold"), 
                                          fg_color="#313244", hover_color="#45475a", anchor="w", command=self.show_settings_tab)
        self.btn_settings.pack(pady=8, padx=15, fill="x")

        # الحاوية الرئيسية
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#eff1f5")
        self.main_container.grid(row=0, column=1, sticky="nsew")

        self.show_reports_tab()

    def update_sidebar_buttons(self, active_button):
        for btn in [self.btn_pos, self.btn_products, self.btn_reports, self.btn_settings]:
            btn.configure(fg_color="#313244")
        active_button.configure(fg_color="#1e66f5")

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # --- 1. قسم التقارير ---
    def show_reports_tab(self):
        self.update_sidebar_buttons(self.btn_reports)
        self.clear_container()

        main_scroll = ctk.CTkScrollableFrame(self.main_container, fg_color="#f2f4f8")
        main_scroll.pack(fill="both", expand=True)

        header_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        title_lbl = ctk.CTkLabel(header_frame, text="لوحة التقارير", font=("Arial", 22, "bold"), text_color="#2c3e50")
        title_lbl.pack(side="right")

        time_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        time_buttons_frame.pack(side="left")

        btn_today = ctk.CTkButton(time_buttons_frame, text="اليوم", font=("Arial", 12, "bold"), width=80, fg_color="#e0e0e0", text_color="#333", hover_color="#cccccc", command=lambda: self.filter_reports_by_days(0))
        btn_today.pack(side="right", padx=3)

        btn_week = ctk.CTkButton(time_buttons_frame, text="هذا الأسبوع", font=("Arial", 12, "bold"), width=90, fg_color="#e0e0e0", text_color="#333", hover_color="#cccccc", command=lambda: self.filter_reports_by_days(7))
        btn_week.pack(side="right", padx=3)

        btn_month = ctk.CTkButton(time_buttons_frame, text="هذا الشهر", font=("Arial", 12, "bold"), width=80, fg_color="#e0e0e0", text_color="#333", hover_color="#cccccc", command=lambda: self.filter_reports_by_days(30))
        btn_month.pack(side="right", padx=3)

        filter_bar = ctk.CTkFrame(main_scroll, fg_color="#ffffff", corner_radius=8)
        filter_bar.pack(fill="x", padx=20, pady=10)

        btn_pdf = ctk.CTkButton(filter_bar, text="طباعة PDF", fg_color="#34495e", hover_color="#2c3e50", font=("Arial", 12, "bold"), width=90)
        btn_pdf.pack(side="left", padx=10, pady=10)

        btn_csv = ctk.CTkButton(filter_bar, text="تصدير CSV", fg_color="#27ae60", hover_color="#219150", font=("Arial", 12, "bold"), width=90)
        btn_csv.pack(side="left", padx=5, pady=10)

        btn_refresh = ctk.CTkButton(filter_bar, text="تحديث", fg_color="#2980b9", hover_color="#1f6391", font=("Arial", 12, "bold"), width=80, command=self.load_report_data)
        btn_refresh.pack(side="left", padx=10, pady=10)

        combo_cashier = ctk.CTkOptionMenu(filter_bar, values=["كل الكاشير"], width=120, fg_color="#f8f9fa", text_color="#333", button_color="#ddd")
        combo_cashier.pack(side="right", padx=5, pady=10)

        combo_payment = ctk.CTkOptionMenu(filter_bar, values=["كل طرق الدفع", "نقداً"], width=120, fg_color="#f8f9fa", text_color="#333", button_color="#ddd")
        combo_payment.pack(side="right", padx=5, pady=10)

        ctk.CTkLabel(filter_bar, text="من:", text_color="#333", font=("Arial", 12)).pack(side="right", padx=2)
        self.ent_date_from = ctk.CTkEntry(filter_bar, width=110, placeholder_text="jj/mm/aaaa", fg_color="#ffffff", text_color="#000")
        self.ent_date_from.pack(side="right", padx=5)

        ctk.CTkLabel(filter_bar, text="إلى:", text_color="#333", font=("Arial", 12)).pack(side="right", padx=2)
        self.ent_date_to = ctk.CTkEntry(filter_bar, width=110, placeholder_text="jj/mm/aaaa", fg_color="#ffffff", text_color="#000")
        self.ent_date_to.pack(side="right", padx=5)

        sub_tabs_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        sub_tabs_frame.pack(fill="x", padx=20, pady=5)

        tabs = ["سجل النشاط", "الفواتير", "المخزون", "الفئات", "المنتجات", "الرئيسية"]
        for t in tabs:
            is_active = (t == "الرئيسية")
            btn_t = ctk.CTkButton(sub_tabs_frame, text=t, font=("Arial", 13, "bold"),
                                  fg_color="#2980b9" if is_active else "#ffffff",
                                  text_color="#ffffff" if is_active else "#555555",
                                  hover_color="#1f6391" if is_active else "#e0e0e0",
                                  corner_radius=6, height=35)
            btn_t.pack(side="right", padx=4, expand=True, fill="x")

        cards_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)

        self.card_sales = ctk.CTkFrame(cards_frame, fg_color="#ffffff", corner_radius=8)
        self.card_sales.pack(side="right", expand=True, fill="both", padx=5)
        ctk.CTkLabel(self.card_sales, text="المبيعات", font=("Arial", 13, "bold"), text_color="#7f8c8d").pack(pady=(10, 5))
        self.lbl_sales_val = ctk.CTkLabel(self.card_sales, text="0.00", font=("Arial", 22, "bold"), text_color="#2980b9")
        self.lbl_sales_val.pack(pady=(0, 10))

        self.card_profit = ctk.CTkFrame(cards_frame, fg_color="#ffffff", corner_radius=8)
        self.card_profit.pack(side="right", expand=True, fill="both", padx=5)
        ctk.CTkLabel(self.card_profit, text="الأرباح", font=("Arial", 13, "bold"), text_color="#7f8c8d").pack(pady=(10, 5))
        self.lbl_profit_val = ctk.CTkLabel(self.card_profit, text="0.00", font=("Arial", 22, "bold"), text_color="#27ae60")
        self.lbl_profit_val.pack(pady=(0, 10))

        self.card_invoices = ctk.CTkFrame(cards_frame, fg_color="#ffffff", corner_radius=8)
        self.card_invoices.pack(side="right", expand=True, fill="both", padx=5)
        ctk.CTkLabel(self.card_invoices, text="الفواتير", font=("Arial", 13, "bold"), text_color="#7f8c8d").pack(pady=(10, 5))
        self.lbl_invoices_val = ctk.CTkLabel(self.card_invoices, text="0", font=("Arial", 22, "bold"), text_color="#2c3e50")
        self.lbl_invoices_val.pack(pady=(0, 10))

        self.card_alerts = ctk.CTkFrame(cards_frame, fg_color="#ffffff", corner_radius=8)
        self.card_alerts.pack(side="right", expand=True, fill="both", padx=5)
        ctk.CTkLabel(self.card_alerts, text="تنبيهات المخزون", font=("Arial", 13, "bold"), text_color="#7f8c8d").pack(pady=(10, 5))
        self.lbl_alerts_val = ctk.CTkLabel(self.card_alerts, text="0", font=("Arial", 22, "bold"), text_color="#e74c3c")
        self.lbl_alerts_val.pack(pady=(0, 10))

        charts_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        charts_frame.pack(fill="x", padx=20, pady=10)

        right_chart_box = ctk.CTkFrame(charts_frame, fg_color="#ffffff", corner_radius=8)
        right_chart_box.pack(side="right", expand=True, fill="both", padx=5)

        ctk.CTkLabel(right_chart_box, text="المبيعات الأسبوعية", font=("Arial", 12, "bold"), text_color="#333").pack(pady=5)
        canvas_line = tk.Canvas(right_chart_box, bg="#ffffff", height=180, highlightthickness=0)
        canvas_line.pack(fill="both", expand=True, padx=10, pady=10)

        points = [(30, 140), (80, 110), (130, 120), (180, 80), (230, 50), (280, 60), (330, 30)]
        for i in range(len(points) - 1):
            canvas_line.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill="#2980b9", width=3)
            canvas_line.create_oval(points[i][0]-4, points[i][1]-4, points[i][0]+4, points[i][1]+4, fill="#2980b9")
        canvas_line.create_oval(points[-1][0]-4, points[-1][1]-4, points[-1][0]+4, points[-1][1]+4, fill="#2980b9")

        left_chart_box = ctk.CTkFrame(charts_frame, fg_color="#ffffff", corner_radius=8, width=280)
        left_chart_box.pack(side="left", fill="both", padx=5)

        ctk.CTkLabel(left_chart_box, text="توزيع الفئات", font=("Arial", 12, "bold"), text_color="#333").pack(pady=5)
        canvas_donut = tk.Canvas(left_chart_box, bg="#ffffff", height=180, highlightthickness=0)
        canvas_donut.pack(fill="both", expand=True, padx=10, pady=10)

        canvas_donut.create_oval(50, 20, 190, 160, fill="#2ecc71", outline="")
        canvas_donut.create_oval(85, 55, 155, 125, fill="#ffffff", outline="")

        self.load_report_data()

    def load_report_data(self):
        self.cursor.execute("SELECT SUM(total_vente), SUM(total_profit), COUNT(id) FROM sales")
        res = self.cursor.fetchone()
        
        total_sales = res[0] if res[0] else 0.0
        total_profit = res[1] if res[1] else 0.0
        total_invoices = res[2] if res[2] else 0

        self.cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= 3")
        alerts_count = self.cursor.fetchone()[0]

        self.lbl_sales_val.configure(text=f"{total_sales:.2f}")
        self.lbl_profit_val.configure(text=f"{total_profit:.2f}")
        self.lbl_invoices_val.configure(text=str(total_invoices))
        self.lbl_alerts_val.configure(text=str(alerts_count))

    def filter_reports_by_days(self, days_count):
        if days_count == 0:
            query_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("SELECT SUM(total_vente), SUM(total_profit), COUNT(id) FROM sales WHERE date_vente LIKE ?", (f"{query_date}%",))
        else:
            date_limit = (datetime.now() - timedelta(days=days_count)).strftime("%Y-%m-%d")
            self.cursor.execute("SELECT SUM(total_vente), SUM(total_profit), COUNT(id) FROM sales WHERE date_vente >= ?", (date_limit,))

        res = self.cursor.fetchone()
        total_sales = res[0] if res[0] else 0.0
        total_profit = res[1] if res[1] else 0.0
        total_invoices = res[2] if res[2] else 0

        self.lbl_sales_val.configure(text=f"{total_sales:.2f}")
        self.lbl_profit_val.configure(text=f"{total_profit:.2f}")
        self.lbl_invoices_val.configure(text=str(total_invoices))

    # --- 2. قسم نقطة البيع ---
    def show_pos_tab(self):
        self.update_sidebar_buttons(self.btn_pos)
        self.clear_container()

        frame = ctk.CTkFrame(self.main_container, fg_color="#ffffff", corner_radius=10)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # اليمين: قائمة السلة
        cart_frame = ctk.CTkFrame(frame, fg_color="#f8f9fa", width=450)
        cart_frame.pack(side="right", fill="both", padx=10, pady=10)

        ctk.CTkLabel(cart_frame, text="🛒 سلة المشتريات", font=("Arial", 16, "bold"), text_color="#333").pack(pady=10)

        columns = ("name", "qty", "price", "total")
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show="headings", height=15)
        self.cart_tree.heading("name", text="اسم القطعة")
        self.cart_tree.heading("qty", text="الكمية")
        self.cart_tree.heading("price", text="السعر")
        self.cart_tree.heading("total", text="الإجمالي")
        self.cart_tree.column("name", width=140)
        self.cart_tree.column("qty", width=60)
        self.cart_tree.column("price", width=80)
        self.cart_tree.column("total", width=80)
        self.cart_tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.lbl_cart_total = ctk.CTkLabel(cart_frame, text="المجموع: 0.00 DZD", font=("Arial", 18, "bold"), text_color="#27ae60")
        self.lbl_cart_total.pack(pady=10)

        btn_checkout = ctk.CTkButton(cart_frame, text="إتمام البيع وطباعة الفاتورة", font=("Arial", 14, "bold"), fg_color="#27ae60", hover_color="#219150", height=40, command=self.checkout)
        btn_checkout.pack(fill="x", padx=10, pady=10)

        # اليسار: البحث والمنتجات
        search_frame = ctk.CTkFrame(frame, fg_color="transparent")
        search_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(search_frame, text="البحث عن قطع الغيار (الاسم أو الباركود):", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="e", pady=5)
        
        self.ent_pos_search = ctk.CTkEntry(search_frame, placeholder_text="اكتب هنا للبحث...", font=("Arial", 13), text_color="#000", fg_color="#fff", height=35)
        self.ent_pos_search.pack(fill="x", pady=5)
        self.ent_pos_search.bind("<KeyRelease>", self.search_pos_products)

        prod_columns = ("barcode", "name", "models", "price", "stock")
        self.pos_prod_tree = ttk.Treeview(search_frame, columns=prod_columns, show="headings")
        self.pos_prod_tree.heading("barcode", text="الباركود")
        self.pos_prod_tree.heading("name", text="القطعة")
        self.pos_prod_tree.heading("models", text="السيارة")
        self.pos_prod_tree.heading("price", text="السعر")
        self.pos_prod_tree.heading("stock", text="المخزون")
        self.pos_prod_tree.pack(fill="both", expand=True, pady=10)
        self.pos_prod_tree.bind("<Double-1>", self.add_to_cart)

        self.load_pos_products()

    def load_pos_products(self, query=""):
        for row in self.pos_prod_tree.get_children():
            self.pos_prod_tree.delete(row)
        
        if query:
            self.cursor.execute("SELECT barcode, part_name, car_models, prix_vente, stock FROM products WHERE part_name LIKE ? OR barcode LIKE ?", (f"%{query}%", f"%{query}%"))
        else:
            self.cursor.execute("SELECT barcode, part_name, car_models, prix_vente, stock FROM products")

        for p in self.cursor.fetchall():
            self.pos_prod_tree.insert("", "end", values=p)

    def search_pos_products(self, event):
        q = self.ent_pos_search.get().strip()
        self.load_pos_products(q)

    def add_to_cart(self, event):
        selected = self.pos_prod_tree.selection()
        if not selected:
            return
        item = self.pos_prod_tree.item(selected[0])["values"]
        barcode, name, model, price, stock = item[0], item[1], item[2], float(item[3]), int(item[4])

        if stock <= 0:
            messagebox.showwarning("تنبيه", "هذا المنتج غير متوفر بالمخزون!")
            return

        for cart_item in self.cart:
            if cart_item["barcode"] == barcode:
                if cart_item["qty"] + 1 > stock:
                    messagebox.showwarning("تنبيه", "الكمية المطلوبة تتجاوز المخزون!")
                    return
                cart_item["qty"] += 1
                cart_item["total"] = cart_item["qty"] * price
                self.update_cart_tree()
                return

        self.cart.append({"barcode": barcode, "name": name, "price": price, "qty": 1, "total": price})
        self.update_cart_tree()

    def update_cart_tree(self):
        for r in self.cart_tree.get_children():
            self.cart_tree.delete(r)
        
        total_sum = 0
        for item in self.cart:
            self.cart_tree.insert("", "end", values=(item["name"], item["qty"], item["price"], item["total"]))
            total_sum += item["total"]
        
        self.lbl_cart_total.configure(text=f"المجموع: {total_sum:.2f} DZD")

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("تنبيه", "السلة فارغة!")
            return

        total_sales = sum(i["total"] for i in self.cart)
        total_profit = 0

        for item in self.cart:
            self.cursor.execute("SELECT prix_achat, stock FROM products WHERE barcode=?", (item["barcode"],))
            res = self.cursor.fetchone()
            if res:
                p_achat, stock = res[0], res[1]
                total_profit += (item["price"] - p_achat) * item["qty"]
                new_stock = stock - item["qty"]
                self.cursor.execute("UPDATE products SET stock=? WHERE barcode=?", (new_stock, item["barcode"]))

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO sales (date_vente, total_vente, total_profit, methode_paiement) VALUES (?, ?, ?, ?)",
                            (date_str, total_sales, total_profit, "نقداً"))
        self.conn.commit()

        messagebox.showinfo("نجاح", "تمت عملية البيع وتسجيل الفاتورة بنجاح!")
        self.cart = []
        self.update_cart_tree()
        self.load_pos_products()

    # --- 3. قسم المنتجات والمخزون ---
    def show_products_tab(self):
        self.update_sidebar_buttons(self.btn_products)
        self.clear_container()

        frame = ctk.CTkFrame(self.main_container, fg_color="#ffffff", corner_radius=10)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # النموذج (يمين)
        form_frame = ctk.CTkFrame(frame, fg_color="#f8f9fa", width=350)
        form_frame.pack(side="right", fill="y", padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="إضافة / تعديل قطعة", font=("Arial", 16, "bold"), text_color="#333").pack(pady=10)

        self.ent_p_barcode = ctk.CTkEntry(form_frame, placeholder_text="الباركود", fg_color="#fff", text_color="#000")
        self.ent_p_barcode.pack(fill="x", padx=10, pady=5)

        self.ent_p_name = ctk.CTkEntry(form_frame, placeholder_text="اسم قطعة الغيار", fg_color="#fff", text_color="#000")
        self.ent_p_name.pack(fill="x", padx=10, pady=5)

        self.ent_p_models = ctk.CTkEntry(form_frame, placeholder_text="موديلات السيارات (مثال: Golf 7)", fg_color="#fff", text_color="#000")
        self.ent_p_models.pack(fill="x", padx=10, pady=5)

        self.ent_p_engines = ctk.CTkEntry(form_frame, placeholder_text="المحرك (مثال: 2.0 TDI)", fg_color="#fff", text_color="#000")
        self.ent_p_engines.pack(fill="x", padx=10, pady=5)

        self.ent_p_years = ctk.CTkEntry(form_frame, placeholder_text="السنوات (2013-2019)", fg_color="#fff", text_color="#000")
        self.ent_p_years.pack(fill="x", padx=10, pady=5)

        self.ent_p_buy = ctk.CTkEntry(form_frame, placeholder_text="سعر الشراء (DZD)", fg_color="#fff", text_color="#000")
        self.ent_p_buy.pack(fill="x", padx=10, pady=5)

        self.ent_p_sell = ctk.CTkEntry(form_frame, placeholder_text="سعر البيع (DZD)", fg_color="#fff", text_color="#000")
        self.ent_p_sell.pack(fill="x", padx=10, pady=5)

        self.ent_p_stock = ctk.CTkEntry(form_frame, placeholder_text="الكمية بالمخزون", fg_color="#fff", text_color="#000")
        self.ent_p_stock.pack(fill="x", padx=10, pady=5)

        btn_add = ctk.CTkButton(form_frame, text="حفظ القطعة", fg_color="#27ae60", hover_color="#219150", font=("Arial", 13, "bold"), command=self.save_product)
        btn_add.pack(fill="x", padx=10, pady=15)

        # جدول المنتجات (يسار)
        list_frame = ctk.CTkFrame(frame, fg_color="transparent")
        list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        cols = ("id", "barcode", "name", "models", "buy", "sell", "stock")
        self.prod_tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        self.prod_tree.heading("id", text="ID")
        self.prod_tree.heading("barcode", text="الباركود")
        self.prod_tree.heading("name", text="القطعة")
        self.prod_tree.heading("models", text="السيارات")
        self.prod_tree.heading("buy", text="الشراء")
        self.prod_tree.heading("sell", text="البيع")
        self.prod_tree.heading("stock", text="المخزون")
        
        self.prod_tree.column("id", width=40)
        self.prod_tree.column("barcode", width=100)
        self.prod_tree.column("name", width=150)
        self.prod_tree.column("models", width=120)
        self.prod_tree.column("buy", width=80)
        self.prod_tree.column("sell", width=80)
        self.prod_tree.column("stock", width=60)
        
        self.prod_tree.pack(fill="both", expand=True)

        self.load_all_products()

    def save_product(self):
        barcode = self.ent_p_barcode.get().strip()
        name = self.ent_p_name.get().strip()
        models = self.ent_p_models.get().strip()
        engines = self.ent_p_engines.get().strip()
        years = self.ent_p_years.get().strip()
        buy = self.ent_p_buy.get().strip()
        sell = self.ent_p_sell.get().strip()
        stock = self.ent_p_stock.get().strip()

        if not barcode or not name or not sell or not stock:
            messagebox.showwarning("خطأ", "يرجى ملء كافة الحقول الأساسية!")
            return

        try:
            self.cursor.execute('''
                INSERT INTO products (barcode, part_name, car_models, engine_types, years, prix_achat, prix_vente, stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (barcode, name, models, engines, years, float(buy), float(sell), int(stock)))
            self.conn.commit()
            messagebox.showinfo("نجاح", "تمت إضافة القطعة بنجاح")
            self.load_all_products()
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر الإضافة (قد يكون الباركود مكرراً): {e}")

    def load_all_products(self):
        for r in self.prod_tree.get_children():
            self.prod_tree.delete(r)
        self.cursor.execute("SELECT id, barcode, part_name, car_models, prix_achat, prix_vente, stock FROM products")
        for row in self.cursor.fetchall():
            self.prod_tree.insert("", "end", values=row)

    # --- 4. قسم الإعدادات ---
    def show_settings_tab(self):
        self.update_sidebar_buttons(self.btn_settings)
        self.clear_container()

        frame = ctk.CTkFrame(self.main_container, fg_color="#ffffff", corner_radius=10)
        frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(frame, text="⚙️ إعدادات المتجر والفواتير", font=("Arial", 18, "bold"), text_color="#333").pack(pady=20)

        settings = self.get_settings()

        self.ent_st_name = ctk.CTkEntry(frame, width=400, fg_color="#f8f9fa", text_color="#000")
        self.ent_st_name.insert(0, settings["store_name"])
        self.ent_st_name.pack(pady=10)

        self.ent_st_phone = ctk.CTkEntry(frame, width=400, fg_color="#f8f9fa", text_color="#000")
        self.ent_st_phone.insert(0, settings["phone"])
        self.ent_st_phone.pack(pady=10)

        self.ent_st_addr = ctk.CTkEntry(frame, width=400, fg_color="#f8f9fa", text_color="#000")
        self.ent_st_addr.insert(0, settings["address"])
        self.ent_st_addr.pack(pady=10)

        self.ent_st_foot = ctk.CTkEntry(frame, width=400, fg_color="#f8f9fa", text_color="#000")
        self.ent_st_foot.insert(0, settings["footer_text"])
        self.ent_st_foot.pack(pady=10)

        btn_save = ctk.CTkButton(frame, text="حفظ التغييرات", font=("Arial", 14, "bold"), fg_color="#1e66f5", width=200, command=self.save_settings)
        btn_save.pack(pady=20)

    def save_settings(self):
        name = self.ent_st_name.get()
        phone = self.ent_st_phone.get()
        addr = self.ent_st_addr.get()
        foot = self.ent_st_foot.get()

        self.cursor.execute("UPDATE settings SET store_name=?, phone=?, address=?, footer_text=? WHERE id=1", (name, phone, addr, foot))
        self.conn.commit()
        messagebox.showinfo("نجاح", "تم حفظ الإعدادات بنجاح!")

if __name__ == "__main__":
    app = SuperPOSApp()
    app.mainloop()
