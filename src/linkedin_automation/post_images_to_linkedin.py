import requests
import json
import os
import time

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
AUTHOR_URN = os.getenv('AUTHOR_URN')

# Asegúrate que aquí pongas las rutas a los slides que generaste
IMAGES_PATHS = [
    "output_carrusel/slide1.png",
    "output_carrusel/slide2.png",
    "output_carrusel/slide3.png",
    # Agrega aquí los paths correctos a tus slides generados
]

POST_TEXT = "🚀 ¡Aquí está el resumen de vulnerabilidades CVE de la semana! 🔥\n\n#HackTheCat #Ciberseguridad #CVEs"

def registrar_upload(access_token, author_urn):
    url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    body = {
        "registerUploadRequest": {
            "owner": author_urn,
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "serviceRelationships": [
                {
                    "identifier": "urn:li:userGeneratedContent",
                    "relationshipType": "OWNER"
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        upload_info = response.json()
        upload_url = upload_info['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset = upload_info['value']['asset']
        return upload_url, asset
    else:
        raise Exception(f"❌ Error al registrar upload: {response.status_code} {response.text}")

def subir_imagen(upload_url, image_path):
    headers = {
        "Content-Type": "application/octet-stream"
    }
    with open(image_path, "rb") as f:
        response = requests.put(upload_url, headers=headers, data=f)
    if response.status_code not in [200, 201]:
        raise Exception(f"❌ Error al subir imagen: {response.status_code} {response.text}")

def publicar_carrusel(access_token, author_urn, asset_list, texto_post):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    media = [{"status": "READY", "media": asset} for asset in asset_list]
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": texto_post},
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

if __name__ == "__main__":
    if not ACCESS_TOKEN or not AUTHOR_URN:
        raise Exception("❌ Faltan variables de entorno ACCESS_TOKEN o AUTHOR_URN.")
    
    asset_ids = []
    for image_path in IMAGES_PATHS:
        print(f"🔵 Registrando subida de: {image_path}")
        upload_url, asset = registrar_upload(ACCESS_TOKEN, AUTHOR_URN)
        print(f"🟡 Subiendo imagen: {image_path}")
        subir_imagen(upload_url, image_path)
        asset_ids.append(asset)
        time.sleep(1)  # Pequeña pausa

    print("🟣 Publicando post con todas las imágenes...")
    publicar_carrusel(ACCESS_TOKEN, AUTHOR_URN, asset_ids, POST_TEXT)
