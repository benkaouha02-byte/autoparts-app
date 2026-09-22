import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from datetime import datetime, timedelta
import os

# استيراد Matplotlib لرسم المخططات البيانية
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
                                         fg_color="#1e66f5", hover_color="#45475a", anchor="w", command=self.show_reports_tab)
        self.btn_reports.pack(pady=8, padx=15, fill="x")

        self.btn_settings = ctk.CTkButton(self.sidebar, text="⚙️ الإعدادات", font=("Arial", 14, "bold"), 
                                          fg_color="#313244", hover_color="#45475a", anchor="w", command=self.show_settings_tab)
        self.btn_settings.pack(pady=8, padx=15, fill="x")

        # الحاوية الرئيسية
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#eff1f5")
        self.main_container.grid(row=0, column=1, sticky="nsew")

        self.show_reports_tab()

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # --- 1. قسم لوحة التقارير بالتصميم الجديد ---
    def show_reports_tab(self):
        self.clear_container()

        main_scroll = ctk.CTkScrollableFrame(self.main_container, fg_color="#f2f4f8")
        main_scroll.pack(fill="both", expand=True)

        # 1. الهيدر وأزرار التصفية السريعة (اليوم / هذا الأسبوع / هذا الشهر)
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

        # 2. شريط الفلاتر وأزرار التصدير
        filter_bar = ctk.CTkFrame(main_scroll, fg_color="#ffffff", corner_radius=8)
        filter_bar.pack(fill="x", padx=20, pady=10)

        # أزرار التصدير (يمين)
        btn_pdf = ctk.CTkButton(filter_bar, text="طباعة PDF", fg_color="#34495e", hover_color="#2c3e50", font=("Arial", 12, "bold"), width=90)
        btn_pdf.pack(side="left", padx=10, pady=10)

        btn_csv = ctk.CTkButton(filter_bar, text="تصدير CSV", fg_color="#27ae60", hover_color="#219150", font=("Arial", 12, "bold"), width=90)
        btn_csv.pack(side="left", padx=5, pady=10)

        btn_refresh = ctk.CTkButton(filter_bar, text="تحديث", fg_color="#2980b9", hover_color="#1f6391", font=("Arial", 12, "bold"), width=80, command=self.load_report_data)
        btn_refresh.pack(side="left", padx=10, pady=10)

        # الفلاتر (شمال)
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

        # 3. تبويبات الأقسام التوضيحية
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

        # 4. بطاقات المؤشرات الأربع الرئيسية
        cards_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)

        # المبيعات
        self.card_sales = ctk.CTkFrame(cards_frame, fg_color="#ffffff", corner_radius=8)
        self.card_sales.pack(side="right", expand=True, fill="both", padx=5)
        ctk.CTkLabel(self.card_sales, text="المبيعات", font=("Arial", 13, "bold"), text_color="#7f8c8d").pack(pady=(10, 5))
        self.lbl_sales_val = ctk.CTkLabel(self.card_sales, text="0.00", font=("Arial", 22, "bold"), text_color="#2980b9")
        self.lbl_sales_val.pack(pady=(0, 10))

        # الأرباح
        self.card_profit = ctk.CTkFrame(cards_frame, fg_color="#ffffff", corner_radius=8)
        self.card_profit.pack(side="right", expand=True, fill="both", padx=5)
        ctk.CTkLabel(self.card_profit, text="الأرباح", font=("Arial", 13, "bold"), text_color="#7f8c8d").pack(pady=(10, 5))
        self.lbl_profit_val = ctk.CTkLabel(self.card_profit, text="0.00", font=("Arial", 22, "bold"), text_color="#27ae60")
        self.lbl_profit_val.pack(pady=(0, 10))

        # الفواتير
        self.card_invoices = ctk.CTkFrame(cards_frame, fg_color="#ffffff", corner_radius=8)
        self.card_invoices.pack(side="right", expand=True, fill="both", padx=5)
        ctk.CTkLabel(self.card_invoices, text="الفواتير", font=("Arial", 13, "bold"), text_color="#7f8c8d").pack(pady=(10, 5))
        self.lbl_invoices_val = ctk.CTkLabel(self.card_invoices, text="0", font=("Arial", 22, "bold"), text_color="#2c3e50")
        self.lbl_invoices_val.pack(pady=(0, 10))

        # تنبيهات المخزون
        self.card_alerts = ctk.CTkFrame(cards_frame, fg_color="#ffffff", corner_radius=8)
        self.card_alerts.pack(side="right", expand=True, fill="both", padx=5)
        ctk.CTkLabel(self.card_alerts, text="تنبيهات المخزون", font=("Arial", 13, "bold"), text_color="#7f8c8d").pack(pady=(10, 5))
        self.lbl_alerts_val = ctk.CTkLabel(self.card_alerts, text="0", font=("Arial", 22, "bold"), text_color="#e74c3c")
        self.lbl_alerts_val.pack(pady=(0, 10))

        # 5. المخططات البيانية (الرسم الدائري والمبيعات)
        charts_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        charts_frame.pack(fill="x", padx=20, pady=10)

        # المخطط البياني الخطي / الشريطي (يمين)
        right_chart_box = ctk.CTkFrame(charts_frame, fg_color="#ffffff", corner_radius=8)
        right_chart_box.pack(side="right", expand=True, fill="both", padx=5)

        fig1, ax1 = plt.subplots(figsize=(6, 3), dpi=100)
        fig1.patch.set_facecolor('#ffffff')
        ax1.set_facecolor('#ffffff')
        
        # بيانات توضيحية للمبيعات
        days = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
        sales_data = [12000, 18000, 15000, 22000, 31000, 28000, 32450]
        
        ax1.plot(days, sales_data, marker='o', color='#2980b9', linewidth=2)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#cccccc')
        ax1.spines['bottom'].set_color('#cccccc')
        ax1.tick_params(colors='#555555', labelsize=8)
        ax1.set_title("المبيعات اليومية (DZD)", fontsize=10, color="#333333", pad=10)

        canvas1 = FigureCanvasTkAgg(fig1, master=right_chart_box)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # المخطط الدائري Donut Chart (شمال)
        left_chart_box = ctk.CTkFrame(charts_frame, fg_color="#ffffff", corner_radius=8, width=300)
        left_chart_box.pack(side="left", fill="both", padx=5)

        fig2, ax2 = plt.subplots(figsize=(3, 3), dpi=100)
        fig2.patch.set_facecolor('#ffffff')
        
        sizes = [100]
        colors = ['#2ecc71']
        
        wedges, _ = ax2.pie(sizes, colors=colors, startangle=90, wedgeprops=dict(width=0.4, edgecolor='w'))
        ax2.legend(wedges, ['غير تصنيف'], loc="upper center", bbox_to_anchor=(0.5, 1.15), frameon=False, fontsize=8)

        canvas2 = FigureCanvasTkAgg(fig2, master=left_chart_box)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.load_report_data()

    def load_report_data(self):
        """تحميل وتحديث قيم التقارير من قاعدة البيانات"""
        self.cursor.execute("SELECT SUM(total_vente), SUM(total_profit), COUNT(id) FROM sales")
        res = self.cursor.fetchone()
        
        total_sales = res[0] if res[0] else 0.0
        total_profit = res[1] if res[1] else 0.0
        total_invoices = res[2] if res[2] else 0

        # التنبيهات: القطع التي شارف مخزونها على الانتهاء (أقل من 3 قطع)
        self.cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= 3")
        alerts_count = self.cursor.fetchone()[0]

        self.lbl_sales_val.configure(text=f"{total_sales:.2f}")
        self.lbl_profit_val.configure(text=f"{total_profit:.2f}")
        self.lbl_invoices_val.configure(text=str(total_invoices))
        self.lbl_alerts_val.configure(text=str(alerts_count))

    def filter_reports_by_days(self, days_count):
        """تصفية المبيعات حسب عدد الأيام"""
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

    # --- باقي الأقسام ---
    def show_pos_tab(self):
        self.clear_container()
        lbl = ctk.CTkLabel(self.main_container, text="🛒 واجهة نقطة البيع", font=("Arial", 20, "bold"))
        lbl.pack(pady=20)

    def show_products_tab(self):
        self.clear_container()
        lbl = ctk.CTkLabel(self.main_container, text="📦 واجهة إدارة المنتجات والمخزون", font=("Arial", 20, "bold"))
        lbl.pack(pady=20)

    def show_settings_tab(self):
        self.clear_container()
        lbl = ctk.CTkLabel(self.main_container, text="⚙️ واجهة الإعدادات", font=("Arial", 20, "bold"))
        lbl.pack(pady=20)

if __name__ == "__main__":
    app = SuperPOSApp()
    app.mainloop()
