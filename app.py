import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SuperPOSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SUPER_POS - CarOps Auto")
        self.geometry("1200x750")
        
        self.init_db()
        self.cart = []
        self.setup_ui()

    def init_db(self):
        self.conn = sqlite3.connect("super_pos.db")
        self.cursor = self.conn.cursor()
        
        # جدول قطع الغيار
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
        
        self.conn.commit()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # الشريط الجانبي
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1e1e2e")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        title_lbl = ctk.CTkLabel(self.sidebar, text="SUPER_POS\nCarOps Auto", font=("Arial", 20, "bold"), text_color="#89b4fa")
        title_lbl.pack(pady=25)

        self.btn_pos = ctk.CTkButton(self.sidebar, text="🛒 نقطة البيع (POS)", font=("Arial", 14, "bold"), 
                                     fg_color="#313244", hover_color="#45475a", anchor="w", command=self.show_pos_tab)
        self.btn_pos.pack(pady=8, padx=15, fill="x")

        self.btn_products = ctk.CTkButton(self.sidebar, text="📦 إدارة المخزون", font=("Arial", 14, "bold"), 
                                          fg_color="#313244", hover_color="#45475a", anchor="w", command=self.show_products_tab)
        self.btn_products.pack(pady=8, padx=15, fill="x")

        self.btn_reports = ctk.CTkButton(self.sidebar, text="📊 التقارير والأرباح", font=("Arial", 14, "bold"), 
                                         fg_color="#313244", hover_color="#45475a", anchor="w", command=self.show_reports_tab)
        self.btn_reports.pack(pady=8, padx=15, fill="x")

        # الحاوية الرئيسية
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#181825")
        self.main_container.grid(row=0, column=1, sticky="nsew")

        self.show_pos_tab()

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # --- 1. قسم نقطة البيع (POS) ---
    def show_pos_tab(self):
        self.clear_container()

        left_frame = ctk.CTkFrame(self.main_container, width=380, fg_color="#1e1e2e")
        left_frame.pack(side="left", fill="both", padx=10, pady=10)

        right_frame = ctk.CTkFrame(self.main_container, fg_color="#1e1e2e")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(right_frame, text="البحث عن قطعة غيار:", font=("Arial", 14, "bold"), text_color="#cdd6f4").pack(anchor="ne", padx=10, pady=5)

        self.search_entry = ctk.CTkEntry(right_frame, placeholder_text="ابحث بالاسم، موديل السيارة، المحرك، أو الباركود...", font=("Arial", 13))
        self.search_entry.pack(fill="x", padx=10, pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_products)

        columns = ("id", "barcode", "part_name", "car_model", "engine", "year", "prix", "stock")
        self.pos_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        
        self.pos_tree.heading("id", text="ID")
        self.pos_tree.heading("barcode", text="الباركود")
        self.pos_tree.heading("part_name", text="القطعة")
        self.pos_tree.heading("car_model", text="السيارة")
        self.pos_tree.heading("engine", text="المحرك")
        self.pos_tree.heading("year", text="العام")
        self.pos_tree.heading("prix", text="السعر")
        self.pos_tree.heading("stock", text="المخزون")

        self.pos_tree.column("id", width=30)
        self.pos_tree.column("barcode", width=80)
        self.pos_tree.column("part_name", width=110)
        self.pos_tree.column("car_model", width=90)
        self.pos_tree.column("engine", width=80)
        self.pos_tree.column("year", width=50)
        self.pos_tree.column("prix", width=70)
        self.pos_tree.column("stock", width=60)

        self.pos_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_add = ctk.CTkButton(right_frame, text="➕ إضافة القطعة لسلة البيع", font=("Arial", 14, "bold"), 
                                fg_color="#89b4fa", text_color="#11111b", hover_color="#b4befe", command=self.add_selected_to_cart)
        btn_add.pack(pady=8)

        # سلة المشتريات
        ctk.CTkLabel(left_frame, text="🛒 سلة المشتريات", font=("Arial", 16, "bold"), text_color="#cdd6f4").pack(pady=10)

        self.cart_tree = ttk.Treeview(left_frame, columns=("name", "qty", "total"), show="headings", height=12)
        self.cart_tree.heading("name", text="القطعة / السيارة")
        self.cart_tree.heading("qty", text="الكمية")
        self.cart_tree.heading("total", text="المجموع")
        self.cart_tree.column("name", width=170)
        self.cart_tree.column("qty", width=50)
        self.cart_tree.column("total", width=80)
        self.cart_tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.lbl_total = ctk.CTkLabel(left_frame, text="الإجمالي: 0.00 DZD", font=("Arial", 16, "bold"), text_color="#a6e3a1")
        self.lbl_total.pack(pady=10)

        btn_pay = ctk.CTkButton(left_frame, text="💳 إتمام البيع وطباعة الفاتورة", fg_color="#a6e3a1", text_color="#11111b", 
                                font=("Arial", 15, "bold"), hover_color="#94e2d5", command=self.process_payment)
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
        self.load_pos_products(self.search_entry.get().strip())

    def add_selected_to_cart(self):
        selected = self.pos_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى تحديد قطعة من الجدول أولاً!")
            return
            
        item = self.pos_tree.item(selected[0])['values']
        
        prod_id = int(item[0])
        part_name = str(item[2])
        car_model = str(item[3])
        engine = str(item[4])
        prix_vente = float(item[6])
        stock = int(item[7])
        
        if stock <= 0:
            messagebox.showerror("خطأ", "القطعة غير متوفرة في المخزون! يرجى إعادة شحن المخزون أولاً.")
            return

        self.cursor.execute("SELECT prix_achat FROM products WHERE id = ?", (prod_id,))
        res = self.cursor.fetchone()
        pa = res[0] if res else 0.0
        
        display_name = f"{part_name} ({car_model} {engine})"
        
        for cart_item in self.cart:
            if cart_item['id'] == prod_id:
                if cart_item['qty'] + 1 > stock:
                    messagebox.showwarning("تنبيه", "الكمية المطلوبة تتجاوز المخزون المتاح!")
                    return
                cart_item['qty'] += 1
                self.update_cart_display()
                return

        self.cart.append({'id': prod_id, 'name': display_name, 'prix': prix_vente, 'prix_achat': pa, 'qty': 1})
        self.update_cart_display()

    def update_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        total = 0
        for item in self.cart:
            subtotal = item['prix'] * item['qty']
            total += subtotal
            self.cart_tree.insert("", "end", values=(item['name'], item['qty'], f"{subtotal:.2f}"))
            
        self.lbl_total.configure(text=f"الإجمالي: {total:.2f} DZD")

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

        for item in self.cart:
            self.cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item['qty'], item['id']))

        self.conn.commit()
        messagebox.showinfo("نجاح العملية", f"تم التسجيل بنجاح!\nالربح المحقق: {profit:.2f} DZD")
        self.cart.clear()
        self.update_cart_display()
        self.load_pos_products()

    # --- 2. قسم إدارة المخزون ---
    def show_products_tab(self):
        self.clear_container()

        top_frame = ctk.CTkFrame(self.main_container, fg_color="#1e1e2e")
        top_frame.pack(fill="x", padx=15, pady=10)

        bottom_frame = ctk.CTkFrame(self.main_container, fg_color="#1e1e2e")
        bottom_frame.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(top_frame, text="📦 إضافة / تحديث قطعة غيار بالمخزون", font=("Arial", 16, "bold"), text_color="#cdd6f4").grid(row=0, column=0, columnspan=4, pady=10)

        ctk.CTkLabel(top_frame, text="اسم القطعة:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        ent_part = ctk.CTkEntry(top_frame, width=180, placeholder_text="Démarreur")
        ent_part.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="السيارة:").grid(row=1, column=2, padx=10, pady=5, sticky="e")
        ent_car = ctk.CTkEntry(top_frame, width=180, placeholder_text="Golf 7")
        ent_car.grid(row=1, column=3, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="المحرك:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        ent_engine = ctk.CTkEntry(top_frame, width=180, placeholder_text="2.0 TDI")
        ent_engine.grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="العام:").grid(row=2, column=2, padx=10, pady=5, sticky="e")
        ent_year = ctk.CTkEntry(top_frame, width=180, placeholder_text="2018")
        ent_year.grid(row=2, column=3, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="الباركود:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        ent_bc = ctk.CTkEntry(top_frame, width=180)
        ent_bc.grid(row=3, column=1, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="الكمية المضافة:").grid(row=3, column=2, padx=10, pady=5, sticky="e")
        ent_stock = ctk.CTkEntry(top_frame, width=180)
        ent_stock.grid(row=3, column=3, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="سعر الشراء:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        ent_pa = ctk.CTkEntry(top_frame, width=180)
        ent_pa.grid(row=4, column=1, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="سعر البيع:").grid(row=4, column=2, padx=10, pady=5, sticky="e")
        ent_pv = ctk.CTkEntry(top_frame, width=180)
        ent_pv.grid(row=4, column=3, padx=10, pady=5)

        def save_or_update_product():
            try:
                bc = ent_bc.get().strip()
                part = ent_part.get().strip()
                car = ent_car.get().strip()
                engine = ent_engine.get().strip()
                year = int(ent_year.get().strip()) if ent_year.get().strip() else 0
                pa = float(ent_pa.get())
                pv = float(ent_pv.get())
                add_qty = int(ent_stock.get())

                self.cursor.execute("""
                    SELECT id, stock FROM products 
                    WHERE (barcode != '' AND barcode = ?) OR (part_name = ? AND car_model = ? AND engine_type = ?)
                """, (bc, part, car, engine))
                existing = self.cursor.fetchone()

                if existing:
                    prod_id, current_stock = existing
                    new_stock = current_stock + add_qty
                    self.cursor.execute("""
                        UPDATE products 
                        SET stock = ?, prix_achat = ?, prix_vente = ?
                        WHERE id = ?
                    """, (new_stock, pa, pv, prod_id))
                    messagebox.showinfo("تحديث", f"تمت زيادة مخزون القطعة بنجاح!\nالكمية الجديدة: {new_stock}")
                else:
                    self.cursor.execute("""
                        INSERT INTO products (barcode, part_name, car_model, engine_type, year, prix_achat, prix_vente, stock) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (bc, part, car, engine, year, pa, pv, add_qty))
                    messagebox.showinfo("نجاح", "تم حفظ القطعة الجديدة بالمخزون!")

                self.conn.commit()
                load_manage_products()
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر الحفظ: {e}")

        btn_save = ctk.CTkButton(top_frame, text="حفظ / زيادة المخزون", fg_color="#a6e3a1", text_color="#11111b", 
                                font=("Arial", 14, "bold"), hover_color="#94e2d5", command=save_or_update_product)
        btn_save.grid(row=5, column=0, columnspan=4, pady=15)

        ctk.CTkLabel(bottom_frame, text="قائمة المخزون الحالية - تعديل شحن الكميات المنتهية", font=("Arial", 14, "bold"), text_color="#cdd6f4").pack(pady=5)

        columns = ("id", "part_name", "car_model", "engine", "year", "prix_vente", "stock")
        manage_tree = ttk.Treeview(bottom_frame, columns=columns, show="headings", height=8)
        
        manage_tree.heading("id", text="ID")
        manage_tree.heading("part_name", text="القطعة")
        manage_tree.heading("car_model", text="السيارة")
        manage_tree.heading("engine", text="المحرك")
        manage_tree.heading("year", text="العام")
        manage_tree.heading("prix_vente", text="سعر البيع")
        manage_tree.heading("stock", text="المخزون الحالي")

        manage_tree.pack(fill="both", expand=True, padx=10, pady=5)

        def load_manage_products():
            for item in manage_tree.get_children():
                manage_tree.delete(item)
            self.cursor.execute("SELECT id, part_name, car_model, engine_type, year, prix_vente, stock FROM products")
            for row in self.cursor.fetchall():
                manage_tree.insert("", "end", values=row)

        quick_edit_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        quick_edit_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(quick_edit_frame, text="إعادة شحن سريعة للقطعة المحددة:").pack(side="right", padx=10)
        ent_quick_qty = ctk.CTkEntry(quick_edit_frame, width=100, placeholder_text="+الكمية")
        ent_quick_qty.pack(side="right", padx=5)

        def quick_add_stock():
            selected = manage_tree.selection()
            if not selected:
                messagebox.showwarning("تنبيه", "يرجى تحديد قطعة من الجدول أولاً!")
                return
            try:
                qty_to_add = int(ent_quick_qty.get().strip())
                item = manage_tree.item(selected[0])['values']
                prod_id = item[0]

                self.cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty_to_add, prod_id))
                self.conn.commit()
                messagebox.showinfo("نجاح", "تم تحديث كمية المخزون بنجاح!")
                load_manage_products()
            except Exception as e:
                messagebox.showerror("خطأ", f"ادخل كمية صحيحة: {e}")

        btn_quick_add = ctk.CTkButton(quick_edit_frame, text="تحديث الكمية", fg_color="#89b4fa", text_color="#11111b", font=("Arial", 12, "bold"), command=quick_add_stock)
        btn_quick_add.pack(side="right", padx=10)

        load_manage_products()

    # --- 3. قسم التقارير والأرباح ---
    def show_reports_tab(self):
        self.clear_container()

        frame = ctk.CTkFrame(self.main_container, fg_color="#1e1e2e")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="📊 لوحة الإحصائيات والأرباح", font=("Arial", 18, "bold"), text_color="#cdd6f4").pack(pady=15)

        self.cursor.execute("SELECT SUM(total_vente), SUM(total_profit), COUNT(id) FROM sales")
        res = self.cursor.fetchone()
        
        total_sales = res[0] if res[0] else 0.0
        total_profit = res[1] if res[1] else 0.0
        total_invoices = res[2] if res[2] else 0

        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=20)

        card1 = ctk.CTkFrame(cards_frame, fg_color="#313244", corner_radius=10)
        card1.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(card1, text="إجمالي رقم الأعمال", font=("Arial", 13), text_color="#a6adc8").pack(pady=5)
        ctk.CTkLabel(card1, text=f"{total_sales:.2f} DZD", font=("Arial", 18, "bold"), text_color="#89b4fa").pack(pady=10)

        card2 = ctk.CTkFrame(cards_frame, fg_color="#313244", corner_radius=10)
        card2.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(card2, text="صافي الأرباح", font=("Arial", 13), text_color="#a6adc8").pack(pady=5)
        ctk.CTkLabel(card2, text=f"{total_profit:.2f} DZD", font=("Arial", 18, "bold"), text_color="#a6e3a1").pack(pady=10)

        card3 = ctk.CTkFrame(cards_frame, fg_color="#313244", corner_radius=10)
        card3.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(card3, text="عدد الفواتير المكتملة", font=("Arial", 13), text_color="#a6adc8").pack(pady=5)
        ctk.CTkLabel(card3, text=str(total_invoices), font=("Arial", 18, "bold"), text_color="#f38ba8").pack(pady=10)

if __name__ == "__main__":
    app = SuperPOSApp()
    app.mainloop()
