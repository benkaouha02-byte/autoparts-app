import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from datetime import datetime

# ضبط المظهر العام للمظهر الاحترافي الداكن/الفاتح
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SuperPOSPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SUPER_POS Pro - CarOps Auto Parts Management System")
        self.geometry("1280x750")
        self.minsize(1100, 680)

        self.init_db()
        self.cart = []

        self.setup_ui()

    def init_db(self):
        self.conn = sqlite3.connect("super_pos_auto.db")
        self.cursor = self.conn.cursor()

        # جدول قطع السيارات المتكامل
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                part_name TEXT,
                car_model TEXT,
                engine_type TEXT,
                year INTEGER,
                prix_achat REAL,
                prix_vente REAL,
                stock INTEGER
            )
        ''')

        # جدول المبيعات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_vente TEXT,
                total_vente REAL,
                total_profit REAL,
                methode_paiement TEXT
            )
        ''')

        # جدول تفاصيل الفاتورة
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                product_id INTEGER,
                quantite INTEGER,
                prix_unitaire REAL,
                FOREIGN KEY(sale_id) REFERENCES sales(id)
            )
        ''')

        self.conn.commit()

    def setup_ui(self):
        # الهيكل العام: شريط جانبي + مساحة العمل
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # 1. الشريط الجانبي (Sidebar Navigation)
        # ----------------------------------------------------
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1E1E2E")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # الشعار والعنوان
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=25, padx=20, fill="x")

        lbl_logo_icon = ctk.CTkLabel(logo_frame, text="⚡", font=("Arial", 28))
        lbl_logo_icon.pack(side="left", padx=5)

        lbl_title = ctk.CTkLabel(logo_frame, text="SUPER_POS", font=("Segoe UI", 20, "bold"), text_color="#38BDF8")
        lbl_title.pack(side="left")
        
        lbl_subtitle = ctk.CTkLabel(self.sidebar, text="CarOps Auto Edition v2.5", font=("Segoe UI", 10), text_color="#94A3B8")
        lbl_subtitle.pack(pady=(0, 20))

        # أزرار التنقل الرئيسية
        self.btn_pos = self.create_nav_button("🛒  نقطة البيع (POS)", self.show_pos)
        self.btn_inventory = self.create_nav_button("📦  إدارة المخزون والقطع", self.show_inventory)
        self.btn_reports = self.create_nav_button("📊  التقارير والأرباح", self.show_reports)

        # معلومات النظام أسفل الشريط الجانبي
        system_status = ctk.CTkFrame(self.sidebar, fg_color="#181825", corner_radius=10)
        system_status.pack(side="bottom", fill="x", padx=15, pady=15)
        
        lbl_status = ctk.CTkLabel(system_status, text="● النظام متصل وحاضر", font=("Segoe UI", 11), text_color="#4ADE80")
        lbl_status.pack(pady=10)

        # ----------------------------------------------------
        # 2. منطقة عرض المحتوى الرئيسية (Main Content Frame)
        # ----------------------------------------------------
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="#11111B")
        self.content_area.grid(row=0, column=1, sticky="nsew")

        # العرض الافتراضي
        self.show_pos()

    def create_nav_button(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar, 
            text=text, 
            command=command, 
            font=("Segoe UI", 13, "bold"),
            fg_color="transparent", 
            text_color="#CDD6F4",
            hover_color="#313244",
            anchor="w",
            height=45,
            corner_radius=8
        )
        btn.pack(fill="x", padx=12, pady=5)
        return btn

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # ====================================================
    # 🛒 1. واجهة نقطة البيع (POS Interface)
    # ====================================================
    def show_pos(self):
        self.clear_content()

        # شريط العنوان العلوي للواجهة
        header = ctk.CTkFrame(self.content_area, fg_color="#1E1E2E", height=50, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="شاشة البيع والكاشير المباشر", font=("Segoe UI", 16, "bold"), text_color="#F5E0DC").pack(side="right", padx=20, pady=10)

        main_pos_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        main_pos_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # --- الجزء الأيسر: سلة المشتريات والدفع ---
        left_cart_frame = ctk.CTkFrame(main_pos_frame, width=400, fg_color="#1E1E2E", corner_radius=12)
        left_cart_frame.pack(side="left", fill="both", padx=(0, 10), pady=0)

        ctk.CTkLabel(left_cart_frame, text="سلة المشتريات الحالية", font=("Segoe UI", 15, "bold"), text_color="#F38BA8").pack(pady=12)

        # جدول السلة
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#181825", foreground="#CDD6F4", fieldbackground="#181825", rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background="#313244", foreground="#CBA6F7", font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#45475A')])

        self.cart_tree = ttk.Treeview(left_cart_frame, columns=("name", "qty", "total"), show="headings", height=12)
        self.cart_tree.heading("name", text="القطع / السيارة")
        self.cart_tree.heading("qty", text="الكمية")
        self.cart_tree.heading("total", text="المجموع")
        self.cart_tree.column("name", width=190)
        self.cart_tree.column("qty", width=50, anchor="center")
        self.cart_tree.column("total", width=90, anchor="e")
        self.cart_tree.pack(fill="both", expand=True, padx=10, pady=5)

        # ملخص الفاتورة والأزرار
        summary_frame = ctk.CTkFrame(left_cart_frame, fg_color="#181825", corner_radius=10)
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.lbl_cart_total = ctk.CTkLabel(summary_frame, text="0.00 DZD", font=("Segoe UI", 22, "bold"), text_color="#A6E3A1")
        self.lbl_cart_total.pack(pady=10)

        btn_pay = ctk.CTkButton(left_cart_frame, text="💳 إتمام العملية وطباعة الفاتورة", font=("Segoe UI", 14, "bold"), fg_color="#A6E3A1", text_color="#11111B", hover_color="#94E2D5", height=45, command=self.process_payment)
        btn_pay.pack(fill="x", padx=10, pady=(0, 10))

        btn_clear = ctk.CTkButton(left_cart_frame, text="إلغاء السلة", font=("Segoe UI", 11), fg_color="#F38BA8", text_color="#11111B", hover_color="#EBA0AC", height=30, command=self.clear_cart)
        btn_clear.pack(fill="x", padx=10, pady=(0, 10))

        # --- الجزء الأيمن: البحث وقطع الغيار ---
        right_search_frame = ctk.CTkFrame(main_pos_frame, fg_color="#1E1E2E", corner_radius=12)
        right_search_frame.pack(side="right", fill="both", expand=True)

        # شريط البحث المتطور
        search_box = ctk.CTkFrame(right_search_frame, fg_color="transparent")
        search_box.pack(fill="x", padx=15, pady=15)

        self.pos_search_entry = ctk.CTkEntry(
            search_box, 
            placeholder_text="🔍 ابحث بالاسم، السيارة (Golf, Symbol..)، المحرك (TDI..)، السنة، أو الباركود...", 
            font=("Segoe UI", 12),
            height=40,
            corner_radius=8
        )
        self.pos_search_entry.pack(fill="x")
        self.pos_search_entry.bind("<KeyRelease>", self.filter_pos_products)

        # جدول قطع الغيار المتاحة
        cols = ("id", "barcode", "part_name", "car_model", "engine", "year", "prix", "stock")
        self.pos_tree = ttk.Treeview(right_search_frame, columns=cols, show="headings")

        self.pos_tree.heading("id", text="ID")
        self.pos_tree.heading("barcode", text="الباركود")
        self.pos_tree.heading("part_name", text="اسم القطعة")
        self.pos_tree.heading("car_model", text="السيارة")
        self.pos_tree.heading("engine", text="المحرك")
        self.pos_tree.heading("year", text="العام")
        self.pos_tree.heading("prix", text="السعر")
        self.pos_tree.heading("stock", text="المخزون")

        self.pos_tree.column("id", width=35, anchor="center")
        self.pos_tree.column("barcode", width=90, anchor="center")
        self.pos_tree.column("part_name", width=120)
        self.pos_tree.column("car_model", width=110)
        self.pos_tree.column("engine", width=80, anchor="center")
        self.pos_tree.column("year", width=55, anchor="center")
        self.pos_tree.column("prix", width=85, anchor="e")
        self.pos_tree.column("stock", width=60, anchor="center")

        self.pos_tree.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        btn_add_to_cart = ctk.CTkButton(
            right_search_frame, 
            text="➕ إضافة القطعة المحددة إلى السلة", 
            font=("Segoe UI", 13, "bold"),
            fg_color="#89B4FA", 
            text_color="#11111B",
            hover_color="#B4BEFE",
            height=40,
            command=self.add_selected_to_cart
        )
        btn_add_to_cart.pack(fill="x", padx=15, pady=10)

        self.load_pos_products()

    def load_pos_products(self, query=""):
        for item in self.pos_tree.get_children():
            self.pos_tree.delete(item)

        if query:
            q = f"%{query}%"
            self.cursor.execute("""
                SELECT id, barcode, part_name, car_model, engine_type, year, prix_vente, stock 
                FROM products 
                WHERE barcode LIKE ? OR part_name LIKE ? OR car_model LIKE ? OR engine_type LIKE ? OR year LIKE ?
            """, (q, q, q, q, q))
        else:
            self.cursor.execute("SELECT id, barcode, part_name, car_model, engine_type, year, prix_vente, stock FROM products")

        for row in self.cursor.fetchall():
            self.pos_tree.insert("", "end", values=row)

    def filter_pos_products(self, event):
        self.load_pos_products(self.pos_search_entry.get().strip())

    def add_selected_to_cart(self):
        selected = self.pos_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى تحديد قطعة غيار من القائمة أولاً!")
            return
        
        item = self.pos_tree.item(selected[0])['values']
        stock = item[7]

        if stock <= 0:
            messagebox.showerror("تنبيه المخزون", "عذراً، هذه القطعة غير متوفرة في المخزون حالياً!")
            return

        self.cursor.execute("SELECT prix_achat FROM products WHERE id = ?", (item[0],))
        prix_achat = self.cursor.fetchone()[0]

        display_title = f"{item[2]} ({item[3]} - {item[4]})"
        
        # التأكد إذا كانت القطعة مجودة سابقاً في السلة
        for cart_item in self.cart:
            if cart_item['id'] == item[0]:
                if cart_item['qty'] + 1 > stock:
                    messagebox.showerror("خطأ", "لقد تجاوزت الكمية المتاحة في المخزون!")
                    return
                cart_item['qty'] += 1
                self.update_cart_display()
                return

        self.cart.append({
            'id': item[0],
            'name': display_title,
            'prix': item[6],
            'prix_achat': prix_achat,
            'qty': 1
        })
        self.update_cart_display()

    def update_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total_price = 0
        for item in self.cart:
            subtotal = item['prix'] * item['qty']
            total_price += subtotal
            self.cart_tree.insert("", "end", values=(item['name'], item['qty'], f"{subtotal:.2f}"))

        self.lbl_cart_total.configure(text=f"{total_price:.2f} DZD")

    def clear_cart(self):
        self.cart.clear()
        self.update_cart_display()

    def process_payment(self):
        if not self.cart:
            messagebox.showwarning("سلة فارغة", "الرجاء إضافة قطع غيار للسلة قبل الدفع!")
            return

        total_vente = sum(item['prix'] * item['qty'] for item in self.cart)
        total_achat = sum(item['prix_achat'] * item['qty'] for item in self.cart)
        profit = total_vente - total_achat
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("INSERT INTO sales (date_vente, total_vente, total_profit, methode_paiement) VALUES (?, ?, ?, ?)",
                            (date_now, total_vente, profit, "نقداً"))
        sale_id = self.cursor.lastrowid

        for item in self.cart:
            self.cursor.execute("INSERT INTO sale_details (sale_id, product_id, quantite, prix_unitaire) VALUES (?, ?, ?, ?)",
                                (sale_id, item['id'], item['qty'], item['prix']))
            self.cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item['qty'], item['id']))

        self.conn.commit()
        messagebox.showinfo("تمت العملية بنجاح", f"🎉 تم إتمام البيع بنجاح!\nإجمالي الفاتورة: {total_vente:.2f} DZD\nصافي الربح: {profit:.2f} DZD")
        self.clear_cart()
        self.load_pos_products()

    # ====================================================
    # 📦 2. واجهة إدارة المخزون وقطع الغيار (Inventory)
    # ====================================================
    def show_inventory(self):
        self.clear_content()

        header = ctk.CTkFrame(self.content_area, fg_color="#1E1E2E", height=50, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="إدارة قطع الغيار وإضافة المنتجات", font=("Segoe UI", 16, "bold"), text_color="#FAB387").pack(side="right", padx=20, pady=10)

        main_inv_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        main_inv_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # استمارة إدخال القطع
        form_frame = ctk.CTkFrame(main_inv_frame, fg_color="#1E1E2E", corner_radius=12)
        form_frame.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(form_frame, text="إضافة قطعة غيار جديدة إلى المخزون", font=("Segoe UI", 14, "bold"), text_color="#89B4FA").grid(row=0, column=0, columnspan=4, pady=12, padx=15, sticky="w")

        # الحقول المقسمة بوضوح
        ctk.CTkLabel(form_frame, text="اسم القطعة (مثلاً: Démarreur, Injecteur):", font=("Segoe UI", 11)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        ent_part = ctk.CTkEntry(form_frame, width=220)
        ent_part.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="اسم / موديل السيارة (مثلاً: Golf 7, Symbol):", font=("Segoe UI", 11)).grid(row=1, column=2, padx=10, pady=5, sticky="e")
        ent_car = ctk.CTkEntry(form_frame, width=220)
        ent_car.grid(row=1, column=3, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="نوع المحرك (مثلاً: 2.0 TDI, 1.2 Ess):", font=("Segoe UI", 11)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        ent_engine = ctk.CTkEntry(form_frame, width=220)
        ent_engine.grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="سنة التصنيع (العام مثلاً: 2018):", font=("Segoe UI", 11)).grid(row=2, column=2, padx=10, pady=5, sticky="e")
        ent_year = ctk.CTkEntry(form_frame, width=220)
        ent_year.grid(row=2, column=3, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="الباركود (اختياري / مسح بالدوشة):", font=("Segoe UI", 11)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        ent_bc = ctk.CTkEntry(form_frame, width=220)
        ent_bc.grid(row=3, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="الكمية المتوفرة:", font=("Segoe UI", 11)).grid(row=3, column=2, padx=10, pady=5, sticky="e")
        ent_stock = ctk.CTkEntry(form_frame, width=220)
        ent_stock.grid(row=3, column=3, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="سعر الشراء (التكلفة DZD):", font=("Segoe UI", 11)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
        ent_pa = ctk.CTkEntry(form_frame, width=220)
        ent_pa.grid(row=4, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="سعر البيع (DZD):", font=("Segoe UI", 11)).grid(row=4, column=2, padx=10, pady=5, sticky="e")
        ent_pv = ctk.CTkEntry(form_frame, width=220)
        ent_pv.grid(row=4, column=3, padx=10, pady=5)

        def save_product_action():
            try:
                bc = ent_bc.get().strip()
                part = ent_part.get().strip()
                car = ent_car.get().strip()
                engine = ent_engine.get().strip()
                year = int(ent_year.get().strip()) if ent_year.get().strip() else 0
                pa = float(ent_pa.get().strip())
                pv = float(ent_pv.get().strip())
                stock = int(ent_stock.get().strip())

                if not part or not car:
                    messagebox.showerror("خطأ", "يرجى تعبئة اسم القطعة واسم السيارة على الأقل!")
                    return

                self.cursor.execute("""
                    INSERT INTO products (barcode, part_name, car_model, engine_type, year, prix_achat, prix_vente, stock) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (bc, part, car, engine, year, pa, pv, stock))

                self.conn.commit()
                messagebox.showinfo("نجاح", "تم حفظ قطعة الغيار وتحديث المخزون بنجاح!")
                self.show_inventory()
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر الحفظ: {e}")

        btn_save = ctk.CTkButton(form_frame, text="💾 حفظ القطعة في قاعدة البيانات", font=("Segoe UI", 12, "bold"), fg_color="#A6E3A1", text_color="#11111B", hover_color="#94E2D5", height=38, command=save_product_action)
        btn_save.grid(row=5, column=0, columnspan=4, pady=15, padx=20, sticky="ew")

        # جدول استعراض كافة المخزون
        table_frame = ctk.CTkFrame(main_inv_frame, fg_color="#1E1E2E", corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=5)

        ctk.CTkLabel(table_frame, text="سجل قطع الغيار المسجلة بالمخزون", font=("Segoe UI", 13, "bold"), text_color="#CDD6F4").pack(anchor="w", padx=15, pady=10)

        cols = ("id", "barcode", "part_name", "car_model", "engine", "year", "pa", "pv", "stock")
        inv_tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        inv_tree.heading("id", text="ID")
        inv_tree.heading("barcode", text="الباركود")
        inv_tree.heading("part_name", text="القطعة")
        inv_tree.heading("car_model", text="السيارة")
        inv_tree.heading("engine", text="المحرك")
        inv_tree.heading("year", text="العام")
        inv_tree.heading("pa", text="سعر الشراء")
        inv_tree.heading("pv", text="سعر البيع")
        inv_tree.heading("stock", text="المخزون")

        inv_tree.column("id", width=30, anchor="center")
        inv_tree.column("barcode", width=90, anchor="center")
        inv_tree.column("part_name", width=120)
        inv_tree.column("car_model", width=110)
        inv_tree.column("engine", width=80, anchor="center")
        inv_tree.column("year", width=55, anchor="center")
        inv_tree.column("pa", width=80, anchor="e")
        inv_tree.column("pv", width=80, anchor="e")
        inv_tree.column("stock", width=60, anchor="center")

        inv_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.cursor.execute("SELECT id, barcode, part_name, car_model, engine_type, year, prix_achat, prix_vente, stock FROM products")
        for r in self.cursor.fetchall():
            inv_tree.insert("", "end", values=r)

    # ====================================================
    # 📊 3. واجهة التقارير والأرباح (Reports & Profit Dashboard)
    # ====================================================
    def show_reports(self):
        self.clear_content()

        header = ctk.CTkFrame(self.content_area, fg_color="#1E1E2E", height=50, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="لوحة التحليلات الأرباح والمبيعات", font=("Segoe UI", 16, "bold"), text_color="#A6E3A1").pack(side="right", padx=20, pady=10)

        main_rep_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        main_rep_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # استعلامات الأرباح والمبيعات
        self.cursor.execute("SELECT SUM(total_vente), SUM(total_profit), COUNT(id) FROM sales")
        res = self.cursor.fetchone()

        total_sales = res[0] if res[0] else 0.0
        total_profit = res[1] if res[1] else 0.0
        total_invoices = res[2] if res[2] else 0

        # بطاقات ملونة عصرية الإحصائيات (Stat Cards)
        cards_box = ctk.CTkFrame(main_rep_frame, fg_color="transparent")
        cards_box.pack(fill="x", pady=(0, 20))

        # بطاقة 1: المبيعات
        c1 = ctk.CTkFrame(cards_box, fg_color="#1E1E2E", corner_radius=12, border_width=1, border_color="#313244")
        c1.pack(side="left", expand=True, fill="both", padx=8)
        ctk.CTkLabel(c1, text="إجمالي رقم الأعمال (المبيعات)", font=("Segoe UI", 12), text_color="#94A3B8").pack(pady=(15, 5))
        ctk.CTkLabel(c1, text=f"{total_sales:,.2f} DZD", font=("Segoe UI", 20, "bold"), text_color="#89B4FA").pack(pady=(0, 15))

        # بطاقة 2: صافي الأرباح
        c2 = ctk.CTkFrame(cards_box, fg_color="#1E1E2E", corner_radius=12, border_width=1, border_color="#313244")
        c2.pack(side="left", expand=True, fill="both", padx=8)
        ctk.CTkLabel(c2, text="صافي الأرباح المحققة", font=("Segoe UI", 12), text_color="#94A3B8").pack(pady=(15, 5))
        ctk.CTkLabel(c2, text=f"{total_profit:,.2f} DZD", font=("Segoe UI", 20, "bold"), text_color="#A6E3A1").pack(pady=(0, 15))

        # بطاقة 3: عدد المبيعات
        c3 = ctk.CTkFrame(cards_box, fg_color="#1E1E2E", corner_radius=12, border_width=1, border_color="#313244")
        c3.pack(side="left", expand=True, fill="both", padx=8)
        ctk.CTkLabel(c3, text="إجمالي العمليات / الفواتير", font=("Segoe UI", 12), text_color="#94A3B8").pack(pady=(15, 5))
        ctk.CTkLabel(c3, text=str(total_invoices), font=("Segoe UI", 20, "bold"), text_color="#F9E2AF").pack(pady=(0, 15))

        # جدول سجل المبيعات الأخيرة
        sales_table_frame = ctk.CTkFrame(main_rep_frame, fg_color="#1E1E2E", corner_radius=12)
        sales_table_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(sales_table_frame, text="سجل الفواتير والمبيعات الأخيرة", font=("Segoe UI", 13, "bold"), text_color="#CDD6F4").pack(anchor="w", padx=15, pady=12)

        sales_cols = ("id", "date", "total", "profit", "method")
        sales_tree = ttk.Treeview(sales_table_frame, columns=sales_cols, show="headings")

        sales_tree.heading("id", text="رقم الفاتورة")
        sales_tree.heading("date", text="التاريخ والوقت")
        sales_tree.heading("total", text="المبلغ الإجمالي")
        sales_tree.heading("profit", text="الربح المحقق")
        sales_tree.heading("method", text="طريقة الدفع")

        sales_tree.column("id", width=80, anchor="center")
        sales_tree.column("date", width=180, anchor="center")
        sales_tree.column("total", width=120, anchor="e")
        sales_tree.column("profit", width=120, anchor="e")
        sales_tree.column("method", width=100, anchor="center")

        sales_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.cursor.execute("SELECT id, date_vente, total_vente, total_profit, methode_paiement FROM sales ORDER BY id DESC LIMIT 30")
        for row in self.cursor.fetchall():
            sales_tree.insert("", "end", values=(row[0], row[1], f"{row[2]:.2f} DZD", f"{row[3]:.2f} DZD", row[4]))

if __name__ == "__main__":
    app = SuperPOSPro()
    app.mainloop()
