import re

import pandas as pd
from pydantic import BaseModel


class Taxon(BaseModel):
    rank: str
    order_scientific: str | None = None
    order_common: str | None = None
    family_scientific: str | None = None
    family_common: str | None = None
    genus_scientific: str | None = None
    genus_common: str | None = None
    species_scientific: str | None = None
    species_common: str | None = None
    subspecies_scientific: str | None = None
    subspecies_common: str | None = None


def extract_species(df):
    # ignore taxa that are extinct or or marked as Potential species
    taxon_rank_col = "Kľúč (Code)"
    sci_name_order_col = "Rad (Order)"
    sci_name_family_col = "Čeľaď (Family)"
    sci_name_subfamily_col = "Podčeľaď (Subfamily)"
    sci_name_genus_col = "Rod (Genus)"
    sci_name_species_col = "Druh (Species)"
    sci_name_subspecies_col = "Poddruh (Subspecies)"
    
    sk_name_col = "Slovenské meno (Slovak name)"


    taxa = []

    

    for _, row in df.iterrows():

        if pd.isna(row[sci_name_col]) or pd.isna(row[sk_name_col]) or row[sk_name_col].strip() == "–":
            continue

        taxon_rank = "species"
        sci_name = row[sci_name_col].strip()

        if len(sci_name.split()) == 1:
            taxon_rank = "genus"

        if "sect." in sci_name:
            taxon_rank = "section"

        if "×" in sci_name:
            taxon_rank = "hybrid" # TODO check all rank names

        if "nothosubsp." in sci_name:
            sci_name = re.sub(r"\s*nothosubsp\.\s*", " ", sci_name)
            taxon_rank = "subspecies hybrid"
        
        if "subsp." in sci_name:
            sci_name = re.sub(r"\s*subsp\.\s*", " ", sci_name)
            taxon_rank = "subspecies"

        if "var." in sci_name:
            sci_name = re.sub(r"\s*var\.\s*", " ", sci_name)
            taxon_rank = "variety"
        
        if "f." in sci_name:
            sci_name = re.sub(r"\s*f\.\s*", " ", sci_name)
            taxon_rank = "form"

        sk_name = row[sk_name_col].strip()

        # remove pronunciation information (anything in square brackets)
        if "[" in sk_name or "]" in sk_name:
            # remove anything even in cases where the opening or closing bracket is of the opposite type
            sk_name_edited = re.sub(r"[ ]?[\[\]].*[\[\]][ ]?", " ", sk_name).strip()
            # print(f"Slovak name contains pronunciation marker: '{sk_name}'. Removing it: '{sk_name_edited}'")
            sk_name = sk_name_edited
        
        # remove alternative names (anything in parentheses)
        if "(" in sk_name:
            sk_name_edited = re.sub(r"[ ]?\([^(]+\)[ ]?", " ", sk_name).strip()
            print(f"Slovak name contains alternative name(s): '{sk_name}'. Removing it: '{sk_name_edited}'")
            sk_name = sk_name_edited

        taxa.append(
            Taxon(
                rank=taxon_rank,
                family_scientific=row[sci_name_family_col].strip() if pd.notna(row[sci_name_family_col]) else None,
                species_scientific=sci_name,
                species_common=sk_name,
            )
        )

    return taxa

if __name__ == "__main__":
    species_raw_data = pd.read_excel("SVMS_13_aug_2020.xlsx", sheet_name="Slovenské mená vtákov sveta")
    species_list = extract_species(species_raw_data)

    taxon_df = pd.DataFrame(species_list)

    taxon_df.to_csv("taxa.csv", index=False)

    taxon_df.to_json(
        "taxa.json",
        index=False,
        orient="records",
    )
