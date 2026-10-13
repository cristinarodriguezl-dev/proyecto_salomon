import os
import zipfile


def crear_zip_proyecto(nombre_zip="proyecto_salomon_limpio.zip"):
    # Directorio raíz del proyecto actual
    dir_raiz = os.getcwd()

    # Directorios y archivos que queremos excluir
    exclusiones = {'.venv', '.git', '__pycache__', '.idea', 'dist', 'build'}

    print(f"Comprimiendo proyecto desde: {dir_raiz}")

    with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for carpeta_actual, subcarpetas, archivos in os.walk(dir_raiz):
            # Modificar subcarpetas in situ para evitar que os.walk entre en ellas
            subcarpetas[:] = [d for d in subcarpetas if d not in exclusiones]

            for archivo in archivos:
                # Omitir archivos .env o el propio archivo zip generado
                if archivo == '.env' or archivo.endswith('.zip') or archivo.endswith('.pyc'):
                    continue

                ruta_completa = os.path.join(carpeta_actual, archivo)

                # Calcular ruta relativa para mantener la estructura dentro del ZIP
                ruta_relativa = os.path.relpath(ruta_completa, dir_raiz)

                # Omitir si por alguna razón la ruta relativa empieza con exclusiones
                if any(part in ruta_relativa.split(os.sep) for part in exclusiones):
                    continue

                print(f"Agregando: {ruta_relativa}")
                zipf.write(ruta_completa, ruta_relativa)

    print(f"\n¡Archivo ZIP creado con éxito: {os.path.abspath(nombre_zip)}")


if __name__ == "__main__":
    crear_zip_proyecto()