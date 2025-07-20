from PyPDF2 import PdfReader
from unstructured.partition.auto import partition
import json

# Lecture du fichier PDF pour déterminer si c’est un PDF texte ou scanné
reader = PdfReader("document.pdf")
is_scanned = all(page.extract_text() is None for page in reader.pages)

# Choix de la stratégie en fonction du type
if is_scanned:
    print("📸 PDF scanné détecté — utilisation de l’OCR (hi_res)...")
    elements = partition("document.pdf", strategy="hi_res", languages=["fra"])
else:
    print("📄 PDF texte détecté — extraction rapide (fast)...")
    elements = partition("document.pdf", strategy="fast", languages=["fra"])

# Extraire et concaténer le texte
paragraphs = [el.text.strip() for el in elements if hasattr(el, "text") and el.text.strip()]
full_text = "\n\n".join(paragraphs)

# Sauvegarde dans un fichier JSON
output = {
    "filename": "document.pdf",
    "page_count": len(reader.pages),
    "text": full_text
}

with open("outputPdfReader.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("✅ Extraction terminée et sauvegardée dans output.json")
