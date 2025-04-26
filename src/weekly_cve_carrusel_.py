
import requests
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import textwrap
import os
import subprocess
import time

# === Configuración General ===
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

# === Funciones de generación de contenido ===
def obtener_cves():
    inicio = hace_7_dias.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    fin = hoy.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?pubStartDate={inicio}&pubEndDate={fin}&cvssV3Severity=CRITICAL&cvssV3Severity=HIGH"
    headers = {"User-Agent": "HackTheCatBot/1.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("vulnerabilities", [])[:5]
    except Exception as e:
        print(f"❌ Error al obtener los CVEs: {e}")
        return []

def crear_slide_intro():
    img = Image.new("RGB", TAMANO_IMG, COLOR_FONDO)
    draw = ImageDraw.Draw(img)
    font_title = ImageFont.truetype(FUENTE, 72)
    font_sub = ImageFont.truetype(FUENTE, 48)
    font_phrase = ImageFont.truetype(FUENTE, 40)
    fecha = f"{hace_7_dias.strftime('%d/%m/%Y')} al {hoy.strftime('%d/%m/%Y')}"
    textos = [
        ("CVEs más relevantes de la semana", font_title),
        (f"Del {fecha}", font_sub),
        ("Porque el primer paso para defender es conocer las amenazas.", font_phrase)
    ]
    total_height = sum(draw.textbbox((0, 0), t[0], font=t[1])[3] + 40 for t in textos)
    y = (TAMANO_IMG[1] - total_height) // 2
    for linea, font in textos:
        bbox = draw.textbbox((0, 0), linea, font=font)
        x = (TAMANO_IMG[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), linea, font=font, fill=COLOR_TEXTO)
        y += bbox[3] + 40
    logo = Image.open(LOGO_PATH).convert("RGBA").resize((160, 160))
    img.paste(logo, (TAMANO_IMG[0] - 180, TAMANO_IMG[1] - 180), logo)
    draw.rectangle([10, 10, TAMANO_IMG[0] - 10, TAMANO_IMG[1] - 10], outline=COLOR_BORDE, width=4)
    img.save(os.path.join(OUTPUT_DIR, "00_intro_slide.png"))

def crear_slide_final(total, promedio):
    img = Image.new("RGB", TAMANO_IMG, COLOR_FONDO)
    draw = ImageDraw.Draw(img)
    font_main = ImageFont.truetype(FUENTE, 60)
    font_small = ImageFont.truetype(FUENTE, 48)
    textos = [
        ("Resumen del Reporte", font_main),
        (f"CVEs analizados: {total}", font_small),
        (f"Promedio CVSS: {promedio:.2f}", font_small),
        ("Fuente: nvd.nist.gov", font_small),
        ("Nos vemos la próxima semana. Hack the Cat 🐾", font_small)
    ]
    total_height = sum(draw.textbbox((0, 0), t[0], font=t[1])[3] + 40 for t in textos)
    y = (TAMANO_IMG[1] - total_height) // 2
    for linea, font in textos:
        bbox = draw.textbbox((0, 0), linea, font=font)
        x = (TAMANO_IMG[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), linea, font=font, fill=COLOR_TEXTO)
        y += bbox[3] + 40
    logo = Image.open(LOGO_PATH).convert("RGBA").resize((160, 160))
    img.paste(logo, (TAMANO_IMG[0] - 180, TAMANO_IMG[1] - 180), logo)
    draw.rectangle([10, 10, TAMANO_IMG[0] - 10, TAMANO_IMG[1] - 10], outline=COLOR_BORDE, width=4)
    img.save(os.path.join(OUTPUT_DIR, f"{total+1:02d}_summary_slide.png"))

def crear_imagen(texto, index, fecha_publicacion):
    img = Image.new("RGB", TAMANO_IMG, COLOR_FONDO)
    draw = ImageDraw.Draw(img)
    font_title = ImageFont.truetype(FUENTE, 48)
    font_body = ImageFont.truetype(FUENTE, 36)
    font_fecha = ImageFont.truetype(FUENTE, 28)

    secciones = texto.strip().split("\n\n")
    bloques = []
    total_height = 0

    for i, bloque in enumerate(secciones):
        font = font_title if i == 0 else font_body
        lineas = textwrap.wrap(bloque, width=66)
        bloque_lines = []
        for linea in lineas:
            bbox = draw.textbbox((0, 0), linea, font=font)
            height = bbox[3] - bbox[1]
            bloque_lines.append((linea, font, height))
            total_height += height + 16
        total_height += 40
        bloques.append(bloque_lines)

    bbox_fecha = draw.textbbox((0, 0), fecha_publicacion, font=font_fecha)
    total_height += bbox_fecha[3] - bbox_fecha[1] + 20

    y_text = (TAMANO_IMG[1] - total_height) // 2

    for bloque in bloques:
        for line, font, height in bloque:
            draw.text((MARGEN_IZQUIERDO, y_text), line, font=font, fill=COLOR_TEXTO)
            y_text += height + 16
        y_text += 40

    draw.text((MARGEN_IZQUIERDO, y_text), fecha_publicacion, font=font_fecha, fill=COLOR_TEXTO)
    logo = Image.open(LOGO_PATH).convert("RGBA").resize(LOGO_SIZE)
    img.paste(logo, (TAMANO_IMG[0] - LOGO_SIZE[0] - MARGEN_DERECHO, TAMANO_IMG[1] - LOGO_SIZE[1] - 20), logo)
    draw.rectangle([10, 10, TAMANO_IMG[0] - 10, TAMANO_IMG[1] - 10], outline=COLOR_BORDE, width=4)
    img.save(os.path.join(OUTPUT_DIR, f"{index:02d}_cve_slide.png"))

# (continúa en el siguiente bloque...)
