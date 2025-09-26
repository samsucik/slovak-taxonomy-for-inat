import re

import pandas as pd
from pydantic import BaseModel


class Taxon(BaseModel):
    rank: str
    superfamily_scientific: str | None = None
    family_scientific: str | None = None
    family_common: str | None = None
    subfamily_scientific: str | None = None
    genus_scientific: str | None = None
    species_scientific: str | None = None
    species_common: str | None = None


def extract_taxon_data(text):
    taxa = []

    current_superfamily = None
    current_family = None
    current_subfamily = None
    current_genus = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Match superfamily:
        # Nadčeľaď: NEPTICULOIDEA
        superfamily_match = re.match(r"Nadčeľaď:\s*([A-ZÀ-Ž]+IDEA)", line)
        if superfamily_match:
            current_superfamily = superfamily_match.group(1).lower()
            taxa.append(
                Taxon(rank="superfamily", superfamily_scientific=current_superfamily)
            )
            current_family = current_subfamily = current_genus = None
            continue

        # Match family:
        # Čeľaď: NEPTICULIDAE – DROBNÍKOVITÉ
        family_match = re.match(r"Čeľaď:\s*([A-ZÀ-Ž]+IDAE)( – ([A-ZÀ-Ž]+))?", line)
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
                    superfamily_scientific=current_superfamily,
                    family_scientific=current_family,
                    family_common=current_family_common,
                )
            )
            current_subfamily = current_genus = None
            continue

        # Match subfamily:
        # Podčeľaď: NEPTICULINAE
        subfamily_match = re.match(r"Podčeľaď:\s*([A-ZÀ-Ž]+INAE)", line)
        if subfamily_match:
            current_subfamily = subfamily_match.group(1).lower()
            taxa.append(
                Taxon(
                    rank="subfamily",
                    superfamily_scientific=current_superfamily,
                    family_scientific=current_family,
                    family_common=current_family_common,
                    subfamily_scientific=current_subfamily,
                )
            )
            current_genus = None
            continue

        if re.match(f"Kmeň:.*", line) or re.match(f"Podkmeň:.*", line):
            continue

        # Match genus:
        # Enteucha Meyrick, 1915
        genus_match = re.match(
            r"^([A-Z][a-z]+).*",
            line,
        )
        if genus_match:
            current_genus = genus_match.group(1).lower()
            taxa.append(
                Taxon(
                    rank="genus",
                    superfamily_scientific=current_superfamily,
                    family_scientific=current_family,
                    family_common=current_family_common,
                    subfamily_scientific=current_subfamily,
                    genus_scientific=current_genus,
                )
            )
            continue

        # Match species:
        # acetosae (Stainton, 1854) – drobník štiavový
        # v-flava (Haworth, 1828) – moľa sudová
        species_match = re.match(r"([a-zà-ž-]+).* – (.*)", line)
        if species_match and current_genus:
            species = species_match.group(1).strip()
            species_common = species_match.group(2).strip()
            species_scientific = f"{current_genus} {species}"
            taxa.append(
                Taxon(
                    rank="species",
                    superfamily_scientific=current_superfamily,
                    family_scientific=current_family,
                    family_common=current_family_common,
                    subfamily_scientific=current_subfamily,
                    genus_scientific=current_genus,
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
