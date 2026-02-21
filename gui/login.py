import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from gui.menu import MenuWindow
from db import conectar_db  

class LoginWindow:
    def __init__(self, root):    
        self.root = root
        self.root.title("Ingreso al Sistema")
        width = 787
        height = 586
        self.center_window(width, height)
        self.root.resizable(1,1)

        # Frame principal
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        #--- Usuario ---
        ttk.Label(frame, text="Usuario:", font=("Segoe UI", 12)).grid(
        row=1, column=0, sticky="w", pady=10)
        self.usuario = ttk.Entry(frame, width=30)
        self.usuario.grid(row=1, column=1, pady=10)

        #--- Contraseña ---
        ttk.Label(frame, text="Contraseña:", font=("Segoe UI", 12)).grid(
        row=2, column=0, sticky="w", pady=10)
        self.contrasena = ttk.Entry(frame, width=30, show="*")
        self.contrasena.grid(row=2, column=1, pady=10)

        #--- Botón ingresar ---
        ttk.Button(frame, text="Ingresar", command=self.validar_login).grid(
            row=3, column=1, pady=20 )


    def center_window(self, width, height):
        """Centra la ventana en la pantalla."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.root.geometry(f"{width}x{height}+{x}+{y}")


   
    def validar_login(self):
        usuario = self.usuario.get().strip()
        contrasena = self.contrasena.get().strip()

        resultado = self.verificar_usuario(usuario, contrasena)
        if not resultado:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            return
        id_vendedor, usuario, rol = resultado
        # Cerrar Login y abrir menú
        self.root.withdraw()
        MenuWindow(self.root, id_usuario=id_vendedor)


    def verificar_usuario(self, usuario, contrasena ):
        conn = conectar_db()
        try:
            cursor = conn.cursor()

            query = """
                SELECT id_vendedor, usuario, rol_tienda    
                FROM login 
                WHERE usuario = %s AND contrasena= %s
            """
            cursor.execute(query, (usuario, contrasena))
            resultado = cursor.fetchone()
            return resultado

        except Exception as e:
            print("Error:", e)
            return None

        finally:
            cursor.close()
            conn.close()



