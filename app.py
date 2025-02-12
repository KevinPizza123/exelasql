import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from sqlalchemy import create_engine, inspect

# Función para seleccionar archivo
def seleccionar_archivo():
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo",
        filetypes=[("Todos los archivos", "*.*")],
        parent=root,
        multiple=False
    )

    if file_path:
        ruta_archivo.set(file_path)  # Mostrar la ruta en la interfaz
        try:
            if file_path.endswith((".xls", ".xlsx")):
                df = pd.read_excel(file_path)
                messagebox.showinfo("Éxito", f"Archivo Excel cargado con {len(df)} registros.")
            else:
                messagebox.showinfo("Archivo seleccionado", f"Seleccionaste: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el archivo.\n{e}")

# Función para conectarse a la base de datos y crear tabla
def cargar_a_sql():
    file_path = ruta_archivo.get()
    if not file_path:
        messagebox.showerror("Error", "Por favor, selecciona un archivo primero.")
        return
    
    db_tipo = combo_db.get()
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()
    db_nombre = entry_db.get()

    if not (usuario and contraseña and db_nombre):
        messagebox.showerror("Error", "Todos los campos de conexión son obligatorios.")
        return

    # Construir la cadena de conexión según la base de datos seleccionada
    if db_tipo == "PostgreSQL":
        db_connection_string = f"postgresql+psycopg2://{usuario}:{contraseña}@localhost:5432/{db_nombre}"
    elif db_tipo == "SQL Server":
        db_connection_string = f"mssql+pyodbc://{usuario}:{contraseña}@localhost/{db_nombre}?driver=SQL+Server"
    else:
        messagebox.showerror("Error", "Selecciona un tipo de base de datos.")
        return

    # Intentar cargar el Excel
    try:
        df = pd.read_excel(file_path)
        sheet_name = os.path.splitext(os.path.basename(file_path))[0]  # Nombre de la tabla igual al archivo
        
        engine = create_engine(db_connection_string)
        inspector = inspect(engine)

        # Verificar si la tabla ya existe
        if inspector.has_table(sheet_name):
            messagebox.showwarning("Aviso", f"La tabla '{sheet_name}' ya existe en la base de datos.")
            return

        # Guardar datos en la base de datos
        df.to_sql(sheet_name, con=engine, index=False, if_exists="fail")
        messagebox.showinfo("Éxito", f"Datos cargados en la tabla '{sheet_name}'.")
    
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar en la base de datos.\n{e}")

# Crear la ventana principal
root = tk.Tk()
root.title("Convertir Excel a SQL")
root.geometry("500x400")

# Variable para mostrar la ruta
ruta_archivo = tk.StringVar()

# Selección de archivo
tk.Label(root, text="Seleccione un archivo:").pack(pady=5)
tk.Button(root, text="Buscar", command=seleccionar_archivo).pack()
tk.Label(root, textvariable=ruta_archivo, wraplength=450, fg="blue").pack(pady=5)

# Tipo de base de datos
tk.Label(root, text="Seleccione la base de datos:").pack(pady=5)
combo_db = ttk.Combobox(root, values=["PostgreSQL", "SQL Server"], state="readonly")
combo_db.pack()
combo_db.set("PostgreSQL")  # Valor por defecto

# Campos de conexión
tk.Label(root, text="Usuario:").pack(pady=2)
entry_usuario = tk.Entry(root)
entry_usuario.pack()

tk.Label(root, text="Contraseña:").pack(pady=2)
entry_contraseña = tk.Entry(root, show="*")
entry_contraseña.pack()

tk.Label(root, text="Nombre de la Base de Datos:").pack(pady=2)
entry_db = tk.Entry(root)
entry_db.pack()

# Botón para cargar en SQL
tk.Button(root, text="Convertir a SQL", command=cargar_a_sql, bg="green", fg="white").pack(pady=10)

# Forzar X11 en Ubuntu si es necesario
if os.environ.get("WAYLAND_DISPLAY"):
    os.environ["GDK_BACKEND"] = "x11"

# Ejecutar la aplicación
root.mainloop()