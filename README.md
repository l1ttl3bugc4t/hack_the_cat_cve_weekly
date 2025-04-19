# Hack the Cat - CVE Carrusel Generator 🐱

Este proyecto genera un carrusel semanal con los CVEs más relevantes usando datos de NIST.

## Estructura

- `src/`: Contiene el script principal.
- `assets/`: Logos y fuente utilizada para los slides.
- `output/`: Carpeta de salida (se recomienda ignorarla en Git).

## Requisitos

- Python 3
- Librerías:
  - requests
  - fpdf
  - pillow

## Uso

```bash
pip install -r requirements.txt
python src/weekly_cve_carrusel.py
```

Se generará una carpeta `output_XX_XX_XX_XX` con las imágenes del carrusel y un PDF exportado automáticamente.
