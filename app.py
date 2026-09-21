import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AutoPartsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestion de Stock & Ventes - Pièces Auto")
        self.geometry("1100x700")
        self.init_db()
        self.cart = []
        self.create_widgets()

    def init_db(self):
        self.conn = sqlite3.connect("autoparts.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pieces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT UNIQUE,
                nom TEXT,
                prix_achat REAL,
                prix_vente REAL,
                quantite INTEGER,
                emplacement TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS compatibilites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                piece_id INTEGER,
                marque TEXT,
                modele TEXT,
                moteur TEXT,
                annee INTEGER,
                FOREIGN KEY (piece_id) REFERENCES pieces (id)
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_search = self.tabview.add("Recherche & Vente")
        self.tab_add = self.tabview.add("Ajouter Pièce / Compatibilité")
        self.setup_search_tab()
        self.setup_add_tab()

    def setup_search_tab(self):
        search_frame = ctk.CTkFrame(self.tab_search)
        search_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(search_frame, text="Marque:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_search_marque = ctk.CTkEntry(search_frame, placeholder_text="ex: Renault")
        self.entry_search_marque.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(search_frame, text="Modèle:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_search_modele = ctk.CTkEntry(search_frame, placeholder_text="ex: Symbol")
        self.entry_search_modele.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(search_frame, text="Moteur:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_search_moteur = ctk.CTkEntry(search_frame, placeholder_text="ex: 1.2 16V")
        self.entry_search_moteur.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(search_frame, text="Année:").grid(row=1, column=2, padx=5, pady=5)
        self.entry_search_annee = ctk.CTkEntry(search_frame, placeholder_text="ex: 2015")
        self.entry_search_annee.grid(row=1, column=3, padx=5, pady=5)

        btn_search = ctk.CTkButton(search_frame, text="Rechercher", command=self.rechercher_pieces)
        btn_search.grid(row=0, column=4, rowspan=2, padx=15, pady=5)

        result_frame = ctk.CTkFrame(self.tab_search)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "reference", "nom", "prix", "quantite", "emplacement")
        self.tree_results = ttk.Treeview(result_frame, columns=columns, show="headings")
        self.tree_results.heading("id", text="ID")
        self.tree_results.heading("reference", text="Référence")
        self.tree_results.heading("nom", text="Nom de Pièce")
        self.tree_results.heading("prix", text="Prix Vente (DZD)")
        self.tree_results.heading("quantite", text="En Stock")
        self.tree_results.heading("emplacement", text="Emplacement")
        self.tree_results.column("id", width=40)
        self.tree_results.pack(fill="both", expand=True, side="left")

        action_frame = ctk.CTkFrame(self.tab_search)
        action_frame.pack(fill="x", padx=10, pady=10)

        btn_add_cart = ctk.CTkButton(action_frame, text="Ajouter au Panier", command=self.ajouter_panier)
        btn_add_cart.pack(side="left", padx=10)

        btn_checkout = ctk.CTkButton(action_frame, text="Valider & Imprimer", fg_color="green", command=self.valider_vente)
        btn_checkout.pack(side="right", padx=10)

    def rechercher_pieces(self):
        for item in self.tree_results.get_children():
            self.tree_results.delete(item)

        marque = self.entry_search_marque.get().strip()
        modele = self.entry_search_modele.get().strip()
        moteur = self.entry_search_moteur.get().strip()
        annee = self.entry_search_annee.get().strip()

        query = '''
            SELECT DISTINCT p.id, p.reference, p.nom, p.prix_vente, p.quantite, p.emplacement 
            FROM pieces p
            JOIN compatibilites c ON p.id = c.piece_id
            WHERE 1=1
        '''
        params = []
        if marque:
            query += " AND c.marque LIKE ?"
            params.append(f"%{marque}%")
        if modele:
            query += " AND c.modele LIKE ?"
            params.append(f"%{modele}%")
        if moteur:
            query += " AND c.moteur LIKE ?"
            params.append(f"%{moteur}%")
        if annee:
            query += " AND c.annee = ?"
            params.append(annee)

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree_results.insert("", "end", values=row)

    def ajouter_panier(self):
        selected = self.tree_results.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une pièce.")
            return
        item = self.tree_results.item(selected[0])
        values = item['values']
        if values[4] <= 0:
            messagebox.showerror("Erreur", "Stock épuisé pour cette pièce!")
            return
        self.cart.append(values)
        messagebox.showinfo("Panier", f"Pièce '{values[2]}' ajoutée au panier.")

    def valider_vente(self):
        if not self.cart:
            messagebox.showwarning("Panier Vide", "Aucune pièce dans le panier.")
            return

        choice_window = ctk.CTkToplevel(self)
        choice_window.title("Format d'impression")
        choice_window.geometry("350x180")
        choice_window.grab_set()

        ctk.CTkLabel(choice_window, text="Choisissez le format d'impression:").pack(pady=15)

        def traiter_impression(fmt):
            for item in self.cart:
                piece_id = item[0]
                self.cursor.execute("UPDATE pieces SET quantite = quantite - 1 WHERE id = ?", (piece_id,))
            self.conn.commit()

            messagebox.showinfo("Succès", f"Vente enregistrée! Impression au format [{fmt}] en cours...")
            self.cart.clear()
            choice_window.destroy()
            self.rechercher_pieces()

        ctk.CTkButton(choice_window, text="Ticket de Caisse (80mm)", command=lambda: traiter_impression("Ticket 80mm")).pack(pady=5)
        ctk.CTkButton(choice_window, text="Facture Papier (A4 / A5)", command=lambda: traiter_impression("A4/A5")).pack(pady=5)

    def setup_add_tab(self):
        frame = ctk.CTkFrame(self.tab_add)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Référence:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_ref = ctk.CTkEntry(frame)
        self.ent_ref.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Nom de Pièce:").grid(row=0, column=2, padx=5, pady=5)
        self.ent_nom = ctk.CTkEntry(frame)
        self.ent_nom.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Prix Achat:").grid(row=1, column=0, padx=5, pady=5)
        self.ent_p_achat = ctk.CTkEntry(frame)
        self.ent_p_achat.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Prix Vente:").grid(row=1, column=2, padx=5, pady=5)
        self.ent_p_vente = ctk.CTkEntry(frame)
        self.ent_p_vente.grid(row=1, column=3, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Quantité Initial:").grid(row=2, column=0, padx=5, pady=5)
        self.ent_qty = ctk.CTkEntry(frame)
        self.ent_qty.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Emplacement (Rayon):").grid(row=2, column=2, padx=5, pady=5)
        self.ent_loc = ctk.CTkEntry(frame)
        self.ent_loc.grid(row=2, column=3, padx=5, pady=5)

        ctk.CTkLabel(frame, text="--- Compatibilité Véhicule ---", font=("Arial", 14, "bold")).grid(row=3, column=0, columnspan=4, pady=15)

        ctk.CTkLabel(frame, text="Marque:").grid(row=4, column=0, padx=5, pady=5)
        self.ent_c_marque = ctk.CTkEntry(frame)
        self.ent_c_marque.grid(row=4, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Modèle:").grid(row=4, column=2, padx=5, pady=5)
        self.ent_c_modele = ctk.CTkEntry(frame)
        self.ent_c_modele.grid(row=4, column=3, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Moteur:").grid(row=5, column=0, padx=5, pady=5)
        self.ent_c_moteur = ctk.CTkEntry(frame)
        self.ent_c_moteur.grid(row=5, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Année:").grid(row=5, column=2, padx=5, pady=5)
        self.ent_c_annee = ctk.CTkEntry(frame)
        self.ent_c_annee.grid(row=5, column=3, padx=5, pady=5)

        btn_save = ctk.CTkButton(frame, text="Enregistrer Pièce et Compatibilité", fg_color="green", command=self.sauvegarder_piece)
        btn_save.grid(row=6, column=0, columnspan=4, pady=20)

    def sauvegarder_piece(self):
        try:
            ref = self.ent_ref.get().strip()
            nom = self.ent_nom.get().strip()
            pa = float(self.ent_p_achat.get())
            pv = float(self.ent_p_vente.get())
            qty = int(self.ent_qty.get())
            loc = self.ent_loc.get().strip()

            marque = self.ent_c_marque.get().strip()
            modele = self.ent_c_modele.get().strip()
            moteur = self.ent_c_moteur.get().strip()
            annee = int(self.ent_c_annee.get())

            self.cursor.execute('''
                INSERT INTO pieces (reference, nom, prix_achat, prix_vente, quantite, emplacement)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ref, nom, pa, pv, qty, loc))

            piece_id = self.cursor.lastrowid

            self.cursor.execute('''
                INSERT INTO compatibilites (piece_id, marque, modele, moteur, annee)
                VALUES (?, ?, ?, ?, ?)
            ''', (piece_id, marque, modele, moteur, annee))

            self.conn.commit()
            messagebox.showinfo("Succès", "Pièce ajoutée avec succès!")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")

if __name__ == "__main__":
    app = AutoPartsApp()
    app.mainloop()
