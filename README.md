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

# Merge des 2 fichiers csv propre (film_propre et titre_fr)
film_complet = pd.merge(data, data2, how="left", left_on="tconst", right_on='titleId')

# Verification du même nombre de film entre notre base de donnée initial et la nouvelle base après le merge, toujours 3105 films
print(data.shape, film_complet.shape)

# Suppression des colonnes inutiles pour notre analyse
film_complet = film_complet.drop(columns=['region', 'isOriginalTitle', 'ordering', 'types', 'titleId'])

# Export du fichier propre : film_complet
film_complet.to_csv("../data/propre/film_complet.csv", index=False)
```