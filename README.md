# Projet 2 : appel à projets du CNC — un cinéma et son moteur de recommandation

En équipe, nous répondons à un appel à projets du CNC pour ouvrir un cinéma : où, pour quel public, avec quels films.

Le projet comprend une présentation, un tableau de bord de notre catalogue de films, et une application de recommandation qui fait découvrir ce catalogue au public. Il est construit en quatre semaines à partir des bases réelles IMDb et TMDB.

## Données

- **IMDb** : https://datasets.imdbws.com/ (title.basics, title.ratings, title.akas, title.principals, name.basics)
- **TMDB** : fichier trop lourd pour GitHub (~600 Mo)

Les fichiers bruts ne sont jamais modifiés. Les fichiers transformés par notre code sont dans `data/propre/`.

Les données de "film.csv" ont été obtenue via IMDb et TMDB et transformées dans google collab afin de les réduire et pouvoire les utiliser dans VScode.

## Transformation des données

Les données contennaient 12 997 011 films
On les a filtrées pour qu'elles correspondent à ce que nous voulions proposer dans notre cinéma. On a commencé par trier sur la colonne `genres` pour n'avoir que des `Comedy`. On a réduit à 2 495 129 films.
Puis, on a filtrer pour retirer les séries et les courts-métrages et n'avoir que des films. On a donc prix uniquement les `movie` de la colonne `titleType`, ce qui nous a amené à 126 748 films.
Après un merge avec la base TMDB, on a choisi de garder que les films sortis après 1965 en filtrant sur `startYear`. Notre base à donc été réduite à 91 607 films.
Enfin, on a pris uniquement les films de production française, colone `production_countries` contient `France` ou les films internationnaux qui ont une note supérieure ou égale à 8 (`averageRating`) et un nombre de vote supérieur à 500 (`numVotes`) afin de ne conserver que les meilleurs films internationnaux. On arrive donc à 4500 films. On a fait ce choix car pour nous le plus important est d'être un cinéma qui fait de la comédie française. Avoir des films internationnaux est possible, mais on ne souhaite avoir que le meilleur, ce que les gens ont préféré en internationnal, pour leur permettre derrière de découvrir des comédies françaises qui correspondent à leurs attentes.
On a décidé de considéré "comédie française" toutes les comédies qui ont une porduction tout ou partie française. Un film internationnal mais qui est co-produit français/USA, on le considère de production française.
On a également retiré tous les films pour adultes noté dans les deux bases (colonnes `adult == 0` et colonne `isAdult == 0`), ce qui nous donne 4393 films, et on a retiré les films dont la note moyenne était en dessous de 5 (`averageRating`) ce qui nous amène à un total de 3677 films.

Enfin, on a retirés tous les doublons qu'on a repéré sur la colonne `tconst` ce qui nous amène à un total final de 3508 films.

Notre cinéma se veut familial, on a donc retiré tous les films "pour adulte", cependant nous pensons que des films interdits au moins de 10 ou 12 ans ne doivent pas être exclus de notre catalogue. La plupart de nos films sont pour tout publique, il ne nous semble pas que si certains sont pour les plus grands il faille les retirer.

## Avancement

## US02 — Titres français

## Titres français et catalogue final

Objectif : produire `data/propre/film_complet.csv`, le catalogue utilisé par le tableau de bord
et l'application, avec pour chaque film le titre sous lequel il est connu en France.

### Étape 1 : extraire les titres français (`titres_fr.csv`)

Source : le fichier IMDb `title.akas`, qui liste les titres de chaque film dans chaque pays
(le fichier TMDB ne contient pas de titre français).

- `region == "FR"` plutôt que `language == "fr"`, qui donne surtout des titres québécois ;
- `types == "imdbDisplay"` : le titre officiellement affiché ;
- un seul titre par film, pour ne pas créer de doublons lors de la jointure.

```python
# Garder uniquement les titres utilisés en France et officiels
akas_fr = title_akas[(title_akas["region"] == "FR") & (title_akas["types"] == "imdbDisplay")][["titleId", "title", "types", "ordering", "region", "isOriginalTitle"]]

# Trier par film, puis par ordering, pour départager les doublons
akas_fr = akas_fr.sort_values(["titleId", "ordering"])

# Garder un seul titre par film
akas_fr = akas_fr.drop_duplicates(subset=["titleId"], keep="first")

# Renommer la colonne pour éviter la confusion avec le "title" de TMDB
akas_fr = akas_fr.rename(columns={"title": "titre_fr"})

# Exporter le fichier des titres français
akas_fr.to_csv("data/propre/titres_fr.csv", index=False)
```

### Étape 2 : construire le catalogue final (`film_complet.csv`)

Point de départ : `data`, les films filtrés (IMDb) déjà joints avec TMDB.

**1. Supprimer les colonnes inutiles ou en double**

- doublons IMDb / TMDB (titres, votes, durée, date, genres, identifiants) : nous gardons la version IMDb,
  qui a servi à nos filtres. Les genres IMDb et TMDB divergent sur 502 films ;
- `budget` et `revenue` : à 0 pour plus de 85 % des films ;
- colonnes sans utilité pour le projet (`homepage`, `backdrop_path`, `tagline`…).

```python
data = data.drop(columns=["titleType", "isAdult", "endYear", "tagline", "id",
                          "vote_average", "vote_count", "genres_y", "spoken_languages",
                          "imdb_id", "backdrop_path", "release_date", "homepage", "adult",
                          "status", "runtime", "budget", "revenue", "title", "original_title"])
```

**2. Ajouter le titre français**

```python
titres_fr = pd.read_csv("../data/propre/titres_fr.csv")
titres_fr = titres_fr[["titleId", "titre_fr"]]

# left : conserver tous les films, même sans titre français
data = pd.merge(data, titres_fr, how="left", left_on="tconst", right_on="titleId")
data = data.drop(columns=["titleId"])
```

**3. Créer le titre affiché**

Règle : le titre français s'il existe ; sinon le titre original pour un film français ;
sinon le titre principal IMDb.

```python
import numpy as np

# Titre de secours : titre original si le film est en français, sinon titre principal
data["titre_affiche"] = np.where(data["original_language"] == "fr",
                                 data["originalTitle"],
                                 data["primaryTitle"])

# Remplacer par le titre français quand il existe
data["titre_affiche"] = data["titre_fr"].fillna(data["titre_affiche"])
```

**4. Ranger, renommer et exporter**

```python
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

data.to_csv("../data/propre/film_complet.csv", index=False, encoding="utf-8-sig")
```

**5. Supprimer les doublons**

TMDB contient parfois plusieurs fiches pour un même film : la jointure avait créé 169 doublons.
Les colonnes IMDb sont identiques, seules les colonnes TMDB diffèrent. Les fiches en trop ont
une popularité de 0 et sont souvent incomplètes (sans résumé, parfois avec une langue fausse).
Nous gardons, pour chaque film, la fiche TMDB la plus populaire.

```python
film = pd.read_csv("../data/propre/film_complet.csv")

# Pour chaque film, placer la fiche TMDB la plus populaire en premier
film = film.sort_values(["id_imdb", "popularite_tmdb"], ascending=[True, False])

# Garder une seule ligne par film
film = film.drop_duplicates(subset=["id_imdb"], keep="first")

# Vérifier : 0 doublon
print(film["id_imdb"].duplicated().sum())

film.to_csv("../data/propre/film_complet.csv", index=False, encoding="utf-8-sig")
```

### Résultat

- **2 936 films** (3 105 lignes avant suppression des 169 doublons), **16 colonnes**
- **Une ligne par film, sans doublon**