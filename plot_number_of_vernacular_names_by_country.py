from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import geopandas as gpd

language_to_iso2 = {
    "albanian": "AL",
    "belarusian": "BY",
    "bosnian": "BA",
    "bulgarian": "BG",
    "croatian": "HR",
    "czech": "CZ",
    "danish": "DK",
    "dutch": "NL",
    "english": "GB",
    "estonian": "EE",
    "finnish": "FI",
    "french": "FR",
    "german": "DE",
    "greek": "GR",
    "hungarian": "HU",
    "icelandic": "IS",
    "irish": "IE",
    "italian": "IT",
    "latvian": "LV",
    "lithuanian": "LT",
    "macedonian": "MK",
    "maltese": "MT",
    "norwegian": "NO",
    "polish": "PL",
    "portuguese": "PT",
    "romanian": "RO",
    "serbian": "RS",
    "slovak": "SK",
    "slovenian": "SI",
    "spanish": "ES",
    "swedish": "SE",
    "ukrainian": "UA",
}

inat_taxonomy_export_dir = Path("inaturalist-taxonomy.dwca")

country_to_number_of_names = []

for language_name, country_code in tqdm(language_to_iso2.items()):
    names = pd.read_csv(inat_taxonomy_export_dir / f"VernacularNames-{language_name}.csv")
    country_to_number_of_names.append({"country_code": country_code, "number_of_names": len(names)})

df = pd.DataFrame(country_to_number_of_names)

url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url)
world.loc[world['NAME'] == 'France', 'ISO_A2'] = 'FR'
world.loc[world['NAME'] == 'Norway', 'ISO_A2'] = 'NO'

gdf = world.merge(df, left_on="ISO_A2", right_on="country_code")

gdf.plot(column="number_of_names", cmap="viridis", legend=True, figsize=(8, 6), vmax=100000)
plt.axis("off")
plt.savefig("number_of_vernacular_names_by_country_jan_2026.png", dpi=300)
