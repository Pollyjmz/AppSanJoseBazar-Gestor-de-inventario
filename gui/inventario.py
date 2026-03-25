import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from db import conectar_db

class InventarioActualWindow(tk.Toplevel):
    def __init__(self,parent) :
        super().__init__(parent)
        self.parent = parent        
        self.title("Inventario Actual")
        self.center_window(1414, 944)
        self.configure(bg="#8c8c8c")
        self.resizable(True, True)
        self.articulo_seleccionado = None
       

       # ===== BUSCADOR (arriba) =====
        self.search_var = tk.StringVar()
        top_frame = tk.Frame(self, bg="#8c8c8c")
        top_frame.pack(fill="x", pady=20)
        # Icono de lupa 
        ttk.Label(top_frame, text="🔍", font=("Segoe UI", 16), background="#8c8c8c").pack(side="left", padx=10)
        self.search_entry = ttk.Entry(top_frame, width=40, textvariable=self.search_var)
        self.search_entry.pack(side="left", padx=10)

        self.search_entry.bind("<Return>", self.buscar_articulos)

        

        # ===== TABLA =====
        table_frame = tk.Frame(self, bg="#8c8c8c")
        table_frame.pack(fill="both", expand=True, padx=40)

       # En el __init__ de InventarioActualWindow
        columns = ("id_articulo", "nombre", "cantidad_disponible", "id_vendedor", "precio", "estado", "id_categoria","nombre_categoria", "id_tipo","tipo", "talla", "comentario") 
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.table.heading(col, text=col)        
            if col in ["id_articulo", "id_vendedor", "id_categoria", "id_tipo"]:
                # Ancho 0, minwidth 0 y stretch en False para que no se vea
                self.table.column(col, width=0, minwidth=0, stretch=tk.NO)
            else:
                self.table.column(col, width=120, anchor="center")
        self.table.pack(fill="both", expand=True)        

      # ===== BOTONES =====
        bottom_frame = tk.Frame(self, bg="#8c8c8c")
        bottom_frame.pack(fill="x", pady=20, padx=20)
        tk.Button(bottom_frame, text="Volver ⏎", width=15, bg="#F07B75", command=self.regresar).pack(side="left",padx=10)              
        tk.Button(bottom_frame, text="Agregar", width=15, bg="#DCD0FF", command= self.agregar).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Editar", width=15, bg="#A2CFFE", command = self.editar).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Apartar", width=15, bg="#EEE69D", command= self.apartar).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Vender", width=15, bg="#AAF0D1", command = self.vender).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Borrar 🗑️", width=15, bg="#EEE69D", command=self.borrar).pack(side="left", padx=10)

        datos =self.obtener_inventario()
        self.cargar_inventario(datos)
        self.table.bind("<<TreeviewSelect>>", self.seleccionar_articulo)


    def center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
# ----------------------------- Funciones ---------------------------


    def _get_base_query(self):
        return """
            SELECT 
                a.id_articulo, 
                a.nombre, 
                a.cantidad_disponible,
                a.id_vendedor, 
                a.precio, 
                a.estado,
                a.id_categoria,            
                c.nombre_categoria, -- Cambiamos el ID por el Nombre
                a.id_tipo,
                t.tipo,      -- Cambiamos el ID por el Nombre
                a.talla, 
                a.comentario
            FROM articulos a
            LEFT JOIN categorias c ON a.id_categoria = c.id_categoria
            LEFT JOIN tipos t ON a.id_tipo = t.id_tipo
            WHERE a.estado != 'eliminado'
            

          """  

    def obtener_inventario(self):
        try:
            conn = conectar_db()        
            cursor = conn.cursor()        
            cursor.execute(self._get_base_query())
            articulos = cursor.fetchall()
            conn.close()
            print(f"DEBUG: Se encontraron {len(articulos)} artículos.") # Ver en consola
            return articulos
        except Exception as e:
            print(f"ERROR SQL en obtener_inventario: {e}")
            return []
        
        
    def refrescar_tabla(self):
        self.cargar_inventario(self.obtener_inventario())
        self.articulo_seleccionado = None

    def seleccionar_articulo(self, event):
        seleccion = self.table.selection() 
        if not seleccion: 
            self.articulo_seleccionado = None 
            return 
        item = self.table.item(seleccion[0]) 
        v= item["values"]

        self.articulo_seleccionado = { 
            "id_articulo": v[0],
            "nombre": v[1],
            "cantidad_disponible": v[2],
            "id_vendedor": v[3],
            "precio": v[4],
            "estado": v[5],
            "id_categoria": v[6],
            "nombre_categoria": v[7],
            "id_tipo": v[8],
            "nombre_tipo": v[9],
            "talla": v[10],
            "comentario": v[11],
        }

        

    def cargar_inventario(self, articulos):
        self.table.delete(*self.table.get_children())
        for art in articulos:
            self.table.insert("", "end", values=art)



    def buscar_articulos(self, event= None):
        texto = self.search_var.get().strip()
        conn = conectar_db()
        cursor = conn.cursor()
        query = self._get_base_query()
        if texto == "":
            cursor.execute(query)
        else:   
            query += " WHERE a.nombre LIKE %s OR t.tipo LIKE %s OR c.nombre_categoria LIKE %s  OR a.talla LIKE %s"
            cursor.execute(query, (f"%{texto}%", f"%{texto}%", f"%{texto}%", f"%{texto}%"))

        articulos = cursor.fetchall()
        conn.close()
        self.cargar_inventario(articulos)


  # ======= FUNCIONES DE BOTONES =======
    def agregar(self):
        from gui.inventario_form import InventarioForm
        InventarioForm(self, on_save=self.refrescar_tabla)

    def editar(self):
        if not self.articulo_seleccionado:
            messagebox.showwarning("Atención", "Selecciona un artículo para editar")
            return
        from gui.inventario_form import InventarioForm
        
        InventarioForm(
        self,
        articulo=self.articulo_seleccionado,
        on_save=self.refrescar_tabla
        )   

    def vender(self):        
        if not self.articulo_seleccionado:
            messagebox.showwarning("Atención", "Selecciona un artículo para vender")
            return                # Validar si ya está vendido        
        if self.articulo_seleccionado['estado'] == 'vendido':             
              messagebox.showwarning("Error", "Este artículo ya está vendido.")             
              return        
        from gui.vendido_apartado import VendidoApartado        
        # Pasamos el ID y el modo       
        VendidoApartado(
            self,
            modo="vender", 
            articulo_id=self.articulo_seleccionado["id_articulo"],    
            on_save=self.refrescar_tabla
        ) 
    
    def apartar(self):        
        if not self.articulo_seleccionado:            
            messagebox.showwarning("Atención", "Selecciona un artículo para apartar")            
            return                    
        from gui.vendido_apartado import VendidoApartado       
        VendidoApartado(
            self,
            modo="apartar",
            articulo_id=self.articulo_seleccionado["id_articulo"],
            on_save=self.refrescar_tabla
        )
        
    def borrar(self):
        if not self.articulo_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un artículo.")
            return

        if not messagebox.askyesno("Confirmar", "¿Desea borrar este artículo?"):
            return

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE articulos SET estado = 'eliminado' WHERE id_articulo=%s",
            (self.articulo_seleccionado["id_articulo"],)
        )
        conn.commit()
        conn.close()

        self.refrescar_tabla()
        self.articulo_seleccionado = None
     
    def regresar(self):        
        self.master.deiconify()        
        self.destroy()
           