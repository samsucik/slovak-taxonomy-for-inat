import re

import pandas as pd
from pydantic import BaseModel


class Taxon(BaseModel):
    rank: str
    order_scientific: str
    order_common: str
    infraorder_scientific: str | None = None
    infraorder_common: str | None = None
    superfamily_scientific: str | None = None
    superfamily_common: str | None = None
    family_scientific: str | None = None
    family_common: str | None = None
    genus_scientific: str | None = None
    genus_common: str | None = None
    species_scientific: str | None = None
    species_common: str | None = None


def extract_taxon_data(text):
    taxa = []

    current_order = None
    current_order_common = None
    current_infraorder = None
    current_infraorder_common = None
    current_superfamily = None
    current_superfamily_common = None
    current_family = None
    current_family_common = None
    current_genus = None
    current_genus_common = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Match order:
        # 1. rad: COLLEMBOLA - CHVOSTOSKOKY
        # 16. rad: COPEOGNATHA — PAVšI
        order_match = re.match(
            r"[0-9]+\.\s*rad:\s*(\w+)\s*[-—]\s*([a-zA-Zà-žÀ-Ž]+).*", line, re.IGNORECASE
        )
        if order_match:
            current_order = order_match.group(1).lower()
            current_order_common = order_match.group(2).lower()
            taxa.append(
                Taxon(
                    rank="order",
                    order_scientific=current_order,
                    order_common=current_order_common,
                )
            )
            current_infraorder = current_infraorder_common = current_superfamily = (
                current_superfamily_common
            ) = current_family = current_family_common = current_genus = (
                current_genus_common
            ) = None
            continue

        # Match infraorder:
        # Podrad: ARTHROPLEONA - VOLNOCLNKOVCE
        # Podrad: TEREBRANTIA
        # Podrad: HETERONEURA (FRENATA) - UZDOKRÍDLE (syn. rôznokrídle [22])
        # Podrad: HOMONEURA (JUGATA) - JARMOkrídlE (syn. rovnakokrídle [22])
        infraorder_match = re.match(
            r"^\s*podrad:\s*(\w+)\s*(\(\w+\))?\s*(-\s*(\w[a-zA-Zà-žÀ-Ž\w ]+\w).*)?",
            line,
            re.IGNORECASE,
        )
        if infraorder_match:
            current_infraorder = infraorder_match.group(1).lower()
            current_infraorder_common = (
                infraorder_match.group(4).lower()
                if infraorder_match.group(4) is not None
                else None
            )
            taxa.append(
                Taxon(
                    rank="infraorder",
                    order_scientific=current_order,
                    order_common=current_order_common,
                    infraorder_scientific=current_infraorder,
                    infraorder_common=current_infraorder_common,
                )
            )
            current_superfamily = current_superfamily_common = current_family = (
                current_family_common
            ) = current_genus = current_genus_common = None
            continue

        # Match superfamily:
        # Nadcelad: Cephoidea - bodrušky
        # Nadčeľaď: Gryllacridoidea — kobylkovce
        superfamily_match = re.match(
            r"Nad[čc]e[ľl]a[ďd]:\s*(\w+)([^-\n—]*[-—]\s*(\S+))?", line
        )
        if superfamily_match:
            current_superfamily = superfamily_match.group(1).lower()
            current_superfamily_common = (
                superfamily_match.group(3).strip()
                if superfamily_match.group(3) is not None
                else None
            )
            taxa.append(
                Taxon(
                    rank="superfamily",
                    order_scientific=current_order,
                    order_common=current_order_common,
                    infraorder_scientific=current_infraorder,
                    infraorder_common=current_infraorder_common,
                    superfamily_scientific=current_superfamily,
                    superfamily_common=current_superfamily_common,
                )
            )
            current_family = current_family_common = current_genus = (
                current_genus_common
            ) = None
            continue

        # Match family:
        # Čelad: Tortricidae - obaľovačovité
        # Celad: Onychiuridae
        # Čeľaď: Eosentomonidae — sutkovité
        family_match = re.match(r"[ČC]e[ľl]a[ďd]:\s*(\w+)([^-\n—]*[-—]\s*(\S+))?", line)
        if family_match:
            current_family = family_match.group(1).lower()
            current_family_common = (
                family_match.group(3).strip().lower()
                if family_match.group(3) is not None
                else None
            )
            taxa.append(
                Taxon(
                    rank="family",
                    order_scientific=current_order,
                    order_common=current_order_common,
                    infraorder_scientific=current_infraorder,
                    infraorder_common=current_infraorder_common,
                    superfamily_scientific=current_superfamily,
                    superfamily_common=current_superfamily_common,
                    family_scientific=current_family,
                    family_common=current_family_common,
                )
            )
            current_genus = current_genus_common = None
            continue

        # Match genus:
        # Rod: Recurvaria Haworth 1828 - psota
        # Rod: Lepisma Linnaeus 1758 — Svehla
        # Rod: Miramella Dovnar-Zapolskij 1832 - koník
        # Rod: Stenobothrus (Fischer-Waldheim) 1853 - koník
        # Rod: Saldula Van Duzee 1914 - pobrežnička
        # Rod: Calligrpona J. Sahlberg 1871 - ostrôzka
        # Rod: Xyloterus Erichson - drevokaz
        genus_match = re.match(
            r"Rod[:;]\s*(\w+)\s+\(?[\w— .'-]+\)?\s*([0-9]+[0-9a-z]*\s*)?[-—]\s*(\S+)",
            line,
        )
        if genus_match:
            current_genus = genus_match.group(1).strip().lower()
            current_genus_common = genus_match.group(3).strip().strip()
            taxa.append(
                Taxon(
                    rank="genus",
                    order_scientific=current_order,
                    order_common=current_order_common,
                    infraorder_scientific=current_infraorder,
                    infraorder_common=current_infraorder_common,
                    superfamily_scientific=current_superfamily,
                    superfamily_common=current_superfamily_common,
                    family_scientific=current_family,
                    family_common=current_family_common,
                    genus_scientific=current_genus,
                    genus_common=current_genus_common,
                )
            )
            continue

        # Match species:
        # -nanella (Denis-Schiffermüller) 1775- psota ovocná
        # — aquatica Linnaeus 1746 — chvostoskok vodný
        # — fragilis Meinert 1865 vidličiarka krehká
        # — bicolor (Philippi 1830) - kobylôcka zelenkastá
        # — c-album (Linnaeus) 1758 - babôčka zubatokrídla (syn. bábočka ríbeziová (alcho biele C) [3])
        species_match = re.match(
            r"[-—]\s*([\w-]+)\s*\(?[^)]*\)?\s*([0-9—-]+[0-9])?\s*[-—]\s*([^;(]*).*",
            line,
        )
        if species_match and current_genus:
            species = species_match.group(1).strip()
            if species != species.lower():
                print(f"Attention! Species name seems case-sensitive: {species}")
            species_common = species_match.group(3).strip()
            if current_genus_common.lower() not in species_common.lower():
                print(
                    f"Attention: Current genus common name isn't found in the species common name: '{current_genus_common}' vs '{species_common}'"
                )
            species_scientific = f"{current_genus} {species}"
            taxa.append(
                Taxon(
                    rank="species",
                    order_scientific=current_order,
                    order_common=current_order_common,
                    infraorder_scientific=current_infraorder,
                    infraorder_common=current_infraorder_common,
                    superfamily_scientific=current_superfamily,
                    superfamily_common=current_superfamily_common,
                    family_scientific=current_family,
                    family_common=current_family_common,
                    genus_scientific=current_genus,
                    genus_common=current_genus_common,
                    species_scientific=species_scientific,
                    species_common=species_common,
                )
            )
            continue

    return taxa


if __name__ == "__main__":
    with open("raw_text.txt", "r") as f:
        data = f.readlines()

    taxon_list = extract_taxon_data("\n".join(data))

    taxon_df = pd.DataFrame([taxon.model_dump() for taxon in taxon_list])

    taxon_df.to_csv("taxa.csv", index=False)

    taxon_df.to_json(
        "taxa.json",
        index=False,
        orient="records",
    )
