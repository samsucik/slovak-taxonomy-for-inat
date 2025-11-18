import re

import pandas as pd
from pydantic import BaseModel


class Taxon(BaseModel):
    rank: str
    family_scientific: str | None = None
    family_common: str | None = None
    species_scientific: str | None = None
    species_common: str | None = None


def extract_species(df):
    sci_name_family_col = "vedecké meno čeľade"
    sci_name_col = "vedecké meno taxónu"
    sk_name_col = "platné slovenské meno taxónu"

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


def extract_families(df):
    sci_name_col = "vedecké meno"
    sk_name_col = "slovenské meno"

    taxa = []

    for _, row in df.iterrows():
        if pd.isna(row[sci_name_col]) or pd.isna(row[sk_name_col]):
            continue
        taxa.append(
            Taxon(
                rank="family",
                family_scientific=row[sci_name_col],
                family_common=row[sk_name_col],
            )
        )
    return taxa


if __name__ == "__main__":
    species_raw_data = pd.read_excel("sbm-november-2025.xlsx", sheet_name="druhy")
    species_list = extract_species(species_raw_data)

    family_raw_data = pd.read_excel("sbm-november-2025.xlsx", sheet_name="čeľade")
    family_list = extract_families(family_raw_data)

    taxon_df = pd.DataFrame([taxon.model_dump() for taxon in (species_list + family_list)])

    taxon_df.to_csv("taxa.csv", index=False)

    taxon_df.to_json(
        "taxa.json",
        index=False,
        orient="records",
    )
