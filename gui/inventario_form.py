import tkinter as tk
from tkinter import ttk, messagebox
from db import conectar_db

class InventarioForm(tk.Toplevel):
    
    def __init__(self, parent, articulo=None, on_save=None):
        super().__init__(parent)
        self.articulo = articulo  # Si es None, es "Agregar". Si tiene datos, es "Editar".
        self.on_save = on_save
        
        # Configuración de ventana
        titulo = "Editar Artículo" if self.articulo else "Agregar Artículo"
        self.title(titulo)
        self.geometry("600x750")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.regresar)

        # Diccionarios de mapeo (IDs vs Nombres)
        self.vendedores = {"Admin": 1, "Relove": 2, "ChikaLoka": 3}
        self.vendedores_inv = {v: k for k, v in self.vendedores.items()}
        
        self.categorias = {"Prenda": 1, "Accesorio": 2}
        self.categorias_inv = {v: k for k, v in self.categorias.items()}

        self.tipos = {
            1: {"Camisa":1, "Camiseta":2, "Blusa":3, "Saco Hombre":4,"Saco Mujer":5,
                "Sweter":6, "Pantalones/Short":7, "Enagua":8, "Vestido Largo":9, 
                "Vestido Corto":10, "Vestido Baño":11, "Bufanda":12, "Disfraz":13, 
                "Medias":14, "Zapatos":15},
            2: {"Aretes":1, "Sets":2, "Pulseras":3, "Anillos":4, "Collares":5, 
                "Pines":6, "Estuche Celular":7, "Accesorio Cabello":8, "Piercing":9,
                "Cartera":10, "Faja":11, "Gorra":12, "Gorro":13, "Sombrero":14}
        }
        # Invertir diccionarios de tipos para carga rápida
        self.tipos_inv = {
            1: {v: k for k, v in self.tipos[1].items()},
            2: {v: k for k, v in self.tipos[2].items()}
        }

        self.crear_interfaz(titulo)

        # Si estamos editando, cargar los datos
        if self.articulo:
            self.cargar_datos()

    def crear_interfaz(self, titulo_texto):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Canvas y Scrollbar por si la pantalla es pequeña
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === CONTENIDO DEL FORMULARIO ===
        ttk.Label(self.scrollable_frame, text=titulo_texto, font=("Segoe UI", 18, "bold")).pack(pady=10)

        # 1. Código (ID Articulo) - Solo lectura si es edición, editable si es nuevo
        self.entry_codigo = self.crear_campo("Código Prenda (ID):")
        if self.articulo:
            self.entry_codigo.config(state="readonly")

        # 2. Nombre
        self.entry_nombre = self.crear_campo("Nombre / Descripción:")

        # 3. Cantidad
        self.entry_cantidad = self.crear_campo("Cantidad:")
        
        # 4. Precio
        self.entry_precio = self.crear_campo("Precio (₡):")
        
        # 5. Talla
        self.entry_talla = self.crear_campo("Talla:")

        # 6. Emprendimiento (Combobox)
        ttk.Label(self.scrollable_frame, text="Emprendimiento:", font=("Segoe UI", 11)).pack(anchor="w", pady=(10,0))
        self.combo_emprendimiento = ttk.Combobox(self.scrollable_frame, values=list(self.vendedores.keys()), state="readonly")
        self.combo_emprendimiento.pack(fill="x", pady=5)
        self.combo_emprendimiento.current(0) # Default

        # 7. Estado (Radiobuttons)
        ttk.Label(self.scrollable_frame, text="Estado:", font=("Segoe UI", 11)).pack(anchor="w", pady=(10,0))
        self.var_estado = tk.StringVar(value="disponible")
        frame_estado = ttk.Frame(self.scrollable_frame)
        frame_estado.pack(anchor="w", pady=5)
        for est in ["disponible", "apartado", "vendido"]:
            ttk.Radiobutton(frame_estado, text=est.capitalize(), variable=self.var_estado, value=est).pack(side="left", padx=5)

        # 8. Categoría (Radiobuttons que actualizan Tipos)
        ttk.Label(self.scrollable_frame, text="Categoría:", font=("Segoe UI", 11)).pack(anchor="w", pady=(10,0))
        self.var_categoria = tk.StringVar(value="Prenda") # Default
        frame_cat = ttk.Frame(self.scrollable_frame)
        frame_cat.pack(anchor="w", pady=5)
        
        for cat in self.categorias.keys():
            ttk.Radiobutton(
                frame_cat, text=cat, variable=self.var_categoria, value=cat, 
                command=self.actualizar_tipos_ui
            ).pack(side="left", padx=5)

        # 9. Tipo (Radiobuttons dinámicos)
        ttk.Label(self.scrollable_frame, text="Tipo:", font=("Segoe UI", 11)).pack(anchor="w", pady=(10,0))
        self.frame_tipos = ttk.Frame(self.scrollable_frame)
        self.frame_tipos.pack(anchor="w", pady=5)
        self.var_tipo = tk.StringVar()
        
        # Inicializar tipos
        self.actualizar_tipos_ui()

        # 10. Comentario
        ttk.Label(self.scrollable_frame, text="Comentario:", font=("Segoe UI", 11)).pack(anchor="w", pady=(10,0))
        self.text_comentario = tk.Text(self.scrollable_frame, height=4, width=40)
        self.text_comentario.pack(fill="x", pady=5)

        # BOTONES
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text=" Guardar", command=self.guardar_articulo).pack(side="left", padx=10)
        ttk.Button(btn_frame, text=" Cancelar", command=self.regresar).pack(side="left", padx=10)

    # --- Helpers de UI ---
    def crear_campo(self, label):
        ttk.Label(self.scrollable_frame, text=label, font=("Segoe UI", 11)).pack(anchor="w", pady=(5,0))
        entry = ttk.Entry(self.scrollable_frame)
        entry.pack(fill="x", pady=2)
        return entry

    def actualizar_tipos_ui(self):
        # Limpiar anterior
        for widget in self.frame_tipos.winfo_children():
            widget.destroy()
        
        cat_nombre = self.var_categoria.get()
        if not cat_nombre: return
        
        cat_id = self.categorias[cat_nombre]
        tipos_dict = self.tipos.get(cat_id, {})

        # Crear Grid de Radiobuttons
        row, col = 0, 0
        for nombre_tipo in tipos_dict.keys():
            ttk.Radiobutton(
                self.frame_tipos, text=nombre_tipo, variable=self.var_tipo, value=nombre_tipo
            ).grid(row=row, column=col, sticky="w", padx=5, pady=2)
            col += 1
            if col > 3: # 4 columnas
                col = 0
                row += 1

    
    def cargar_datos(self):
        
        self.entry_codigo.config(state="normal")
        self.entry_codigo.insert(0, str(self.articulo["id_articulo"]))
        self.entry_codigo.config(state="readonly")

        self.entry_nombre.insert(0, self.articulo["nombre"])
        self.entry_cantidad.insert(0, str(self.articulo["cantidad_disponible"]))
        self.entry_precio.insert(0, str(self.articulo["precio"]))
        self.entry_talla.insert(0, self.articulo["talla"])

        self.text_comentario.insert("1.0", self.articulo["comentario"])
        
        #vendedor
        vendedor_nombre = self.vendedores_inv.get(self.articulo["id_vendedor"])
        if vendedor_nombre: self.combo_emprendimiento.set(vendedor_nombre)
        #estado
        self.var_estado.set(self.articulo["estado"])
        # categoria por ID
        self.var_categoria.set(self.articulo["id_categoria"])
        self.actualizar_tipos_ui()

        # tipo por ID
        self.var_tipo.set(self.articulo["id_tipo"])

    def guardar_articulo(self):
        # 1. Obtener datos
        try:
            codigo = self.entry_codigo.get().strip()
            nombre = self.entry_nombre.get().strip()
            cantidad = int(self.entry_cantidad.get())
            precio = float(self.entry_precio.get())
            talla = self.entry_talla.get().strip()
            comentario = self.text_comentario.get("1.0", "end-1c")
            
            vendedor_id = self.vendedores[self.combo_emprendimiento.get()]
            estado = self.var_estado.get()
            
            cat_id = self.categorias[self.var_categoria.get()]
            
            tipo_nombre = self.var_tipo.get()
            if not tipo_nombre:
                messagebox.showerror("Error", "Seleccione un Tipo")
                return
            tipo_id = self.tipos[cat_id][tipo_nombre]

            if not codigo or not nombre:
                messagebox.showerror("Error", "Código y Nombre son obligatorios")
                return

        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser entero y Precio decimal")
            return

        # 2. Guardar en BD
        conn = conectar_db()
        cursor = conn.cursor()

        try:
            if self.articulo: 
                # === ACTUALIZAR  ===
                query = """
                    UPDATE articulos
                    SET nombre=%s, cantidad_disponible=%s, precio=%s, talla=%s, 
                        comentario=%s, id_vendedor=%s, estado=%s, id_categoria=%s, id_tipo=%s
                    WHERE id_articulo=%s
                """
                valores = (nombre, cantidad, precio, talla, comentario, vendedor_id, estado, cat_id, tipo_id, codigo)
                cursor.execute(query, valores)
                mensaje = "Artículo actualizado correctamente."

            else:
                # === CREAR (INSERT) ===
                # Verificar si ID ya existe
                cursor.execute("SELECT id_articulo FROM articulos WHERE id_articulo=%s", (codigo,))
                if cursor.fetchone():
                    messagebox.showerror("Error", f"El código {codigo} ya existe.")
                    conn.close()
                    return

                query = """
                    INSERT INTO articulos 
                    (id_articulo, nombre, cantidad_disponible, precio, talla, comentario, 
                     id_vendedor, estado, id_categoria, id_tipo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (codigo, nombre, cantidad, precio, talla, comentario, vendedor_id, estado, cat_id, tipo_id)
                cursor.execute(query, valores)
                mensaje = "Artículo creado correctamente."

            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", mensaje)
            
            if self.on_save:
                self.on_save() # Refrescar tabla en la ventana padre
            
            self.destroy()

        except Exception as e:
            conn.close()
            messagebox.showerror("Error de Base de Datos", str(e))

    def regresar(self):
        self.destroy()