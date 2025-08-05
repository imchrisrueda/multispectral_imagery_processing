import os
import subprocess
import json
import pandas as pd

def extraer_altitud_exiftool(ruta_imagen):
    try:
        comando = ['exiftool', '-j', '-GPSAltitude', '-AbsoluteAltitude', ruta_imagen]
        resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
        metadata = json.loads(resultado.stdout)[0]
        alt = metadata.get('GPSAltitude') or metadata.get('AbsoluteAltitude')
        if isinstance(alt, str) and ' m' in alt:
            alt = float(alt.replace(' m', ''))
        return float(alt) if alt is not None else None
    except Exception as e:
        print(f"Error con {ruta_imagen}: {e}")
        return None

def procesar_directorio(directorio):
    datos = []
    altitud_anterior = None
    archivos = sorted([f for f in os.listdir(directorio) if f.lower().endswith(('.jpg', '.tif', '.tiff'))])
    print(f"Procesando {len(archivos)} imágenes...")

    for archivo in archivos:
        ruta = os.path.join(directorio, archivo)
        altitud = extraer_altitud_exiftool(ruta)

        if altitud is not None and altitud_anterior is not None:
            estado = "Cambio >10m" if abs(altitud - altitud_anterior) > 10 else "OK"
        else:
            estado = "Sin comparación" if altitud_anterior is None else "Altitud no disponible"

        datos.append({
            "Archivo": archivo,
            "Altitud (m)": round(altitud, 2) if altitud is not None else "No disponible",
            "Estado": estado
        })

        if altitud is not None:
            altitud_anterior = altitud

    return pd.DataFrame(datos)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Lectura robusta de altitud con exiftool")
    parser.add_argument("directorio", help="Ruta al directorio con imágenes")
    args = parser.parse_args()

    tabla = procesar_directorio(args.directorio)
    print(tabla.to_string(index=False))
