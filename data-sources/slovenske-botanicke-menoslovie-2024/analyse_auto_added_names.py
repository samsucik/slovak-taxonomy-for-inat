import pandas as pd
from datetime import datetime

date_lower_bound = datetime.strptime("2025-11-22", '%Y-%m-%d').date()

df_names_added_all = pd.read_csv("VernacularNames-slovak-dec.csv", parse_dates=["created"])
df_names_added_all["created"] = pd.to_datetime(df_names_added_all["created"]).dt.date
df_names_added = df_names_added_all[(df_names_added_all["contributor"] == "Samo Sučík") & (df_names_added_all["created"] >= date_lower_bound)]

df_sbm_taxa = pd.read_csv("data-sources/slovenske-botanicke-menoslovie-2024/taxa.csv")
df_sbm_taxa["commonName"] = df_sbm_taxa.apply(lambda row: row[f"{row["rank"]}_common"], axis=1)
common_name_cols = [col for col in df_sbm_taxa.columns if col.endswith("_common")]
def get_sbm_sci_name_by_common_name(common_name):
    matching_rows = df_sbm_taxa[df_sbm_taxa["commonName"] == common_name]
    if len(matching_rows) > 1 and len(common_name.split()) > 1:
        print(f"Found {len(matching_rows)} taxa with commonName={common_name} but expected exactly 1.")
        return ""
    elif len(matching_rows) == 0:
        print(f"No SBM scientific names found for '{common_name}'")
        return ""
    else:
        return matching_rows["commonName"].values.tolist()[0]

df_names_added["sciNameSBM"] = df_names_added["vernacularName"].apply(get_sbm_sci_name_by_common_name)
exit()

# print(df_names_added)

df_all_inat_taxa = pd.read_csv("all_inat_taxa.csv")
def get_inat_sci_name_by_id(id):
    matching_rows = df_all_inat_taxa[df_all_inat_taxa["id"] == id]
    if len(matching_rows) != 1:
        print(f"Found {len(matching_rows)} taxa with ID={id} but expected exactly 1.")
        return ""
    return matching_rows["scientificName"].values.tolist()[0]


# id,taxonID,identifier,parentNameUsageID,kingdom,phylum,class,order,family,genus,specificEpithet,infraspecificEpithet,modified,scientificName,taxonRank,references

df_names_added["sciNameInat"] = df_names_added["id"].apply(get_inat_sci_name_by_id)

print(df_names_added)
