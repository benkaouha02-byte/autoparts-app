import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PhoneShopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SUPER_POS - إدارة تجارة الهواتف النقالة")
        self.geometry("1250x780")
        
        self.init_db()
        self.setup_ui()

    def init_db(self):
        self.conn = sqlite3.connect("phone_shop.db")
        self.cursor = self.conn.cursor()
        
        # جدول الهواتف
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS phones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_name TEXT,
                buy_price REAL,
                sell_price REAL,
                is_paid TEXT,
                date_added TEXT
            )
        ''')
        
        # جدول المصاريف
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                amount REAL,
                date_exp TEXT
            )
        ''')
        self.conn.commit()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # الشريط الجانبي (Sidebar)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1e1e2e")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        title_lbl = ctk.CTkLabel(self.sidebar, text="PHONE_POS\nإدارة الهواتف", font=("Arial", 18, "bold"), text_color="#89b4fa")
        title_lbl.pack(pady=25)

        self.btn_phones = ctk.CTkButton(self.sidebar, text="📱 الهواتف والمخزون", font=("Arial", 14, "bold"), 
                                        fg_color="#1e66f5", hover_color="#45475a", anchor="w", command=self.show_phones_tab)
        self.btn_phones.pack(pady=8, padx=15, fill="x")

        self.btn_expenses = ctk.CTkButton(self.sidebar, text="💸 المصاريف", font=("Arial", 14, "bold"), 
                                          fg_color="#313244", hover_color="#45475a", anchor="w", command=self.show_expenses_tab)
        self.btn_expenses.pack(pady=8, padx=15, fill="x")

        self.btn_reports = ctk.CTkButton(self.sidebar, text="📊 الأرباح والتقارير", font=("Arial", 14, "bold"), 
                                         fg_color="#313244", hover_color="#45475a", anchor="w", command=self.show_reports_tab)
        self.btn_reports.pack(pady=8, padx=15, fill="x")

        # الحاوية الرئيسية
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#181825")
        self.main_container.grid(row=0, column=1, sticky="nsew")

        self.show_phones_tab()

    def update_sidebar_buttons(self, active_btn):
        for btn in [self.btn_phones, self.btn_expenses, self.btn_reports]:
            btn.configure(fg_color="#313244")
        active_btn.configure(fg_color="#1e66f5")

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # --- 1. قسم إدارة الهواتف ---
    def show_phones_tab(self):
        self.update_sidebar_buttons(self.btn_phones)
        self.clear_container()

        top_frame = ctk.CTkFrame(self.main_container, fg_color="#1e1e2e")
        top_frame.pack(fill="x", padx=15, pady=10)

        bottom_frame = ctk.CTkFrame(self.main_container, fg_color="#1e1e2e")
        bottom_frame.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(top_frame, text="📱 تسجيل هاتف جديد", font=("Arial", 16, "bold"), text_color="#cdd6f4").grid(row=0, column=0, columnspan=4, pady=10)

        ctk.CTkLabel(top_frame, text="اسم ومواصفات الهاتف:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        ent_name = ctk.CTkEntry(top_frame, width=220, placeholder_text="iPhone 11 / Samsung A52")
        ent_name.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="سعر الشراء (رأس المال):").grid(row=1, column=2, padx=10, pady=5, sticky="e")
        ent_buy = ctk.CTkEntry(top_frame, width=220, placeholder_text="0.00")
        ent_buy.grid(row=1, column=3, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="سعر البيع:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        ent_sell = ctk.CTkEntry(top_frame, width=220, placeholder_text="0.00")
        ent_sell.grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="حالة الدفع:").grid(row=2, column=2, padx=10, pady=5, sticky="e")
        combo_paid = ctk.CTkComboBox(top_frame, values=["مدفوع", "غير مدفوع"], width=220)
        combo_paid.grid(row=2, column=3, padx=10, pady=5)
        combo_paid.set("مدفوع")

        def save_phone():
            try:
                name = ent_name.get().strip()
                buy = float(ent_buy.get().strip())
                sell = float(ent_sell.get().strip())
                is_paid = combo_paid.get()
                date_now = datetime.now().strftime("%Y-%m-%d")

                if not name:
                    messagebox.showwarning("تنبيه", "يرجى إدخال اسم الهاتف!")
                    return

                self.cursor.execute("INSERT INTO phones (phone_name, buy_price, sell_price, is_paid, date_added) VALUES (?, ?, ?, ?, ?)",
                                    (name, buy, sell, is_paid, date_now))
                self.conn.commit()
                messagebox.showinfo("نجاح", "تم تسجيل الهاتف بنجاح!")
                
                ent_name.delete(0, 'end')
                ent_buy.delete(0, 'end')
                ent_sell.delete(0, 'end')
                load_phones()
            except Exception as e:
                messagebox.showerror("خطأ", f"تأكد من صحة الأرقام المدخلة: {e}")

        btn_save = ctk.CTkButton(top_frame, text="➕ إضافة الهاتف للحسابات", fg_color="#a6e3a1", text_color="#11111b", 
                                font=("Arial", 14, "bold"), hover_color="#94e2d5", command=save_phone)
        btn_save.grid(row=3, column=0, columnspan=4, pady=15)

        # جدول الهواتف المسجلة
        columns = ("id", "name", "buy", "sell", "profit", "paid", "date")
        phones_tree = ttk.Treeview(bottom_frame, columns=columns, show="headings", height=12)
        
        phones_tree.heading("id", text="ID")
        phones_tree.heading("name", text="الهاتف والمواصفات")
        phones_tree.heading("buy", text="سعر الشراء")
        phones_tree.heading("sell", text="سعر البيع")
        phones_tree.heading("profit", text="الفائدة (الربح)")
        phones_tree.heading("paid", text="حالة الدفع")
        phones_tree.heading("date", text="التاريخ")

        phones_tree.column("id", width=40)
        phones_tree.column("name", width=220)
        phones_tree.column("buy", width=100)
        phones_tree.column("sell", width=100)
        phones_tree.column("profit", width=100)
        phones_tree.column("paid", width=90)
        phones_tree.column("date", width=100)

        phones_tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load_phones():
            for item in phones_tree.get_children():
                phones_tree.delete(item)
            self.cursor.execute("SELECT id, phone_name, buy_price, sell_price, is_paid, date_added FROM phones ORDER BY id DESC")
            for row in self.cursor.fetchall():
                p_id, name, buy, sell, paid, date = row
                profit = sell - buy
                phones_tree.insert("", "end", values=(p_id, name, f"{buy:.2f}", f"{sell:.2f}", f"{profit:.2f}", paid, date))

        def delete_phone():
            selected = phones_tree.selection()
            if not selected:
                messagebox.showwarning("تنبيه", "يرجى تحديد هاتف للحذف!")
                return
            item = phones_tree.item(selected[0])['values']
            p_id = item[0]
            if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا السجل؟"):
                self.cursor.execute("DELETE FROM phones WHERE id = ?", (p_id,))
                self.conn.commit()
                load_phones()

        btn_del = ctk.CTkButton(bottom_frame, text="🗑️ حذف الهاتف المحدد", fg_color="#f38ba8", text_color="#11111b", 
                                font=("Arial", 12, "bold"), hover_color="#e35b78", command=delete_phone)
        btn_del.pack(pady=5)

        load_phones()

    # --- 2. قسم المصاريف ---
    def show_expenses_tab(self):
        self.update_sidebar_buttons(self.btn_expenses)
        self.clear_container()

        top_frame = ctk.CTkFrame(self.main_container, fg_color="#1e1e2e")
        top_frame.pack(fill="x", padx=15, pady=10)

        bottom_frame = ctk.CTkFrame(self.main_container, fg_color="#1e1e2e")
        bottom_frame.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(top_frame, text="💸 تسجيل مصروف جديد (أكل، نقل، صيانة...)", font=("Arial", 16, "bold"), text_color="#cdd6f4").grid(row=0, column=0, columnspan=4, pady=10)

        ctk.CTkLabel(top_frame, text="بيان المصروف:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        ent_title = ctk.CTkEntry(top_frame, width=250, placeholder_text="مثال: مصاريف طريق / أكل")
        ent_title.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(top_frame, text="المبلغ:").grid(row=1, column=2, padx=10, pady=5, sticky="e")
        ent_amount = ctk.CTkEntry(top_frame, width=200, placeholder_text="0.00")
        ent_amount.grid(row=1, column=3, padx=10, pady=5)

        def save_expense():
            try:
                title = ent_title.get().strip()
                amount = float(ent_amount.get().strip())
                date_now = datetime.now().strftime("%Y-%m-%d")

                if not title:
                    messagebox.showwarning("تنبيه", "يرجى إدخال بيان المصروف!")
                    return

                self.cursor.execute("INSERT INTO expenses (title, amount, date_exp) VALUES (?, ?, ?)", (title, amount, date_now))
                self.conn.commit()
                messagebox.showinfo("نجاح", "تم تسجيل المصروف بنجاح!")
                ent_title.delete(0, 'end')
                ent_amount.delete(0, 'end')
                load_expenses()
            except Exception as e:
                messagebox.showerror("خطأ", f"أدخل مبلغاً صحيحاً: {e}")

        btn_save_exp = ctk.CTkButton(top_frame, text="تسجيل المصروف", fg_color="#fab387", text_color="#11111b", 
                                     font=("Arial", 14, "bold"), hover_color="#f9e2af", command=save_expense)
        btn_save_exp.grid(row=2, column=0, columnspan=4, pady=15)

        columns = ("id", "title", "amount", "date")
        exp_tree = ttk.Treeview(bottom_frame, columns=columns, show="headings", height=12)
        exp_tree.heading("id", text="ID")
        exp_tree.heading("title", text="البيان")
        exp_tree.heading("amount", text="المبلغ")
        exp_tree.heading("date", text="التاريخ")
        exp_tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load_expenses():
            for item in exp_tree.get_children():
                exp_tree.delete(item)
            self.cursor.execute("SELECT id, title, amount, date_exp FROM expenses ORDER BY id DESC")
            for row in self.cursor.fetchall():
                exp_tree.insert("", "end", values=row)

        load_expenses()

    # --- 3. قسم التقارير والأرباح المالية ---
    def show_reports_tab(self):
        self.update_sidebar_buttons(self.btn_reports)
        self.clear_container()

        frame = ctk.CTkFrame(self.main_container, fg_color="#1e1e2e")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="📊 لوحة الحسابات ورأس المال والفوائد", font=("Arial", 20, "bold"), text_color="#cdd6f4").pack(pady=15)

        # حساب البيانات من قاعدة البيانات
        self.cursor.execute("SELECT SUM(buy_price), SUM(sell_price) FROM phones")
        p_res = self.cursor.fetchone()
        total_buy = p_res[0] if p_res[0] else 0.0
        total_sell = p_res[1] if p_res[1] else 0.0
        
        # إجمالي الفوائد قبل المصاريف
        total_gross_profit = total_sell - total_buy

        # حساب المصاريف الإجمالية
        self.cursor.execute("SELECT SUM(amount) FROM expenses")
        e_res = self.cursor.fetchone()
        total_expenses = e_res[0] if e_res[0] else 0.0

        # صافي الربح الحقيقي بعد خصم المصاريف
        net_profit = total_gross_profit - total_expenses

        # تصميم البطاقات المالية
        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=20)

        # رأس المال
        c1 = ctk.CTkFrame(cards_frame, fg_color="#313244", corner_radius=10)
        c1.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(c1, text="إجمالي رأس المال (الشراء)", font=("Arial", 13), text_color="#a6adc8").pack(pady=5)
        ctk.CTkLabel(c1, text=f"{total_buy:.2f} DZD", font=("Arial", 18, "bold"), text_color="#89b4fa").pack(pady=10)

        # الفائدة وحدها
        c2 = ctk.CTkFrame(cards_frame, fg_color="#313244", corner_radius=10)
        c2.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(c2, text="إجمالي الفوائد (الأرباح الخام)", font=("Arial", 13), text_color="#a6adc8").pack(pady=5)
        ctk.CTkLabel(c2, text=f"{total_gross_profit:.2f} DZD", font=("Arial", 18, "bold"), text_color="#a6e3a1").pack(pady=10)

        # المصاريف
        c3 = ctk.CTkFrame(cards_frame, fg_color="#313244", corner_radius=10)
        c3.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(c3, text="إجمالي المصاريف", font=("Arial", 13), text_color="#a6adc8").pack(pady=5)
        ctk.CTkLabel(c3, text=f"- {total_expenses:.2f} DZD", font=("Arial", 18, "bold"), text_color="#fab387").pack(pady=10)

        # صافي الربح الحقيقي
        c4 = ctk.CTkFrame(cards_frame, fg_color="#313244", corner_radius=10)
        c4.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(c4, text="صافي الربح (بعد المصاريف)", font=("Arial", 13), text_color="#a6adc8").pack(pady=5)
        ctk.CTkLabel(c4, text=f"{net_profit:.2f} DZD", font=("Arial", 18, "bold"), text_color="#f38ba8").pack(pady=10)

        # ملخص حالة الدفع (مدفوع / غير مدفوع)
        self.cursor.execute("SELECT SUM(sell_price) FROM phones WHERE is_paid = 'مدفوع'")
        paid_res = self.cursor.fetchone()[0]
        paid_total = paid_res if paid_res else 0.0

        self.cursor.execute("SELECT SUM(sell_price) FROM phones WHERE is_paid = 'غير مدفوع'")
        unpaid_res = self.cursor.fetchone()[0]
        unpaid_total = unpaid_res if unpaid_res else 0.0

        status_frame = ctk.CTkFrame(frame, fg_color="#313244", corner_radius=10)
        status_frame.pack(fill="x", padx=10, pady=20)
        
        ctk.CTkLabel(status_frame, text=f"💰 الأموال المدفوعة الفعليّة: {paid_total:.2f} DZD    |    ⚠️ الأموال المعلقة (غير المدفوعة): {unpaid_total:.2f} DZD", 
                     font=("Arial", 14, "bold"), text_color="#cdd6f4").pack(pady=15)

if __name__ == "__main__":
    app = PhoneShopApp()
    app.mainloop()
