import ast
import pandas as pd
from tqdm import tqdm

select_by_file_name = "missing_taxa"

all_sbm_taxa = pd.read_csv("taxa.csv")
taxa_to_select = pd.read_csv(f"{select_by_file_name}.csv")["sciName"].values.tolist()

def does_row_match(row, sci_name):
    return sci_name == row[f"{row['rank']}_scientific"]


def select_sbm_taxa(all_taxa, sci_names_to_select):
    selected_rows = []
    for sci_name in tqdm(sci_names_to_select):
        rows = all_taxa[all_taxa.apply(lambda row: does_row_match(row, sci_name), axis=1)]
        if len(rows) != 1:
            print(f"Found {len(rows)} for {sci_name}")
        else:
            selected_rows.append(rows.iloc[0].to_dict())
    return pd.DataFrame(selected_rows)


selected_sbm_taxa = select_sbm_taxa(all_sbm_taxa, taxa_to_select)

selected_sbm_taxa["synonyms"] = selected_sbm_taxa["scientific_synonyms_sbm"].apply(ast.literal_eval)

selected_sbm_taxa.to_json(f"taxa_selected_by_{select_by_file_name}.json", orient="records")
