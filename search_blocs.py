import sqlite3

def search_blocs(keyword, source=None, bloc_type=None, db_path="corpus.db"):
    """
    Recherche les blocs contenant un mot-clé, éventuellement filtrés par source (PDF) et/ou type de bloc.
    Retourne une liste de dictionnaires.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query = "SELECT id, source, page, bloc_type, contenu FROM blocs WHERE contenu LIKE ?"
    params = [f"%{keyword}%"]
    if source:
        query += " AND source = ?"
        params.append(source)
    if bloc_type:
        query += " AND bloc_type = ?"
        params.append(bloc_type)
    c.execute(query, params)
    results = [
        {
            "id": row[0],
            "source": row[1],
            "page": row[2],
            "bloc_type": row[3],
            "contenu": row[4],
        }
        for row in c.fetchall()
    ]
    conn.close()
    return results

if __name__ == "__main__":
    # Exemples d'utilisation
    print("Recherche de 'probabilité' dans tous les PDF :")
    for bloc in search_blocs("probabilité"):
        print(f"- [{bloc['source']}][page {bloc['page']}][{bloc['bloc_type']}] {bloc['contenu'][:80]}...")

    print("\nRecherche de 'énergie' dans physique.pdf :")
    for bloc in search_blocs("énergie", source="physique.pdf"):
        print(f"- [page {bloc['page']}][{bloc['bloc_type']}] {bloc['contenu'][:80]}...")

    print("\nRecherche de paragraphes contenant 'code' dans JavaLesBases.pdf :")
    for bloc in search_blocs("main", source="JavaLesBases.pdf", bloc_type=""):
        print(f"- [page {bloc['page']}] {bloc['contenu'][:80]}...")
