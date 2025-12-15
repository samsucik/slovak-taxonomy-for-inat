import pandas as pd

df_existing_names_all = pd.read_csv("existing_names.csv")
df_existing_names_covered = pd.read_csv("existing_names_covered.csv")

covered_names = [name.lower() for name in df_existing_names_covered["commonNameINat"].values.tolist()]

def is_name_not_covered(name):
    return name.lower() not in covered_names

df_existing_names_not_covered = df_existing_names_all[df_existing_names_all["commonNameINat"].apply(is_name_not_covered)]
df_existing_names_not_covered.to_csv("existing_names_not_covered.csv", index=False)
