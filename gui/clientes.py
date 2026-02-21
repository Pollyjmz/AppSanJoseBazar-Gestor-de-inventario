import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from db import conectar_db

class ClientesWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.cliente = None

        self.title("Clientes")
        self.center_window(792, 944)
        self.configure(bg="#8c8c8c")
        self.resizable(True, True)
        

        # ===== BUSCADOR (arriba) =====
        self.search_var = tk.StringVar()
        top_frame = tk.Frame(self, bg="#8c8c8c")
        top_frame.pack(fill="x", pady=20)
        # Icono de lupa 
        ttk.Label(top_frame, text="🔍", font=("Segoe UI", 16), background="#8c8c8c").pack(side="left", padx=10)
        self.search_entry = ttk.Entry(top_frame, width=40, textvariable=self.search_var)
        self.search_entry.pack(side="left", padx=10)

        self.search_entry.bind("<Return>", self.buscar_clientes)

        

           
        # ===== TABLA =====
        table_frame = tk.Frame(self, bg="#8c8c8c")
        table_frame.pack(fill="both", expand=True, padx=40)

        columns = ("Nombre", "telefono ", "correo", "Talla Top", "Talla Bottom", "Talla de Zapatos","Signo Zodiacal")

        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=120, anchor="center")

        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.seleccionar_cliente)
        
        # ==== BOTONES  ======== 
        bottom_frame = tk.Frame(self, bg="#8c8c8c") 
        bottom_frame.pack(fill="x", pady=20, padx=20)
        tk.Button(bottom_frame, text="Volver ⏎ ", width=15, bg="#F07B75", command=self.regresar).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Agregar", width=15, bg="#DCD0FF" , command=self.agregar).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Editar", width=15, bg="#A2CFFE" , command=self.editar).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Borrar 🗑️", width=15, bg="#EEE69D", command=self.borrar).pack(side="left", padx=10)

        self.clientes = self.obtener_clientes()       
        self.cargar_clientes(self.obtener_clientes())

    def center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

   # -------------------Funciones de cargar y mostrar--------------------   
    def obtener_clientes(self):
        conn = conectar_db()
        cursor = conn.cursor(dictionary=False)
        cursor.execute("""
            SELECT id_cliente, nombre, telefono, email,
               talla_top, talla_bottom, talla_zapatos, signo_zodiacal, observaciones
            FROM clientes""")
        
        clientes = cursor.fetchall()
        conn.close()
        return clientes
    
    def cargar_clientes(self, clientes):
         #limpiar tabla
        self.table.delete(*self.table.get_children())

        for cliente in clientes:
            self.table.insert(
                "",
                "end",
                text=cliente[0],      # idcliente
                values=cliente[1:]    # resto de columnas
            )

    def refrescar_tabla(self):
        clientes = self.obtener_clientes()
        self.cargar_clientes(clientes)

    def buscar_clientes(self, event= None):
        texto = self.search_var.get()
        conn = conectar_db()
        cursor = conn.cursor()
        if texto.strip() == "":
            cursor.execute("""
                SELECT id_cliente, nombre, telefono, email,
                    talla_top, talla_bottom, talla_zapatos, signo_zodiacal, observaciones
                FROM clientes
            """)             
        else: 
            cursor.execute("""
                SELECT id_cliente, nombre, telefono, email,
                    talla_top, talla_bottom, talla_zapatos, signo_zodiacal, observaciones
                FROM clientes
                WHERE nombre LIKE %s
                    OR telefono LIKE %s
                    OR email LIKE %s
            """, (f"%{texto}%", f"%{texto}%", f"%{texto}%"))
        clientes = cursor.fetchall()
        conn.close()
        self.cargar_clientes(clientes)
        
    def seleccionar_cliente(self, event):
        seleccion = self.table.selection()
        if seleccion:
            item = self.table.item(seleccion[0])
            valores = item["values"]
            db_id = item['text']
            self.cliente = {
                "id_cliente": db_id,
                "nombre": valores[0],
                "telefono": valores[1],
                "email": valores[2],
                "talla_top": valores[3],
                "talla_bottom": valores[4],
                "talla_zapatos": valores[5],
                "signo_zodiacal": valores[6],
                "observaciones": valores[7]
            }

            
            
      # ======= FUNCIONES DE BOTONES =======

    def agregar(self):
        from gui.clientes_form import ClientesForm
        ClientesForm(self, on_save=self.refrescar_tabla)
    
    def editar(self):        
        if not self.cliente:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar.")
            return 
        from gui.clientes_form import ClientesForm
        ClientesForm(self, cliente_data=self.cliente, on_save=self.refrescar_tabla)
        

    def borrar(self):
        if not self.cliente:
            messagebox.showwarning("Advertencia", "Seleccione un cliente.")
            return

        if not messagebox.askyesno("Confirmar", "¿Desea borrar este cliente?"):
            return

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id_cliente=%s", (self.cliente['id_cliente'],))
        conn.commit()
        conn.close()

        self.cargar_clientes(self.obtener_clientes())
        self.cliente = None        

    def regresar(self):
        self.master.deiconify()
        self.destroy()

    
                                                            