import mysql.connector 
from mysql.connector import Error 

def crear_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Turmalina777"
    )

def crear_base_datos():
    conexion = crear_conexion()
    cursor = conexion.cursor()
    cursor.execute("DROP DATABASE IF EXISTS sanjose_bazar;")
    cursor.execute("CREATE DATABASE sanjose_bazar;")
    conexion.commit()
    conexion.close()
    print("Base de datos creada desde cero.")

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Turmalina777",
        database="sanjose_bazar"
    )

def crear_tablas():
    conexion = conectar_db()
    cursor = conexion.cursor()

    # --- LOGIN ---
    cursor.execute("""
    CREATE TABLE login (
        id_vendedor INT AUTO_INCREMENT PRIMARY KEY,
        usuario VARCHAR(50) NOT NULL UNIQUE,
        contrasena VARCHAR(100) NOT NULL,
        rol_tienda ENUM('Admin','Relove', 'Chikaloka') NOT NULL
    );
    """)

    # --- CLIENTES ---
    cursor.execute("""
    CREATE TABLE clientes (
        id_cliente INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        telefono VARCHAR(20),
        email VARCHAR(100),
        signo_zodiacal VARCHAR(50),
        talla_bottom VARCHAR(50),
        talla_zapatos VARCHAR(50),
        talla_top VARCHAR(50),
        estado ENUM('activo', 'inactivo') DEFAULT 'activo',  
        observaciones TEXT           
    );
    """)

    # --- CATEGORIAS ---
    cursor.execute("""
    CREATE TABLE categorias (
        id_categoria INT AUTO_INCREMENT PRIMARY KEY,
        nombre_categoria VARCHAR(100) NOT NULL
    );
    """)

    # --- TIPOS ---
    cursor.execute("""
    CREATE TABLE tipos (
        id_tipo INT AUTO_INCREMENT PRIMARY KEY,
        tipo VARCHAR(50) NOT NULL,
        id_categoria INT ,
        FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
    );
    """)

    # --- ARTICULOS ---
    cursor.execute("""
    CREATE TABLE articulos (
        id_articulo INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        cantidad_disponible INT,
        id_vendedor INT NOT NULL,
        precio FLOAT,
        estado ENUM('disponible', 'apartado', 'vendido', 'eliminado') DEFAULT 'disponible',
        id_categoria INT NOT NULL,
        id_tipo INT NOT NULL,
        talla VARCHAR(10),
        comentario TEXT,
        FOREIGN KEY (id_vendedor) REFERENCES login(id_vendedor),
        FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
        FOREIGN KEY (id_tipo) REFERENCES tipos(id_tipo)
    );
    """)

    # --- VENTAS ---
    cursor.execute("""
    CREATE TABLE ventas (
        id_venta INT AUTO_INCREMENT PRIMARY KEY,
        id_vendedor INT NOT NULL,
        id_cliente INT NOT NULL,
        id_articulo INT NOT NULL,
        fecha DATE DEFAULT (CURRENT_DATE),
        precio_vendido FLOAT,
        cantidad INT,
        total FLOAT,
        FOREIGN KEY (id_vendedor) REFERENCES login(id_vendedor),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_articulo) REFERENCES articulos(id_articulo)
    );
    """)

    #---- APARTAR-----
    cursor.execute("""
        CREATE TABLE apartados (
            id_apartado INT AUTO_INCREMENT PRIMARY KEY,
            id_vendedor INT NOT NULL,
            id_cliente INT NOT NULL,
            id_articulo INT NOT NULL,
            fecha DATE DEFAULT (CURRENT_DATE),
            precio_apartado FLOAT,
            cantidad INT,
            total FLOAT,
            FOREIGN KEY (id_vendedor) REFERENCES login(id_vendedor),
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
            FOREIGN KEY (id_articulo) REFERENCES articulos(id_articulo)
        );
        """)

    conexion.commit()
    conexion.close()
    print("Todas las tablas fueron creadas correctamente.")

    

def insertar_usuarios_iniciales():
    conexion = conectar_db()
    cursor = conexion.cursor()

    usuarios = [
        ('admin', '1234', 'Admin'),
        ('relove', '1234', 'Relove'),
        ('chikaloka', '1234', 'Chikaloka'),
        
    ]

    for usuario, contrasena, rol in usuarios:
        try:
            cursor.execute("""
                INSERT INTO login (usuario, contrasena, rol_tienda)
                VALUES (%s, %s, %s)
            """, (usuario, contrasena, rol))
        except:
            pass
    conexion.commit()
    conexion.close() 
    print("Usuarios iniciales insertados correctamente.")    

def insertar_categorias():
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    categorias = [
        ("prenda",),
        ("accesorio",)
                ]

    for categoria in categorias:
        print("Insertando:", categoria)
        cursor.execute(
            "INSERT INTO categorias (nombre_categoria) VALUES (%s)",
            categoria
        )

    conexion.commit()
    cursor.close()
    conexion.close()

    print(" Categorías insertadas correctamente.")
  
def insertar_tipos():

    conexion = conectar_db()
    cursor = conexion.cursor()

    tipos = [
        ("Camisa", 1),
        ("Camiseta", 1),
        ("Blusa", 1),
        ("Sacos hombre", 1),
        ("Saco mujer", 1),
        ("Sweter", 1),
        ("Pantalones", 1),
        ("Short", 1),
        ("Enaguas", 1),
        ("Vestidos largos", 1),
        ("Vestidos cortos", 1),
        ("Vestidos de baño", 1),
        ("Bufandas", 1),
        ("Disfraces", 1),
        ("Medias", 1),
        ("Zapatos", 1),

        ("Aretes", 2),
        ("Sets", 2),
        ("Pulseras", 2),
        ("Anillos", 2),
        ("Collares", 2),
        ("Pines", 2),
        ("Estuches de celular", 2),
        ("Accesorios para cabello", 2),
        ("Piercing", 2),
        ("Carteras", 2),
        ("Fajas", 2),
        ("Gorras", 2),
        ("Gorros", 2),
        ("Sombreros", 2)
    ]

    for tipo, categoria_id in tipos:
        try:
            cursor.execute("""
                INSERT INTO tipos (tipo, id_categoria)
                VALUES (%s, %s)
            """, (tipo, categoria_id))
        except:
            pass

    conexion.commit()
    conexion.close()
    print("Tipos insertados correctamente.")   

def insertar_articulo_pruebas():
    conexion = conectar_db()
    cursor = conexion.cursor()

    articulos = [
        ("Camisa de mezclilla", 10, 1, 250.0, "disponible", 1, 1, "M", "Camisa azul de mezclilla en buen estado."),
        ("Vestido floral", 5, 2, 300.0, "disponible", 1, 10, "S", "Vestido largo con estampado floral."),
        ("Zapatos deportivos", 8, 3, 400.0, "disponible", 1, 16, "42", "Zapatos deportivos en buen estado."),       
        ("botella de agua", 20, 1, 100.0, "disponible", 2, 17, "M", "Botella de agua de 500ml en buen estado."),
        ("otroejemplo", 15, 2, 150.0, "disponible", 2, 18, "L", "Otro artículo de prueba.")]
    

    for nombre, cantidad, id_vendedor, precio, estado, id_categoria, id_tipo, talla, comentario in articulos:
        cursor.execute("""
            INSERT INTO articulos (nombre, cantidad_disponible, id_vendedor, precio, estado, id_categoria, id_tipo, talla, comentario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, cantidad, id_vendedor, precio, estado, id_categoria, id_tipo, talla, comentario))
    conexion.commit()
    cursor.close()
    conexion.close()
     
    
def recrear_base_datos():
    crear_conexion()    

def crear_apartar():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE apartados (
            id_apartado INT AUTO_INCREMENT PRIMARY KEY,
            id_vendedor INT NOT NULL,
            id_cliente INT NOT NULL,
            id_articulo INT NOT NULL,
            fecha DATE DEFAULT (CURRENT_DATE),
            precio_apartado FLOAT,
            cantidad INT,
            total FLOAT,
            FOREIGN KEY (id_vendedor) REFERENCES login(id_vendedor),
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
            FOREIGN KEY (id_articulo) REFERENCES articulos(id_articulo)
        );
        """)
    conexion.commit()
    conexion.close()
    print("Tabla de apartados creada correctamente.")

if __name__ == "__main__":
    
   

    print("")


