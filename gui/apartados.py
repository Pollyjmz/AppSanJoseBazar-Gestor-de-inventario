import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from db import conectar_db
from gui import vendido_apartado

class apartadosWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.apartado = None
        self.articulo_seleccionado = None
        

        self.title("Apartados")
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

        self.search_entry.bind("<Return>", self.buscar_apartados)

        # ===== TABLA =====
        table_frame = tk.Frame(self, bg="#8c8c8c")
        table_frame.pack(fill="both", expand=True, padx=40)

        columns = ("id_apartado", "Id_cliente", "cliente_nombre", "Fecha", "cantidad", "Total")

        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.table.heading(col, text=col)
            if col in ["Id_cliente"]:
                self.table.column(col, width=0, minwidth=0, stretch=tk.NO)
            else:
                self.table.column(col, width=120, anchor="center")

        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.seleccionar_apartado )
        
        # ==== BOTONES  ======== 
        bottom_frame = tk.Frame(self, bg="#8c8c8c") 
        bottom_frame.pack(fill="x", pady=20, padx=20)
        tk.Button(bottom_frame, text="Volver ⏎ ", width=15, bg="#F07B75", command=self.regresar).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Editar", width=15, bg="#A2CFFE" , command=self.editar).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Borrar 🗑️", width=15, bg="#EEE69D", command=self.borrar).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="vender", width=15, bg="#9DEEB1", command=self.vender).pack(side="left", padx=10)

        self.apartados  = self.obtener_apartados()       
        self.cargar_apartados(self.obtener_apartados())

    def center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

   # -------------------Funciones de cargar y mostrar--------------------   
    def obtener_apartados(self):
        conn = conectar_db()
        cursor = conn.cursor()
        query = """
            SELECT 
                ap.id_apartado,
                ap.id_cliente, 
                cl.nombre,        -- Nombre del cliente en vez de ID
                ap.fecha, 
                ap.cantidad, 
                ap.total
            FROM apartados ap
            JOIN clientes cl ON ap.id_cliente = cl.id_cliente
        """
        cursor.execute(query)
        apartados = cursor.fetchall()
        conn.close()
        return apartados

    
    def cargar_apartados(self, apartados):
        self.table.delete(*self.table.get_children())

        for apartado in apartados:
            self.table.insert(
                "",
                "end",
                values=apartado
        )

    def refrescar_tabla(self):
        apartados = self.obtener_apartados()
        self.cargar_apartados(apartados)

    def buscar_apartados(self, event=None):
        texto = self.search_var.get()
        conn = conectar_db()
        cursor = conn.cursor()
        
        # Base de la consulta con el JOIN para obtener el nombre del cliente
        query_base = """
            SELECT ap.id_apartado, ap.id_cliente, cl.nombre, ap.fecha, ap.cantidad, ap.total
            FROM apartados ap
            JOIN clientes cl ON ap.id_cliente = cl.id_cliente
        """

        if texto.strip() == "":
            cursor.execute(query_base)
        else:
            query_busqueda = query_base + " WHERE cl.nombre LIKE %s OR ap.id_apartado LIKE %s"
            cursor.execute(query_busqueda, (f"%{texto}%", f"%{texto}%"))
            
        apartados = cursor.fetchall()
        conn.close()
        self.cargar_apartados(apartados)
        
    def seleccionar_apartado(self, event):
        seleccion = self.table.selection()
        if seleccion:
            item = self.table.item(seleccion[0])
            valores = item["values"]

            self.apartado = {
            "id_apartado": valores[0],
            "id_cliente":  valores[1],
            "cliente":     valores[2],
            "fecha":       valores[3],
            "cantidad":    valores[4],
            "total":       valores[5]
        }

           
            
      # ======= FUNCIONES DE BOTONES =======

    def vender(self):
        if not self.apartado:
            messagebox.showwarning(
                "Atención",
                "Selecciona un apartado para finalizar la venta"
            )
            return
        respuesta = messagebox.askyesno("Confirmar Venta", 
                f"¿Desea finalizar la venta de este apartado?\n\nTotal a pagar: {self.apartado['total']}"
         )
        if not respuesta:
            return

        try:
            conn = conectar_db()
            cursor = conn.cursor()

            # 1. Obtener datos completos del apartado 
            cursor.execute("SELECT id_vendedor, id_cliente, id_articulo,fecha,precio_apartado,cantidad,total FROM apartados WHERE id_apartado = %s", (self.apartado["id_apartado"],))
            datos_extra = cursor.fetchone()
            
            if not datos_extra:
                messagebox.showerror("Error", "No se encontraron datos del apartado en DB")
                conn.close()
                return

            id_vendedor, id_cliente, id_articulo, fecha, precio_apartado, cantidad, total = datos_extra
                    # 2. Insertar en tabla VENTAS
            cursor.execute("""
                INSERT INTO ventas
                (id_vendedor, id_cliente, id_articulo, fecha,
                precio_vendido, cantidad, total)
                VALUES (%s, %s, %s, CURDATE(), %s, %s, %s)
            """, (id_vendedor, id_cliente, id_articulo, precio_apartado, cantidad,total))

                    # 3. Eliminar de APARTADOS 
            cursor.execute(
                "DELETE FROM apartados WHERE id_apartado = %s",
                (self.apartado["id_apartado"],))
                
                    # 4. Actualizar stock en ARTICULOS  
            cursor.execute("""
                UPDATE articulos 
                SET estado = 'vendido' 
                WHERE id_articulo = %s AND cantidad_disponible <= 0
                """, (id_articulo,))
            conn.commit()
            conn.close()
                    
            messagebox.showinfo("Éxito", "El apartado se ha convertido en venta.")
            self.refrescar_tabla()
            self.apartado = None

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar venta: {e}")
                   
        

    
    def editar(self):        
        if not self.apartado:
            messagebox.showwarning("Advertencia", "Seleccione un apartado para editar.")
            return 
        from gui.vendido_apartado import VendidoApartado
        
        
        VendidoApartado(
            self, 
            modo="apartar", 
            articulo_id=self.apartado["id_articulo"],
            on_save=self.refrescar_tabla
        )
      
        

    def borrar(self):
        if not self.apartado:
            messagebox.showwarning("Advertencia", "Seleccione un apartado para borrar.")
            return

        if not messagebox.askyesno("Confirmar", "¿Desea borrar este apartado?"):
            return

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM apartados WHERE id_apartado=%s", (self.apartado['id_apartado'],))
        conn.commit()
        conn.close()

        self.cargar_apartados(self.obtener_apartados())
        self.apartado = None        

    def regresar(self):
        self.master.deiconify()
        self.destroy()

    
                                                            