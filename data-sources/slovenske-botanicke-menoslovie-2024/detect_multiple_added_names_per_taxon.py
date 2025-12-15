import pandas as pd

df_all = pd.read_csv("VernacularNames-slovak-dec.csv")
newly_affected_ids = df_all.iloc[13235:][df_all.iloc[13235:]["contributor"] == "Samo Sučík"]["id"]


print("DUPLICATES AMONG NEWLY ADDED NAMES")
duplicates_among_newly_affected_ids = [(id, count) for id, count in newly_affected_ids.value_counts().to_dict().items() if count > 1]
for (id, count) in duplicates_among_newly_affected_ids:
    names_added = df_all.iloc[13235:][df_all.iloc[13235:]["id"] == id]["vernacularName"].values.tolist()
    print(f"https://www.inaturalist.org/taxa/{id} ({count} names added: {names_added})")

previously_affected_ids = df_all.iloc[:13235]["id"]
overlapping_ids = set(newly_affected_ids.values.tolist()).intersection(previously_affected_ids.values.tolist())
print(f"There are {len(overlapping_ids)} IDs for which someone added a common name previously and we also added a common name recently.")
