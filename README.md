# Générateur de Diagrammes UML et Explications Pédagogiques

Ce projet permet d'extraire du contenu de cours PDF, de générer des diagrammes UML (ou autres) à partir du texte, et d'obtenir automatiquement une explication pédagogique détaillée grâce à l'IA (OpenAI GPT-4).

## Fonctionnalités
- Extraction de blocs de texte depuis des PDF et stockage dans une base SQLite.
- Génération de diagrammes (UML, mindmap, etc.) à partir de requêtes en langage naturel.
- Appel à l'API OpenAI pour obtenir à la fois le code DOT Graphviz et une explication pédagogique en français.
- Génération de fichiers SVG pour les diagrammes et de fichiers texte pour les explications.

## Installation

1. **Cloner le dépôt ou copier les fichiers.**
2. **Créer un environnement virtuel Python (optionnel mais recommandé) :**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```
4. **Installer Graphviz (binaire système) :**
   - Sous Ubuntu/Debian :
     ```bash
     sudo apt install graphviz
     ```
   - Sous Mac :
     ```bash
     brew install graphviz
     ```

5. **Configurer la clé OpenAI :**
   - Copier votre clé API OpenAI dans un fichier `.env` à la racine du projet :
     ```env
     OPENAI_API_KEY=sk-...
     ```

## Utilisation

Générer un diagramme UML et une explication pédagogique à partir d'un PDF :

```bash
python3 generer_visuel.py <nom_du_pdf> "<votre question ou requête>"
```

- Le diagramme sera généré dans `output_diagramme.svg`.
- L'explication pédagogique sera sauvegardée dans `output_explanation.txt`.

**Exemple :**
```bash
python3 generer_visuel.py JavaLesBases.pdf "Génère un diagramme de classes UML pour les collections et explique chaque classe."
```

## Dépendances
- Python 3.8+
- openai==0.28.0
- graphviz
- python-dotenv

## Conseils
- Pour de meilleurs résultats, posez des questions précises et pédagogiques.
- Vérifiez que le binaire `dot` de Graphviz est bien installé sur votre système.
- Ouvrez les fichiers SVG dans un navigateur moderne pour un rendu optimal.

## Licence
Projet éducatif, open source.
# ai-course-generator
