
#########################
### NE FONCTIONNE PAS ###
#########################

import pandas as pd

lien = "https://datasets.imdbws.com/title.ratings.tsv.gz"
ratings = pd.read_csv(lien, sep="\t")

lien2 = "https://datasets.imdbws.com/title.basics.tsv.gz"
basics = pd.read_csv(lien2, sep="\t", na_values="\\N")

data  = pd.merge (basics, ratings, how='left', on='tconst')
data = data[data['genres'].str.contains("Comedy", na=False)]
data = data[data['titleType'].str.contains("movie", na=False)]

tmdb = pd.read_csv("../data/brute/TMDB_movie_dataset_v11.csv")

data = pd.merge (data, tmdb, how='left', left_on='tconst', right_on='imdb_id')
data[data['startYear'] >= 1980]['numVotes'].mean()
data = data[data['startYear'] >= 1980]
data = data[(data['production_countries'].str.contains("France", na=False)) | ((data['averageRating'] >= 8) & (data['numVotes'] >= 500))]

data.to_csv("../data/propre/film_propre.csv", index=False)