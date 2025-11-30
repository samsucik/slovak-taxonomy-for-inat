import re

import pandas as pd
from pydantic import BaseModel


class Taxon(BaseModel):
    rank: str
    family_scientific: str | None = None
    family_common: str | None = None
    genus_scientific: str | None = None
    genus_common: str | None = None
    genushybrid_scientific: str | None = None
    genushybrid_common: str | None = None
    section_scientific: str | None = None
    section_common: str | None = None
    species_scientific: str | None = None
    species_common: str | None = None
    hybrid_scientific: str | None = None
    hybrid_common: str | None = None
    subspecies_hybrid_scientific: str | None = None
    subspecies_hybrid_common: str | None = None
    subspecies_scientific: str | None = None
    subspecies_common: str | None = None
    group_scientific: str | None = None
    group_common: str | None = None
    variety_scientific: str | None = None
    variety_common: str | None = None
    form_scientific: str | None = None
    form_common: str | None = None


def is_legit_inat_rank(rank):
    return rank in {
        "species",
        "zoosection",
        "kingdom",
        "class",
        "hybrid",
        "superclass",
        "zoosubsection",
        "subphylum",
        "phylum",
        "suborder",
        "stateofmatter",
        "subtribe",
        "epifamily",
        "complex",
        "subclass",
        "genushybrid",
        "infraorder",
        "section",
        "subgenus",
        "supertribe",
        "order",
        "tribe",
        "infrahybrid",
        "subfamily",
        "parvorder",
        "superorder",
        "subspecies",
        "family",
        "form",
        "superfamily",
        "genus",
        "infraclass",
        "subsection",
        "subterclass",
        "variety",
    }


def extract_species(df):
    sci_name_family_col = "vedecké meno čeľade"
    sci_name_col = "vedecké meno taxónu"
    sk_name_col = "platné slovenské meno taxónu"

    taxa = []
    for _, row in df.iterrows():
        if (
            pd.isna(row[sci_name_col])
            or pd.isna(row[sk_name_col])
            or row[sk_name_col].strip() == "–"
        ):
            continue

        taxon_rank = "species"
        sci_name = row[sci_name_col].strip()

        if len(sci_name.split()) == 1:
            taxon_rank = "genus"

        if "sect." in sci_name:
            taxon_rank = "section"

        if sci_name.startswith("×"):
            sci_name = sci_name[1:].strip()
            taxon_rank = "genushybrid"
        elif "×" in sci_name:
            sci_name = re.sub(r"×(\w)", r"× \g<1>", sci_name)
            taxon_rank = "hybrid"  # TODO check all rank names

        if "nothosubsp." in sci_name:
            sci_name = re.sub(r"\s*nothosubsp\.\s*", " ", sci_name)
            taxon_rank = "subspecies_hybrid"

        if "subsp." in sci_name:
            sci_name = re.sub(r"\s*subsp\.\s*", " ", sci_name)
            taxon_rank = "subspecies"

        if "var." in sci_name:
            sci_name = re.sub(r"\s*var\.\s*", " ", sci_name)
            taxon_rank = "variety"

        if "sk." in sci_name:
            sci_name = re.sub(r"\s*sk\.\s*", " ", sci_name)
            taxon_rank = "group"

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
            print(
                f"Slovak name contains alternative name(s): '{sk_name}'. Removing it: '{sk_name_edited}'"
            )
            sk_name = sk_name_edited

        if not is_legit_inat_rank(taxon_rank):
            print("\n\nTHE RANK ISN'T VALID: ", taxon_rank, "\n\n")

        taxon_attrs = {
            "rank": taxon_rank,
            "family_scientific": (
                row[sci_name_family_col].strip()
                if pd.notna(row[sci_name_family_col])
                else None
            ),
            f"{taxon_rank}_scientific": sci_name,
            f"{taxon_rank}_common": sk_name,
        }

        taxa.append(Taxon(**taxon_attrs))

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

    taxon_df = pd.DataFrame(
        [taxon.model_dump() for taxon in (species_list + family_list)]
    )

    taxon_df.to_csv("taxa.csv", index=False)

    taxon_df.to_json(
        "taxa.json",
        index=False,
        orient="records",
    )
