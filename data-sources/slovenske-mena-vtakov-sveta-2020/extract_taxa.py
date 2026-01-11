from copy import deepcopy
from enum import Enum
import re

import pandas as pd
from pydantic import BaseModel


class Taxon(BaseModel):
    rank: str
    order_scientific: str | None = None
    order_common: str | None = None
    family_scientific: str | None = None
    family_common: str | None = None
    subfamily_scientific: str | None = None
    subfamily_common: str | None = None
    genus_scientific: str | None = None
    genus_common: str | None = None
    species_scientific: str | None = None
    species_common: str | None = None
    # subspecies_scientific: str | None = None
    # subspecies_common: str | None = None

class Rank(Enum):
    ORDER = "ord."
    FAMILY = "fam."
    SUBFAMILY = "subf."
    GENUS = "gen."
    SPECIES = "✔"
    SPECIES_OTHER = "☑"
    POTENTIAL_SPECIES = "asp"
    SUBSPECIES = "○"
    SUBSPECIES_OTHER = "~"

rank_map = {
    Rank.ORDER.value: "order",
    Rank.FAMILY.value: "family",
    Rank.SUBFAMILY.value: "subfamily",
    Rank.GENUS.value: "genus",
    Rank.SPECIES.value: "species",
    Rank.SPECIES_OTHER.value: "species",
}

def extract_species(df):
    # ignore taxa that are extinct or or marked as Potential species
    taxon_rank_col = "Kľúč (Code)"
    sequence_col = "Poradie (Sequence)"

    sci_name_cols = {
        "order": "Rad (Order)",
        "family": "Čeľaď (Family)",
        "subfamily": "Podčeľaď (Subfamily)",
        "genus": "Rod (Genus)",
        "species": "Druh (Species)",
        "subspecies": "Poddruh (Subspecies)",
    }
    
    sk_name_col = "Slovenské meno (Slovak name)"

    taxa = []

    taxon = Taxon(rank="unknown")

    for i, row in df.iterrows():
        # if i > 10000:
        #     break
        rank = row[taxon_rank_col].strip()

        if rank in [Rank.POTENTIAL_SPECIES.value, Rank.SUBSPECIES.value, Rank.SUBSPECIES_OTHER.value]:
            continue
        
        rank_standardised = rank_map[rank]
        taxon = deepcopy(taxon)
        taxon.rank = rank_standardised
        sci_name = row[sci_name_cols[rank_standardised]]
        if pd.isna(sci_name):
            print(f"missing sci. name for #{row[sequence_col]}")
            continue
        else:
            sci_name = sci_name.strip()
        sk_name = row[sk_name_col]
        if rank == Rank.ORDER.value:
            sk_name = sk_name.lower()
            sci_name = sci_name.title()
        # print(f"{sk_name} – {sci_name}")
        
        if rank in [Rank.ORDER.value, Rank.FAMILY.value, Rank.SUBFAMILY.value, Rank.GENUS.value]:
            taxon.species_common = None
            taxon.species_scientific = None
        if rank in [Rank.ORDER.value, Rank.FAMILY.value, Rank.SUBFAMILY.value]:
            taxon.genus_common = None
            taxon.genus_scientific = None
        if rank in [Rank.ORDER.value, Rank.FAMILY.value]:
            taxon.subfamily_common = None
            taxon.subfamily_scientific = None
        if rank in [Rank.ORDER.value]:
            taxon.family_common = None
            taxon.family_scientific = None

        setattr(taxon, f"{rank_standardised}_common", sk_name)
        setattr(taxon, f"{rank_standardised}_scientific", sci_name)

        taxa.append(taxon.model_dump())

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
    species_raw_data = pd.read_excel("SMVS_13_aug_2020.xlsx", sheet_name="Slovenské mená vtákov sveta")
    species_list = extract_species(species_raw_data)

    taxon_df = pd.DataFrame(species_list)

    taxon_df.to_csv("taxa.csv", index=False)

    taxon_df.to_json(
        "taxa.json",
        index=False,
        orient="records",
    )
