import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from datetime import datetime

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class SuperPOSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CarOps Auto - SUPER_POS لإدارة قطع غيار السيارات")
        self.geometry("1150x720")
        
        self.init_db()
        self.cart = []
        
        self.setup_ui()

    def init_db(self):
        self.conn = sqlite3.connect("super_pos.db")
        self.cursor = self.conn.cursor()
        
        # جدول المنتجات معدل ليشمل تفاصيل غيار السيارات (السيارة، المحرك، القطعة، السنة)
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
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # الشريط الجانبي (Sidebar)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        title_lbl = ctk.CTkLabel(self.sidebar, text="CarOps Auto", font=("Arial", 22, "bold"))
        title_lbl.pack(pady=20)

        self.btn_pos = ctk.CTkButton(self.sidebar, text="نقطة البيع (POS)", command=self.show_pos_tab)
        self.btn_pos.pack(pady=10, padx=15, fill="x")

        self.btn_products = ctk.CTkButton(self.sidebar, text="إضافة قطعة غيار", command=self.show_products_tab)
        self.btn_products.pack(pady=10, padx=15, fill="x")

        self.btn_reports = ctk.CTkButton(self.sidebar, text="التقارير والأرباح", command=self.show_reports_tab)
        self.btn_reports.pack(pady=10, padx=15, fill="x")

        # الحاوية الرئيسية (Main Container)
        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")

        self.show_pos_tab()

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # --- 1. قسم نقطة البيع (POS) ---
    def show_pos_tab(self):
        self.clear_container()

        left_frame = ctk.CTkFrame(self.main_container, width=380)
        left_frame.pack(side="left", fill="both", padx=10, pady=10)

        right_frame = ctk.CTkFrame(self.main_container)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # شريط البحث بالسيارة أو اسم القطعة أو المحرك أو الباركود
        search_lbl = ctk.CTkLabel(right_frame, text="بحث (اسم القطعة، السيارة، المحرك، أو الباركود):", font=("Arial", 14))
        search_lbl.pack(anchor="ne", padx=10, pady=5)

        self.barcode_entry = ctk.CTkEntry(right_frame, placeholder_text="ابحث بالباركود، اسم القطعة، الموديل، المحرك...")
        self.barcode_entry.pack(fill="x", padx=10, pady=5)
        self.barcode_entry.bind("<KeyRelease>", self.filter_products)

        # جدول عرض قطع الغيار
        columns = ("id", "barcode", "part_name", "car_model", "engine", "year", "prix", "stock")
        self.pos_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        self.pos_tree.heading("id", text="ID")
        self.pos_tree.heading("barcode", text="الباركود")
        self.pos_tree.heading("part_name", text="القطعة")
        self.pos_tree.heading("car_model", text="السيارة")
        self.pos_tree.heading("engine", text="المحرك")
        self.pos_tree.heading("year", text="العام")
        self.pos_tree.heading("prix", text="السعر (DZD)")
        self.pos_tree.heading("stock", text="المخزون")

        self.pos_tree.column("id", width=30)
        self.pos_tree.column("barcode", width=90)
        self.pos_tree.column("part_name", width=110)
        self.pos_tree.column("car_model", width=100)
        self.pos_tree.column("engine", width=80)
        self.pos_tree.column("year", width=50)
        self.pos_tree.column("prix", width=80)
        self.pos_tree.column("stock", width=60)

        self.pos_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_add_cart = ctk.CTkButton(right_frame, text="إضافة إلى السلة", command=self.add_selected_to_cart)
        btn_add_cart.pack(pady=5)

        # قسم سلة المشتريات
        ctk.CTkLabel(left_frame, text="سلة المشتريات", font=("Arial", 18, "bold")).pack(pady=10)

        self.cart_tree = ttk.Treeview(left_frame, columns=("name", "qty", "total"), show="headings", height=10)
        self.cart_tree.heading("name", text="القطعة / السيارة")
        self.cart_tree.heading("qty", text="الكمية")
        self.cart_tree.heading("total", text="المجموع")
        self.cart_tree.column("name", width=180)
        self.cart_tree.column("qty", width=50)
        self.cart_tree.column("total", width=90)
        self.cart_tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.lbl_total = ctk.CTkLabel(left_frame, text="الصافي: 0.00 DZD", font=("Arial", 16, "bold"), text_color="green")
        self.lbl_total.pack(pady=10)

        btn_pay = ctk.CTkButton(left_frame, text="دفع وطباعة", fg_color="green", font=("Arial", 16, "bold"), command=self.process_payment)
        btn_pay.pack(fill="x", padx=15, pady=10)

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

    def filter_products(self, event):
        query = self.barcode_entry.get().strip()
        self.load_pos_products(query)

    def add_selected_to_cart(self):
        selected = self.pos_tree.selection()
        if not selected:
            return
        item = self.pos_tree.item(selected[0])['values']
        
        if item[7] <= 0:
            messagebox.showerror("خطأ", "هذه القطعة غير متوفرة في المخزون!")
            return

        self.cursor.execute("SELECT prix_achat FROM products WHERE id = ?", (item[0],))
        pa = self.cursor.fetchone()[0]
        
        display_name = f"{item[2]} ({item[3]} {item[4]})"
        self.cart.append({'id': item[0], 'name': display_name, 'prix': item[6], 'prix_achat': pa, 'qty': 1})
        self.update_cart_display()

    def update_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        total = 0
        for item in self.cart:
            subtotal = item['prix'] * item['qty']
            total += subtotal
            self.cart_tree.insert("", "end", values=(item['name'], item['qty'], subtotal))
            
        self.lbl_total.configure(text=f"الصافي: {total:.2f} DZD")

    def process_payment(self):
        if not self.cart:
            messagebox.showwarning("تنبيه", "السلة فارغة!")
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
        messagebox.showinfo("نجاح", f"تم تسجيل الفاتورة بنجاح!\nالربح الصافي: {profit:.2f} DZD")
        self.cart.clear()
        self.update_cart_display()
        self.load_pos_products()

    # --- 2. قسم إدخال قطعة غيار جديدة ---
    def show_products_tab(self):
        self.clear_container()

        frame = ctk.CTkFrame(self.main_container)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="إضافة قطعة غيار جديدة", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=4, pady=15)

        # الحقول الخاصة بقطع غيار السيارات
        ctk.CTkLabel(frame, text="اسم القطعة (مثلاً: Démarreur, Alternateur):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        ent_part = ctk.CTkEntry(frame, width=200)
        ent_part.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="اسم / موديل السيارة (مثلاً: Golf 7, Symbol):").grid(row=1, column=2, padx=10, pady=10, sticky="e")
        ent_car = ctk.CTkEntry(frame, width=200)
        ent_car.grid(row=1, column=3, padx=10, pady=10)

        ctk.CTkLabel(frame, text="نوع المحرك (مثلاً: 2.0 TDI, 1.2 Essence):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        ent_engine = ctk.CTkEntry(frame, width=200)
        ent_engine.grid(row=2, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="العام / السنة (مثلاً: 2018):").grid(row=2, column=2, padx=10, pady=10, sticky="e")
        ent_year = ctk.CTkEntry(frame, width=200)
        ent_year.grid(row=2, column=3, padx=10, pady=10)

        ctk.CTkLabel(frame, text="الباركود (اختياري / ممسوح بالدوشة):").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        ent_bc = ctk.CTkEntry(frame, width=200)
        ent_bc.grid(row=3, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="الكمية بالحيّز:").grid(row=3, column=2, padx=10, pady=10, sticky="e")
        ent_stock = ctk.CTkEntry(frame, width=200)
        ent_stock.grid(row=3, column=3, padx=10, pady=10)

        ctk.CTkLabel(frame, text="سعر الشراء (DZD):").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        ent_pa = ctk.CTkEntry(frame, width=200)
        ent_pa.grid(row=4, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="سعر البيع (DZD):").grid(row=4, column=2, padx=10, pady=10, sticky="e")
        ent_pv = ctk.CTkEntry(frame, width=200)
        ent_pv.grid(row=4, column=3, padx=10, pady=10)

        def save_product():
            try:
                bc = ent_bc.get().strip()
                part = ent_part.get().strip()
                car = ent_car.get().strip()
                engine = ent_engine.get().strip()
                year = int(ent_year.get().strip()) if ent_year.get().strip() else 0
                pa = float(ent_pa.get())
                pv = float(ent_pv.get())
                stock = int(ent_stock.get())

                self.cursor.execute("""
                    INSERT INTO products (barcode, part_name, car_model, engine_type, year, prix_achat, prix_vente, stock) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (bc, part, car, engine, year, pa, pv, stock))
                
                self.conn.commit()
                messagebox.showinfo("نجاح", "تم حفظ قطعة الغيار بنجاح!")
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر الحفظ: {e}")

        btn_save = ctk.CTkButton(frame, text="حفظ القطعة", fg_color="green", font=("Arial", 16, "bold"), command=save_product)
        btn_save.grid(row=5, column=0, columnspan=4, pady=25)

    # --- 3. قسم التقارير والأرباح ---
    def show_reports_tab(self):
        self.clear_container()

        frame = ctk.CTkFrame(self.main_container)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="لوحة التقارير والأرباح", font=("Arial", 20, "bold")).pack(pady=15)

        self.cursor.execute("SELECT SUM(total_vente), SUM(total_profit), COUNT(id) FROM sales")
        res = self.cursor.fetchone()
        
        total_sales = res[0] if res[0] else 0.0
        total_profit = res[1] if res[1] else 0.0
        total_invoices = res[2] if res[2] else 0

        cards_frame = ctk.CTkFrame(frame)
        cards_frame.pack(fill="x", pady=20)

        card1 = ctk.CTkFrame(cards_frame, fg_color="#1F6AA5")
        card1.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(card1, text="المبيعات الإجمالية", font=("Arial", 14), text_color="white").pack(pady=5)
        ctk.CTkLabel(card1, text=f"{total_sales:.2f} DZD", font=("Arial", 18, "bold"), text_color="white").pack(pady=10)

        card2 = ctk.CTkFrame(cards_frame, fg_color="#2FA572")
        card2.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(card2, text="صافي الأرباح", font=("Arial", 14), text_color="white").pack(pady=5)
        ctk.CTkLabel(card2, text=f"{total_profit:.2f} DZD", font=("Arial", 18, "bold"), text_color="white").pack(pady=10)

        card3 = ctk.CTkFrame(cards_frame, fg_color="#E76E55")
        card3.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(card3, text="عدد الفواتير", font=("Arial", 14), text_color="white").pack(pady=5)
        ctk.CTkLabel(card3, text=str(total_invoices), font=("Arial", 18, "bold"), text_color="white").pack(pady=10)

if __name__ == "__main__":
    app = SuperPOSApp()
    app.mainloop()
