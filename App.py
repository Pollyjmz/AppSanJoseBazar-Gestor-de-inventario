import tkinter as tk
import gui
from gui.login import LoginWindow   
from gui.menu import MenuWindow
from gui.ventas import VentasWindow
from gui.inventario import InventarioActualWindow
from gui.clientes import ClientesWindow
from gui.inventario_form import InventarioForm
from gui.vendido_apartado import VendidoApartado
from gui.clientes_form import ClientesForm


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
