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


## Préparation du catalogue final

**Code :** `notebook/preparation_catalogue_final.ipynb` (version détaillée) et
`notebook/preparation_catalogue_final.py` (code seul).

**Entrée :** `data/propre/film_propre.csv` (films filtrés, joints avec TMDB) + `data/propre/titres_fr.csv`
**Sortie :** `data/propre/film_complet.csv` (catalogue final : une ligne par film, sans doublon)

**Lancer le script** depuis la racine du projet :

```bash
python notebook/preparation_catalogue_final.py
```

### Les étapes

1. **Lecture** du fichier de films filtrés.
2. **Une seule ligne par film** : si TMDB a plusieurs fiches pour un même film, on garde la plus populaire.
3. **Colonnes inutiles** : suppression des doublons IMDb/TMDB (on garde IMDb, qui a servi aux filtres),
   des colonnes majoritairement vides et de celles sans utilité pour le projet.
4. **Titres français** : jointure avec `titres_fr.csv`, issu du fichier IMDb `title.akas`
   (filtré sur la région FR, et non sur la langue, pour éviter les titres québécois).
5. **Titre affiché** : titre français s'il existe ; sinon titre original pour un film français ;
   sinon titre principal IMDb.
6. **Ordre et renommage** des colonnes en français, avec la source (`_imdb`, `_tmdb`) si besoin.
7. **Export** de `film_complet.csv`.

### Résultat

| Contrôle | Valeur |
|---|---|
| Films | 3 508 |
| Colonnes | 16 |
| Doublons | 0 |
| Films avec un titre français | 2 814 (80 %) |

### Colonnes de `film_complet.csv`

| Colonne | Source | Description |
|---|---|---|
| `id_imdb` | IMDb | identifiant unique du film |
| `titre` | IMDb (title.akas) + règle | titre affiché |
| `titre_original` | IMDb | titre dans la langue d'origine |
| `titre_principal` | IMDb | titre principal, souvent en anglais |
| `annee` | IMDb | année de sortie |
| `duree_min` | IMDb | durée en minutes |
| `genres` | IMDb | jusqu'à 3 genres, séparés par des virgules |
| `note_imdb` | IMDb | note moyenne sur 10 |
| `nb_votes_imdb` | IMDb | nombre de votants |
| `popularite_tmdb` | TMDB | score de popularité |
| `langue_originale` | TMDB | langue d'origine du film |
| `pays_production` | TMDB | pays de production |
| `societes_production` | TMDB | sociétés de production |
| `resume` | TMDB | résumé du film (en anglais) |
| `mots_cles` | TMDB | mots-clés décrivant le film |
| `affiche` | TMDB | fin de l'adresse de l'affiche (après `https://image.tmdb.org/t/p/w500`) |

### Limites

- 694 films (20 %) n'ont pas de titre français : ils gardent leur titre original ou leur titre principal IMDb.
- La langue d'origine vient de TMDB : si elle est absente, le film prend le titre principal.