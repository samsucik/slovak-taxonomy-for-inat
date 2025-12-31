import ast
import pandas as pd
from tqdm import tqdm

take_inat_sci_name_from_file = True

select_by_file_name = "taxa_manually_checked_synonyms"

all_sbm_taxa = pd.read_csv("taxa.csv")
taxa_to_select = pd.read_csv(f"{select_by_file_name}.csv")

def does_row_match(row, sci_name):
    return sci_name == row[f"{row['rank']}_scientific"]

def select_sbm_taxa(all_taxa, taxa_to_select):
    selected_rows = []
    for _, taxon_to_select in tqdm(taxa_to_select.iterrows(), total=len(taxa_to_select)):
        rows = all_taxa[all_taxa.apply(lambda row: does_row_match(row, taxon_to_select["sciName"]), axis=1)]
        if len(rows) != 1:
            print(f"Found {len(rows)} for {taxon_to_select["sciName"]}")
        else:
            row_to_select = rows.iloc[0].to_dict()
            if take_inat_sci_name_from_file:
                row_to_select["synonyms"] = [taxon_to_select["iNatSciName"]]
            selected_rows.append(row_to_select)
    return pd.DataFrame(selected_rows)


selected_sbm_taxa = select_sbm_taxa(all_sbm_taxa, taxa_to_select)

if not take_inat_sci_name_from_file:
    selected_sbm_taxa["synonyms"] = selected_sbm_taxa["scientific_synonyms_sbm"].apply(ast.literal_eval)

selected_sbm_taxa.to_json(f"taxa_selected_by_{select_by_file_name}.json", orient="records")
