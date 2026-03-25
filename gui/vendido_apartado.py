import tkinter as tk
from tkinter import ttk, messagebox
from db import conectar_db
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox
from db import conectar_db


class VendidoApartado(tk.Toplevel):

    def __init__(self, master, modo, articulo_id, on_save):
        super().__init__(master)

        self.modo = modo   # "vender" | "apartar"
        self.articulo_id = articulo_id 
              
        self.on_save = on_save

        self.titulo_texto = "Vender Artículo" if modo == "vender" else "Apartar Artículo"
        self.title(self.titulo_texto)

        self.clientes_map = {}       
        self.articulo = self.obtener_articulo()

        if not self.articulo:
            return

        self.resizable(False, False)

        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text=self.titulo_texto, font=("Segoe UI", 16, "bold")).pack(pady=10)

        ttk.Label(
            frame,
            text=f"Stock actual: {self.articulo['cantidad_disponible']}",
            foreground="gray"
        ).pack(pady=5)

        # Cliente------
        ttk.Label(frame, text="Cliente:", font=("Segoe UI", 11)).pack(anchor="w")
        self.combo_cliente = ttk.Combobox(frame)
        self.combo_cliente.pack(fill="x", pady=5)
        self.cargar_clientes()

        #Cantidad--------
        ttk.Label(frame, text="Cantidad:", font=("Segoe UI", 11)).pack(anchor="w")
        self.entry_cantidad = ttk.Entry(frame, width=10)
        self.entry_cantidad.pack(pady=5)
        self.entry_cantidad.insert(0, "1")#valor por defecto

        # Precio------
        ttk.Label(frame, text="Monto cancelado:", font=("Segoe UI", 11)).pack(anchor="w")
        self.entry_precio = ttk.Entry(frame)
        self.entry_precio.pack(fill="x", pady=5)
        self.entry_precio.insert(0, str(self.articulo["precio"]))

        # ================== BOTONES ==================
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Guardar", command=self.guardar, width=14).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy, width=14).pack(side="left", padx=5)

    # ======================================================
    def center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ======================================================
    def obtener_articulo(self):
        try:
            conn = conectar_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id_articulo,id_vendedor, precio, cantidad_disponible, estado
                FROM articulos
                WHERE id_articulo = %s
                """,
                (self.articulo_id,) 
            )
            articulo = cursor.fetchone()
            conn.close()

            if not articulo:
                messagebox.showerror("Error", "Artículo no encontrado")
                self.destroy()
                return None

            return articulo

        except Exception as e:
            messagebox.showerror("Error DB", str(e))
            self.destroy()
            return None

    
    
    # ======================================================
    def cargar_clientes(self):

        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente, nombre FROM clientes WHERE estado != 'inactivo'")
            clientes = cursor.fetchall()
            conn.close()

            valores = []
            for cid, nombre in clientes:
                self.clientes_map[nombre] = cid
                valores.append(nombre)

            self.combo_cliente["values"] = valores

        except Exception as e:
            messagebox.showerror("Error DB", f"No se pudieron cargar clientes: {e}")

    # ======================================================
        # def Querys de guardar
    def apartar(self, cursor):           
        sql = """
            INSERT INTO apartados
            (id_vendedor, id_cliente, id_articulo, fecha, precio_apartado, cantidad, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        valores = (
                self.articulo['id_vendedor'],
                self.cliente_id,
                self.articulo_id,
                datetime.now().date(),
                self.precio,
                self.cantidad,
                self.precio * self.cantidad
            )

        cursor.execute(sql, valores)

    def vender(self, cursor):        
        sql = """
            INSERT INTO ventas
            (id_vendedor, id_cliente, id_articulo, fecha, precio_vendido, cantidad, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            self.articulo["id_vendedor"],
            self.cliente_id,
            self.articulo_id,
            datetime.now().date(),
            self.precio,
            self.cantidad,
            self.precio * self.cantidad
        )

        cursor.execute(sql, valores)

    def actualizar_stock(self, cursor):
        sql = """
            UPDATE articulos
            SET cantidad_disponible = cantidad_disponible - %s,
                estado = CASE
                    WHEN cantidad_disponible - %s <= 0 THEN 'vendido'
                    ELSE 'disponible'
                END
            WHERE id_articulo = %s

        """
        cursor.execute(sql, (self.cantidad,self.cantidad, self.articulo_id))    

                   
    def guardar(self):
            try:
                #1. Validaciones ---------------
                if not self.combo_cliente.get():
                    messagebox.showerror("Error", "Seleccione un cliente")
                    return
                try:
                    cantidad = int(self.entry_cantidad.get())
                except ValueError:
                    messagebox.showerror("Error", "Cantidad inválida")
                    return
                try:
                    precio = float(self.entry_precio.get())
                except ValueError:
                    messagebox.showerror("Error", "Precio inválido")
                    return
                cliente_id = self.clientes_map[self.combo_cliente.get()]

                if cantidad <= 0:
                    messagebox.showerror("Error", "Cantidad inválida")
                    return
                if cantidad > self.articulo["cantidad_disponible"]:
                    messagebox.showerror("Error", "No hay suficiente stock")
                    return
                
                self.cantidad = cantidad
                self.precio = precio
                self.cliente_id = cliente_id    


                #2. conectar DB ----------------                 
                conn = conectar_db()
                cursor = conn.cursor()
                

                # ===== APARTAR =====
                if self.modo == "apartar":
                    self.apartar(cursor)
                    self.actualizar_stock(cursor)    
                # ===== VENDER =====
                elif self.modo == "vender":
                    self.vender(cursor)
                    self.actualizar_stock(cursor)   
                    
                conn.commit()
                conn.close()

                if self.on_save:
                    self.on_save()

                self.destroy()

            except ValueError:
                messagebox.showerror("Error", "Cantidad y precio deben ser números")

            except Exception as e:
                messagebox.showerror("Error DB", str(e))

                


       
                  


