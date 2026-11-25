import pandas as pd
import numpy as np
from pathlib import Path

# Dossier data/propre, trouvé à partir de l'emplacement du script
DOSSIER = Path(__file__).parent.parent / "data" / "propre"

# 1. Lecture
data = pd.read_csv(DOSSIER / "film_propre.csv")
print("Films :", len(data), "| Colonnes :", data.shape[1], "| Doublons :", data["tconst"].duplicated().sum())

# 2. Une seule ligne par film
data = data.sort_values(["tconst", "popularity"], ascending=[True, False])
data = data.drop_duplicates(subset=["tconst"], keep="first")
print("Films :", len(data))

# 3. Colonnes inutiles
data = data.drop(columns=["titleType", "isAdult", "endYear", "tagline", "id",
                          "vote_average", "vote_count", "genres_y", "spoken_languages",
                          "imdb_id", "backdrop_path", "release_date", "homepage", "adult",
                          "status", "runtime", "budget", "revenue", "title", "original_title"])
print("Colonnes :", data.shape[1])

# 4. Titres français
titres_fr = pd.read_csv(DOSSIER / "titres_fr.csv")[["titleId", "titre_fr"]]
data = pd.merge(data, titres_fr, how="left", left_on="tconst", right_on="titleId")
data = data.drop(columns=["titleId"])
print("Films :", len(data), "| Avec titre français :", data["titre_fr"].notna().sum())

# 5. Titre affiché
data["titre_affiche"] = np.where(data["original_language"] == "fr",
                                 data["originalTitle"],
                                 data["primaryTitle"])
data["titre_affiche"] = data["titre_fr"].fillna(data["titre_affiche"])
print("Titres vides :", data["titre_affiche"].isna().sum())

# 6. Ordre et renommage des colonnes
ordre = ["tconst", "titre_affiche", "originalTitle", "primaryTitle",
         "startYear", "runtimeMinutes", "genres_x",
         "averageRating", "numVotes", "popularity",
         "original_language", "production_countries", "production_companies",
         "overview", "keywords", "poster_path"]
data = data[ordre]

data = data.rename(columns={
    "tconst": "id_imdb", "titre_affiche": "titre", "originalTitle": "titre_original",
    "primaryTitle": "titre_principal", "startYear": "annee", "runtimeMinutes": "duree_min",
    "genres_x": "genres", "averageRating": "note_imdb", "numVotes": "nb_votes_imdb",
    "popularity": "popularite_tmdb", "original_language": "langue_originale",
    "production_countries": "pays_production", "production_companies": "societes_production",
    "overview": "resume", "keywords": "mots_cles", "poster_path": "affiche",
})
print("Films :", len(data), "| Colonnes :", data.shape[1])

# 7. Export
data.to_csv(DOSSIER / "film_complet.csv", index=False, encoding="utf-8-sig")
print("Export :", len(data), "films | Doublons :", data["id_imdb"].duplicated().sum())