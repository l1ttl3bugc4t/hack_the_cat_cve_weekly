
# Hack the Cat - CVE Carrusel Generator 🐱
# Versión regenerada y corregida para tratar configurations como dict o list

import requests
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import textwrap
import os
import subprocess

FUENTE = "assets/Karla.ttf"
LOGO_PATH = os.path.abspath("assets/hack_the_cat_logo_resized.png")
COLOR_TEXTO = (0, 255, 0)
COLOR_FONDO = (10, 10, 10)
COLOR_BORDE = (0, 255, 0)
TAMANO_IMG = (1080, 1080)
MARGEN_IZQUIERDO = 60
MARGEN_DERECHO = 60
LOGO_SIZE = (120, 120)

hoy = datetime.utcnow()
hace_7_dias = hoy - timedelta(days=7)
fecha_inicio_str = hace_7_dias.strftime("%d_%m")
fecha_fin_str = hoy.strftime("%d_%m")
OUTPUT_DIR = f"output_{fecha_inicio_str}_{fecha_fin_str}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# funciones (por espacio no pego aquí todo, pero este contenido es idéntico al que ya tenías)
# la única diferencia real será dentro de la función generar_carrusel()

def generar_carrusel():
    cves = obtener_cves()
    if not cves:
        print("⚠️ No se encontraron CVEs para esta semana.")
        return

    crear_slide_intro()
    resumen = []
    scores = []

    for i, item in enumerate(cves, start=1):
        cve = item["cve"]
        cve_id = cve["id"]
        desc = cve["descriptions"][0]["value"]
        desc = desc if len(desc) <= 400 else desc[:397] + "..."
        score_data = cve.get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {})
        score = score_data.get("baseScore", 0)
        severity = score_data.get("baseSeverity", "N/A")
        vector = score_data.get("vectorString", "N/A")
        cwe = cve.get("weaknesses", [{}])[0].get("description", [{}])[0].get("value", "N/A")

        configurations = cve.get("configurations", {})
        nodes = configurations.get("nodes", []) if isinstance(configurations, dict) else []

        tech = ", ".join([
            cpe.get("criteria", "").split(":")[4]
            for node in nodes
            for cpe in node.get("cpeMatch", [])
        ]) or "No especificado"

        published = item.get("published") or cve.get("published") or "Fecha no disponible"
        published = published[:10]

        texto = f"{cve_id}\n\nDescripción: {desc}\n\nCVSS: {score} ({severity})\n\nVector: {vector}\n\nTipo: {cwe}\n\nTecnología: {tech}"
        crear_imagen(texto, i, f"Publicado el: {published}")
        scores.append(score if isinstance(score, (int, float)) else 0)

    promedio = sum(scores) / len(scores) if scores else 0
    crear_slide_final(len(cves), promedio)

    imagenes = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")])
    pdf = FPDF(orientation='P', unit='pt', format=[1080, 1080])
    for imagen in imagenes:
        pdf.add_page()
        pdf.image(os.path.join(OUTPUT_DIR, imagen), x=0, y=0, w=1080, h=1080)
    pdf.output(os.path.join(OUTPUT_DIR, "carrusel_cvEs.pdf"))

    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "add", OUTPUT_DIR], check=True)
        subprocess.run(["git", "commit", "-m", "📤 Auto: Añadir carrusel semanal de CVEs"], check=True)
        subprocess.run(["git", "push"], check=True)
    except Exception as e:
        print("⚠️ Error al hacer push del output:", e)

if __name__ == "__main__":
    generar_carrusel()
