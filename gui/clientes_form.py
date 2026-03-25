import tkinter as tk
from tkinter import ttk, messagebox
from db import conectar_db

class ClientesForm(tk.Toplevel):
    def __init__(self, parent, cliente_data=None, on_save=None):
        super().__init__(parent)
        
        self.parent = parent
        self.cliente_data = cliente_data
        self.on_save = on_save
                                                                                                                                                                                                                               
        self.title("Formulario de Cliente")
        self.geometry("650x605")
        self.config(bg="#EFEFEF")

        self.protocol("WM_DELETE_WINDOW", self.regresar)

        self.crear_formulario()

    def crear_formulario(self):
        # Título
        titulo = "Editar Cliente" if self.cliente_data else "Agregar Cliente"
        tk.Label(self, text=titulo, font=("Arial", 18, "bold"), bg="#EFEFEF").pack(pady=15)

        frame = tk.Frame(self, bg="#EFEFEF")
        frame.pack(pady=10)

        # Campos del formulario      
        self.entries = {}

        campos = [
            
            ("Nombre", "nombre"),
            ("Número Teléfono", "telefono"),
            ("Correo", "email"),
            ("Signo Zodiacal", "signo_zodiacal"),
            ("Talla Pantalón", "talla_bottom"),
            ("Talla Camisa", "talla_top"),
            ("Talla Zapatos", "talla_zapatos"),
            ("observaciones", "observaciones")

        ]

        # Construir cada entry
        for label, key in campos:
            tk.Label(frame, text=label, bg="#EFEFEF", font=("Arial", 10)).pack(anchor="w")
            entry = tk.Entry(frame, width=45)
            entry.pack(pady=3)
            self.entries[key] = entry

        

        # Si es edición → llenar datos
        if self.cliente_data:
            self.cargar_datos()


        # ==============================
        #   BOTONES
        # ==============================
        btn_frame = tk.Frame(self, bg="#EFEFEF")
        btn_frame.pack(pady=25)

        tk.Button(btn_frame, text="Guardar", width=15, bg="#B3FFAE",
                  command=self.guardar).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Atras", width=15, bg="#FFB2B2",
                  command=self.regresar).pack(side="left", padx=10)

    def cargar_datos(self):
        #Carga info del cliente en el formulario si se está editando
        for key, entry in self.entries.items():
            valor = self.cliente_data.get(key, "")
            entry.insert(0, str(valor))

       
    def guardar(self):
        data = {key: entry.get() for key, entry in self.entries.items()}

        conn = conectar_db()
        cursor = conn.cursor()

        try:
            if self.cliente_data:
              
                # =====================
                # EDITAR CLIENTE
                # =====================
                id_cli = self.cliente_data["id_cliente"]
                query = """
                    UPDATE clientes SET
                        nombre=%s, telefono=%s, email=%s,
                        signo_zodiacal=%s, talla_bottom=%s,
                        talla_top=%s, talla_zapatos=%s, observaciones=%s
                    WHERE id_cliente=%s
                """
                valores =  (
                    data["nombre"],
                    data["telefono"],
                    data["email"],
                    data["signo_zodiacal"],
                    data["talla_bottom"],
                    data["talla_top"],
                    data["talla_zapatos"],
                    data["observaciones"],
                    id_cli
                )
                cursor.execute(query, valores)

            else:
                # =====================
                # AGREGAR CLIENTE
                # =====================
                 query = """
                  INSERT INTO clientes (
                  nombre, telefono, email, signo_zodiacal,
                    talla_bottom, talla_top, talla_zapatos, observaciones
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)                """
                 valores = (
                                    data["nombre"], data["telefono"], data["email"], data["signo_zodiacal"],
                    data["talla_bottom"], data["talla_top"], data["talla_zapatos"], data["observaciones"]
                 )
                 cursor.execute(query, valores)

            conn.commit()
            messagebox.showinfo("Éxito", "Cliente guardado correctamente.")

            if self.on_save:
                self.on_save() 

            self.regresar()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))

        finally:
            conn.close()

  

    def regresar(self):
    
        self.destroy()
        