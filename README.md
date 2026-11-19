# Projet 2 : appel à projets du CNC — un cinéma et son moteur de recommandation

En équipe, nous répondons à un appel à projets du CNC pour ouvrir un cinéma : où, pour quel public, avec quels films.

Le projet comprend une présentation, un tableau de bord de notre catalogue de films, et une application de recommandation qui fait découvrir ce catalogue au public. Il est construit en quatre semaines à partir des bases réelles IMDb et TMDB.

## Données

- **IMDb** : https://datasets.imdbws.com/ (title.basics, title.ratings, title.akas, title.principals, name.basics)
- **TMDB** : fichier trop lourd pour GitHub (~600 Mo)

Les fichiers bruts ne sont jamais modifiés. Les fichiers transformés par notre code sont dans `data/propre/`.

## Transformation des données

Les données ont été filtrées pour correspondre à ce que nous voulions proposer dans notre cinéma. On a commencé par trier sur la colonne `genres` pour n'avoir que des `Comedy`. Puis, on a filtrer pour retirer les séries et les courts-métrages et n'avoir que des films. On a donc prix uniquement les `movie` de la colonne `titleType`.
Après un merge avec la base TMDB, on a choisi de garder que les films sortis après 1980 en filtrant sur `startYear`. Enfin, on a pris uniquement les films de production française, colone `production_countries` contient `France` ou les films internationnaux qui ont une note supérieure ou égale à 8 (`averageRating`) et un nombre de voet supérieur à 500 (`numVotes`) afin de ne conserver que les meilleurs films internationnaux.
On a également retiré tous les films pour adultes noté dans les deux bases (colonnes `adult == 0` et colonne `isAdult == 0`), et on a retiré les films dont la note moyenne était en dessous de 5 (`averageRating`)

## Avancement

## US02 — Titres français 

**Objectif :** afficher les films sous leur titre français (*Les Évadés* plutôt que *The Shawshank Redemption*).

**Démarche :**

1. Les titres par pays se trouvent dans `title.akas`. Le filtre porte sur `region == "FR"` et non sur la langue : les titres marqués en langue `fr` sont surtout québécois.
2. Seuls les titres officiels (`types == "imdbDisplay"`) sont conservés, car ce sont les plus fiables.
3. 637 films avaient plusieurs titres officiels (souvent des ressorties de films anciens). Un seul titre est gardé par film, départagé par la colonne `ordering`.
4. Résultat exporté dans `data/propre/titres_fr.csv`.

**Code :**

```python
# Je garde uniquement les titres utilisés en France (region == "FR") et officiels (types == "imdbDisplay")
akas_fr = title_akas[(title_akas["region"] == "FR") & (title_akas["types"] == "imdbDisplay")][["titleId", "title", "types", "ordering"]]

# Je trie par titleId, puis par ordering (numéro de ligne IMDb) pour départager les doublons
akas_fr = akas_fr.sort_values(["titleId", "ordering"])

# Je supprime les doublons en gardant le premier titre de chaque film
akas_fr = akas_fr.drop_duplicates(subset=["titleId"], keep="first")

# Je renomme la colonne pour éviter la confusion avec le "title" de TMDB
akas_fr = akas_fr.rename(columns={"title": "titre_fr"})

# Export du fichier propre
akas_fr.to_csv("data/propre/titres_fr.csv", index=False)
```

**Prochaine étape :** rattacher ces titres au catalogue, avec un titre de secours quand aucun titre français officiel n'existe :

1. titre français officiel (`imdbDisplay`) ;
2. sinon, pour un film d'origine française (`original_language == "fr"`), le titre original (`originalTitle`) ;
3. sinon, le titre IMDb (`primaryTitle`).