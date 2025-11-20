import pandas as pd
from extract_allowed_inat_taxon_ids import filter_functions

def is_common_name_problematic(common_name):
    return common_name[0].isupper() or "(" in common_name or ")" in common_name

def main():
    all_inat_common_names_df = pd.read_csv("VernacularNames-slovak.csv")
    all_inat_taxa_df = pd.read_csv("all_inat_taxa.csv")

    data_source_name = "slovenske-botanicke-menoslovie-2024"
    filter_func = filter_functions[data_source_name]
    relevant_inat_ids = all_inat_taxa_df[all_inat_taxa_df.apply(filter_func, axis=1)][["id"]].values

    problematic_taxa_by_contributor = {}

    for _, row in all_inat_common_names_df.iterrows():
        if is_common_name_problematic(row["vernacularName"]): # and row["id"] in relevant_inat_ids:
            contributor = row["contributor"]
            if contributor not in problematic_taxa_by_contributor:
                problematic_taxa_by_contributor[contributor] = []
            problematic_taxa_by_contributor[contributor].append({
                "name": row["vernacularName"],
                "url": f"https://www.inaturalist.org/taxon_names/{row['id']}/edit"
            })
    
    for contributor, problematic_taxa in problematic_taxa_by_contributor.items():
        print(f"\n{contributor}:")
        [print(f" - [{taxon['name']}]({taxon["url"]})") for taxon in problematic_taxa]



if __name__ == "__main__":
    main()
