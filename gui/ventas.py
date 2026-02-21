import tkinter as tk
from tkinter import ttk, messagebox
from db import conectar_db  
from tkcalendar import DateEntry


class VentasWindow(tk.Toplevel):
    def __init__(self,parent, id_usuario):
        super().__init__(parent)
        self.parent = parent
        self.id_usuario = id_usuario
        self.title("Ventas")
        self.center_window(787, 586)
        self.resizable(True, True)

        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True)

        # Título
        self.label_title = tk.Label(
            frame,
            text="Ingrese Las fechas Para Generar Reporte de Ventas",
            font=("Times New Roman", 20)
        )
        self.label_title.grid(row=0, column=0, columnspan=2, pady=20)

        # Entradas para las fechas
        ttk.Label(frame, text="Desde:", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w", pady=10)
        self.fecha_inicio = DateEntry(frame, width=27, background="#AAF0D1", foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd")
        self.fecha_inicio.grid(row=1, column=1, pady=10)
        
        ttk.Label(frame, text="Hasta:", font=("Segoe UI", 12)).grid(row=2, column=0, sticky="w", pady=10)
        self.fecha_fin = DateEntry(frame, width=27, background="#AAF0D1", foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd")
        self.fecha_fin.grid(row=2, column=1, pady=10)

        # Botones pack
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(anchor="center")

        btn_generar = ttk.Button(bottom_frame, text="Volver ⏎", command=self.regresar)
        btn_generar.pack(side="left", padx=10)
        btn_volver = ttk.Button(bottom_frame, text="Generar Informe", command=self.generar_informe)
        btn_volver.pack(side="left", padx=10)


    def center_window(self, width, height):
        """Centra la ventana en la pantalla."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def regresar(self):
        self.master.deiconify()    
        self.destroy()    

 # En ventas.py
    def generar_informe(self):
        fecha_inicio = self.fecha_inicio.get()
        fecha_fin = self.fecha_fin.get()

        conn = conectar_db()
        cursor = conn.cursor() # Si usas dictionary=True es más fácil

        try:
            # Mejoramos la consulta para traer el nombre del artículo
            query = """
                SELECT v.fecha, a.nombre, v.cantidad, v.precio_vendido, v.total
                FROM ventas v
                JOIN articulos a ON v.id_articulo = a.id_articulo
                WHERE v.fecha BETWEEN %s AND %s
                AND v.id_vendedor = %s
            """
            cursor.execute(query, (fecha_inicio, fecha_fin, self.id_usuario))
            resultados = cursor.fetchall()

            with open("reporte_ventas.txt", "w", encoding="utf-8") as file:
                file.write(f"REPORTE PERSONAL DE VENTAS\n")
                file.write(f"Vendedor ID: {self.id_usuario}\n")
                file.write(f"Periodo: {fecha_inicio} al {fecha_fin}\n")
                file.write("-" * 60 + "\n")
                file.write(f"{'FECHA':<12} | {'ARTÍCULO':<20} | {'CANT':<5} | {'TOTAL':<10}\n")
                file.write("-" * 60 + "\n")
                
                total_general = 0
                for fecha, nombre, cant, precio, total in resultados:
                    file.write(f"{str(fecha):<12} | {nombre[:20]:<20} | {cant:<5} | {total:<10}\n")
                    total_general += float(total)
                
                file.write("-" * 60 + "\n")
                file.write(f"{'TOTAL ACUMULADO:':<42} $ {total_general:.2f}\n")

            messagebox.showinfo("Éxito", f"Se han procesado {len(resultados)} ventas.")

        except Exception as e:
            messagebox.showerror("Error", f"Detalle: {e}")
        finally:
            conn.close()

