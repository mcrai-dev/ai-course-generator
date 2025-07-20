import sqlite3
import requests
import sys

API_KEY = ""
MODEL = "meta-llama/llama-3-70b-instruct"
DB_PATH = "corpus.db"


def get_course_text(source, max_chars=2000):
    """
    Récupère le texte concaténé de tous les blocs d'un PDF donné (source), limité à max_chars.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT contenu FROM blocs WHERE source=? ORDER BY page, id", (source,))
    textes = [row[0] for row in c.fetchall()]
    conn.close()
    full_text = " ".join(textes)
    return full_text[:max_chars]


def call_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_quiz_from_course.py <nom_du_pdf>")
        sys.exit(1)
    source = sys.argv[1]
    print(f"Génération de quiz pour le cours : {source}")
    extrait = get_course_text(source)
    consigne = "Génère 5 questions à choix multiple adaptées à un élève visuel. Réponds en français uniquement."
    prompt = f"Voici un extrait du cours {source} :\n{extrait}\n\n{consigne}"
    print("\nPrompt envoyé à l'IA :\n", prompt[:400], "...\n[tronqué]" if len(prompt) > 400 else "")
    resultat = call_openrouter(prompt)
    print("\nRéponse de l'IA :\n")
    print(resultat)

if __name__ == "__main__":
    main()
