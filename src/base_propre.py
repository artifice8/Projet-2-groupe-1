from pathlib import Path
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent

data = pd.read_csv(RACINE/"data"/"brute"/"film.csv")
data = data[data['adult'] == 0]

data.to_csv(RACINE/"data"/"propre"/"film_propre.csv", index=False)