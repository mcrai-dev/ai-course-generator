from unstructured.partition.auto import partition
import json

# Charger le fichier PDF
elements = partition("document.pdf")

# Extraire uniquement le texte des éléments valides (ayant l'attribut .text)
paragraphs = [el.text.strip() for el in elements if hasattr(el, "text") and el.text.strip()]

# Fusionner les paragraphes en un seul texte bien formaté
full_text = "\n\n".join(paragraphs)

# Construire un JSON propre
output = {
    "filename": "da.pdf",
    "page_count": len(set(el.metadata.page_number for el in elements if hasattr(el.metadata, "page_number"))),
    "text": full_text
}

# Sauvegarder dans un fichier output.json
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print("✅ Texte complet extrait et sauvegardé dans output.json.")
