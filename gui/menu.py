import tkinter as tk
from tkinter import ttk
from gui import inventario
from gui import clientes
from gui import ventas
from gui import apartados

class MenuWindow(tk.Toplevel):
    def __init__(self, root,id_usuario):
        super().__init__(root)
        self.title(f"Menú Principal - {id_usuario}")
        self.center_window(787, 586)    
        self.resizable(1, 1)
        self.id_usuario = id_usuario

        # ----- FRAME IZQUIERDO -----
        left_frame = tk.Frame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=40, pady=80)

        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)


        # Botón INVENTARIO
        btn_config = {
            "font": ("Segoe UI", 18),
            "width": 15,
            "height": 3
        }

        self.boton_inventario = tk.Button(
            left_frame,
            text="Inventario\nDisponible",
            bg="#DCD0FF",
            command=self.abrir_inventario,
            **btn_config
        )
        self.boton_inventario.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.boton_clientes = tk.Button(
            left_frame,
            text="Clientes",
            bg="#A2CFFE",
            command=self.abrir_clientes,
            **btn_config
        )
        self.boton_clientes.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.boton_ventas = tk.Button(
            left_frame,
            text="Reporte \n de Ventas",
            bg="#AAF0D1",
            command=self.abrir_ventas,
            **btn_config
        )
        self.boton_ventas.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.boton_apartados = tk.Button(
            left_frame,
            text="Apartados",
            bg="#EFC378",
            command=self.abrir_apartados,
            **btn_config
        )
        self.boton_apartados.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

           

        

             # ----- FRAME DERECHO -----
        Right_frame = tk.Frame(self)
        Right_frame.pack(side="right", fill="y", padx=10, pady=10)


        # Botón Salir
        self.boton_salir = tk.Button(
            Right_frame,
            text="Salir",
            font=("Segoe UI", 14),
            bg="#F07B75",  
            width=10,
            height=2,
            command=self.salir
            )
        self.boton_salir.pack(pady=20)

  # ---------------------------
    # FUNCIONES PARA ABRIR VENTANAS
    # ---------------------------


    def abrir_clientes(self):
        from gui.clientes  import ClientesWindow
        self.withdraw()
        clientes.ClientesWindow(self)

    def abrir_inventario(self):
        from gui.inventario import InventarioActualWindow
        self.withdraw()
        inventario.InventarioActualWindow(self)

    def abrir_ventas(self):
        from gui.ventas import VentasWindow
        self.withdraw()
        ventas.VentasWindow(self,self.id_usuario)

    def abrir_apartados(self):     
        from gui.apartados import apartadosWindow
        self.withdraw()
        apartados.apartadosWindow(self)            
        


    # ---------------------------
    # SALIR DEL PROGRAMA
    # ---------------------------
    def salir(self):
        self.quit()     # cierra el loop
        self.destroy()  # destruye esta ventana
        exit()          # apaga todo

    # ---------------------------
    # CENTRAR VENTANA
    # ---------------------------
    def center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
