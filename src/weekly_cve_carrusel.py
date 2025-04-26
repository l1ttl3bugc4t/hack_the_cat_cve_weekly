
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
    if not os.path.isfile(LOGO_PATH):
        raise FileNotFoundError(f"⚠️ No se encontró el logo en {LOGO_PATH}")
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
    if not os.path.isfile(LOGO_PATH):
        raise FileNotFoundError(f"⚠️ No se encontró el logo en {LOGO_PATH}")
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
    if not os.path.isfile(LOGO_PATH):
        raise FileNotFoundError(f"⚠️ No se encontró el logo en {LOGO_PATH}")
    logo = Image.open(LOGO_PATH).convert("RGBA").resize(LOGO_SIZE)
    img.paste(logo, (TAMANO_IMG[0] - LOGO_SIZE[0] - MARGEN_DERECHO, TAMANO_IMG[1] - LOGO_SIZE[1] - 20), logo)
    draw.rectangle([10, 10, TAMANO_IMG[0] - 10, TAMANO_IMG[1] - 10], outline=COLOR_BORDE, width=4)
    img.save(os.path.join(OUTPUT_DIR, f"{index:02d}_cve_slide.png"))

# (continúa: funciones de posteo y main)


def postear_en_linkedin():
    import requests
    import os
    import time

    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    AUTHOR_URN = os.getenv('AUTHOR_URN')

    if not ACCESS_TOKEN:
        print("❌ Falta variable de entorno ACCESS_TOKEN.")
        return

    if not AUTHOR_URN:
        print("⚠️ Advertencia: No se encontró AUTHOR_URN, se usará el perfil asociado al Access Token.")

    imagenes = sorted([
        os.path.join(OUTPUT_DIR, img)
        for img in os.listdir(OUTPUT_DIR)
        if img.endswith('.png')
    ])

    if not imagenes:
        print("⚠️ No hay imágenes para postear en LinkedIn.")
        return

    def registrar_upload(access_token):
        url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [
                    {
                        "identifier": "urn:li:userGeneratedContent",
                        "relationshipType": "OWNER"
                    }
                ],
                "owner": AUTHOR_URN if AUTHOR_URN else None
            }
        }
        body = {k: v for k, v in body.items() if v is not None}
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            upload_info = response.json()
            upload_url = upload_info['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset = upload_info['value']['asset']
            return upload_url, asset
        else:
            raise Exception(f"❌ Error al registrar upload: {response.status_code} {response.text}")

    def subir_imagen(upload_url, image_path):
        headers = {"Content-Type": "application/octet-stream"}
        with open(image_path, "rb") as f:
            response = requests.put(upload_url, headers=headers, data=f)
        if response.status_code not in [200, 201]:
            raise Exception(f"❌ Error al subir imagen: {response.status_code} {response.text}")

    def publicar_carrusel(access_token, asset_list):
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        media = [{"status": "READY", "media": asset} for asset in asset_list]
        payload = {
            "author": AUTHOR_URN if AUTHOR_URN else "urn:li:person:me",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": "🚀 ¡Nuevo resumen semanal de CVEs presentado por Hack the Cat! 🐱💻 #HackTheCat #CyberSecurity #CVEs"},
                    "shareMediaCategory": "IMAGE",
                    "media": media
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            print("✅ Post con imágenes publicado exitosamente en LinkedIn!")
        else:
            raise Exception(f"❌ Error al publicar post: {response.status_code} {response.text}")

    print("🔵 Subiendo imágenes a LinkedIn...")
    asset_ids = []
    for img_path in imagenes:
        print(f"🔵 Registrando y subiendo: {img_path}")
        upload_url, asset = registrar_upload(ACCESS_TOKEN)
        subir_imagen(upload_url, img_path)
        asset_ids.append(asset)
        time.sleep(1)

    print("🟣 Publicando carrusel en LinkedIn...")
    publicar_carrusel(ACCESS_TOKEN, asset_ids)

# === MAIN ===
if __name__ == "__main__":
    cves = obtener_cves()
    if not cves:
        print("⚠️ No se encontraron CVEs para esta semana.")
        exit(0)

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
    pdf.output(os.path.join(OUTPUT_DIR, "carrusel_cves.pdf"))

    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "add", OUTPUT_DIR], check=True)
        subprocess.run(["git", "commit", "-m", "📤 Auto: Añadir carrusel semanal de CVEs"], check=True)
        subprocess.run(["git", "push"], check=True)
    except Exception as e:
        print("⚠️ Error al hacer push del output:", e)

    postear_en_linkedin()
