import sqlite3
import os
import sys
import openai
from graphviz import Source
import re
from dotenv import load_dotenv

# Charge automatiquement les variables d'environnement depuis .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"
DB_PATH = "corpus.db"

# Prompts pour différents types de diagrammes
DIAGRAM_PROMPTS = {
    "class": (
        "Tu es un assistant qui génère des diagrammes de classes UML en syntaxe Graphviz (DOT). "
        "Utilise des noeuds de type 'record' avec les attributs et méthodes formatés. "
        "Réponds uniquement avec le code DOT, sans explication ni balises."
    ),
    "mindmap": (
        "Tu es un assistant qui génère des cartes mentales (mindmaps) en syntaxe DOT de Graphviz. "
        "Chaque idée centrale doit être liée à ses sous-idées. Utilise un style simple et clair. "
        "Réponds uniquement avec le code DOT, sans explication ni balises."
    ),
    "flowchart": (
        "Tu es un assistant qui génère des organigrammes (flowcharts) en syntaxe DOT de Graphviz. "
        "Utilise des boîtes (shape=box), des décisions (diamond), et des flèches pour les flux. "
        "Réponds uniquement avec le code DOT, sans explication ni balises."
    ),
    "graph": (
        "Tu es un assistant qui génère des graphes relationnels ou conceptuels en syntaxe DOT de Graphviz. "
        "Relie les concepts entre eux de façon logique. Réponds uniquement avec le code DOT, sans explication ni balises."
    )
}

def get_course_text(source, max_chars=2000):
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

def detect_diagram_type(user_input: str) -> str:
    input_lower = user_input.lower()
    if any(w in input_lower for w in ["classe", "attribut", "méthode", "objet", "uml"]):
        return "class"
    elif any(w in input_lower for w in ["étapes", "processus", "flux", "organigramme"]):
        return "flowchart"
    elif any(w in input_lower for w in ["concept", "idée", "relation", "carte mentale", "mindmap"]):
        return "mindmap"
    else:
        return "graph"

def generate_diagram(diagram_type: str, user_request: str) -> str:
    if diagram_type not in DIAGRAM_PROMPTS:
        raise ValueError(f"Type de diagramme '{diagram_type}' non supporté.")
    system_prompt = DIAGRAM_PROMPTS[diagram_type]
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY n'est pas défini dans les variables d'environnement.")
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ],
        temperature=0.3
    )
    return response.choices[0].message['content'].strip()

def clean_dot_labels(dot_code: str) -> str:
    # Nettoie les labels de type <{...}> ou label="<{...}>"
    dot_code = re.sub(r'label="\s*<\{([^}]*)\}>"', r'label="{\1}"', dot_code)
    dot_code = re.sub(r'<\{([^}]*)\}>', r'{\1}', dot_code)
    dot_code = re.sub(r'<f\d+>', '', dot_code)
    dot_code = re.sub(r'label=\[', 'label={', dot_code)
    dot_code = re.sub(r'\];', '};', dot_code)
    dot_code = re.sub(r'label="([^"]+)"', lambda m: f'label="{{{m.group(1)}}}"' if not m.group(1).startswith('{') else m.group(0), dot_code)
    dot_code = re.sub(r'\|\s*-', '|_', dot_code)
    dot_code = dot_code.replace('\\n', '\\l')
    dot_code = dot_code.replace('<', '').replace('>', '')
    dot_code = re.sub(r'\|\s*}', '}', dot_code)
    # Corrige les flèches façon IA
    dot_code = re.sub(r'class\s+([A-Za-z0-9_]+)->([A-Za-z0-9_]+)(\[label=.*?\];)', r'\1 -> \2\3', dot_code)
    # Corrige les définitions de nœuds façon IA
    dot_code = re.sub(r'class\s+([A-Za-z0-9_]+)\[', r'\1[', dot_code)
    return dot_code

def apply_default_style(dot_code: str, dpi: int = 300) -> str:
    # Ajoute des options pour éviter la coupure et améliorer la lisibilité
    lines = dot_code.splitlines()
    for i, line in enumerate(lines):
        if '{' in line:
            lines.insert(i+1, '    rankdir=LR;')
            lines.insert(i+2, '    overlap=false;')
            lines.insert(i+3, '    splines=true;')
            break
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: python generer_visuel.py <nom_du_pdf> <requete utilisateur>")
        sys.exit(1)
    source = sys.argv[1]
    user_input = sys.argv[2]
    print(f"Génération de diagramme pour : {source}\nRequête : {user_input}")
    extrait = get_course_text(source)
    diagram_type = detect_diagram_type(user_input)
    # Ajoute une consigne pédagogique explicite
    pedagogic_instruction = "Après le code DOT, fournis une explication pédagogique détaillée (en français) des classes, héritages, et relations du diagramme pour un débutant."
    user_request = f"À partir de ce contenu : {extrait}\n\n{user_input}\n\n{pedagogic_instruction}"
    full_response = generate_diagram(diagram_type, user_request)

    # Extraction du code DOT et de l'explication
    import re
    dot_match = re.search(r'```dot(.*?)```', full_response, re.DOTALL)
    if dot_match:
        dot_code = dot_match.group(1).strip()
        explanation = full_response.replace(dot_match.group(0), '').strip()
    else:
        # Fallback : tout le texte est mis en DOT
        dot_code = full_response.strip()
        explanation = ''

    dot_clean = "\n".join(line for line in dot_code.strip().splitlines() if not line.strip().startswith("```"))
    dot_styled = apply_default_style(dot_clean)
    src = Source(dot_styled)
    print("\n--- CODE DOT GÉNÉRÉ ---\n")
    print(dot_code)
    print("\n------------------------\n")
    svg_output = src.pipe(format="svg").decode("utf-8")
    with open("output_diagramme.svg", "w", encoding="utf-8") as f:
        f.write(svg_output)
    print("\n✅ Diagramme SVG généré dans output_diagramme.svg")
    if explanation:
        print("\n--- EXPLICATION PÉDAGOGIQUE ---\n")
        print(explanation)
        print("\n-------------------------------\n")
        with open("output_explanation.txt", "w", encoding="utf-8") as f:
            f.write(explanation)
        print("\n✅ Explication pédagogique enregistrée dans output_explanation.txt")

if __name__ == "__main__":
    main()
