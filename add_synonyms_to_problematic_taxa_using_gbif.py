import argparse
from pathlib import Path
import pandas as pd
from pygbif import species as gbif_species

ALL_DATASETS_DIR = Path("data-sources")
TARGET_DIR = Path("inat-common-name-adder")


def get_scientific_name(taxon):
    match taxon["rank"]:
        case "species":
            return taxon["species_scientific"]
        case "genus":
            return taxon["genus_scientific"]
        case "subfamily":
            return taxon["subfamily_scientific"]
        case "family":
            return taxon["family_scientific"]
        case "superfamily":
            return taxon["superfamily_scientific"]
        case "order":
            return taxon["order_scientific"]
        case "infraorder":
            return taxon["infraorder_scientific"]

    print(f"Unsupported rank: {taxon['rank']}")
    return None


def fetch_synonym_from_gbif(taxon):
    gbif_results = gbif_species.name_backbone(
        name=get_scientific_name(taxon),
        rank=taxon["rank"],
        clazz="Insecta",
        strict=True,
        verbose=True,
    )

    if gbif_results["matchType"] == "NONE" and "alternatives" not in gbif_results:
        print("no match found in GBIF")
        return None

    if taxon["rank"] == "species" and gbif_results["matchType"] == "HIGHERRANK":
        if "alternatives" in gbif_results:
            relevant_alternatives = [
                alt for alt in gbif_results["alternatives"] if alt["rank"] == "SPECIES"
            ]
            matched_names = []
            for alt in relevant_alternatives:
                matched_synonym = alt["species"]
                if matched_synonym not in matched_names:
                    matched_names.append(matched_synonym)
                matched_sci_name = alt["canonicalName"]
                if matched_sci_name not in matched_names:
                    matched_names.append(matched_sci_name)
            print(
                f"found these matches in GBIF for the species (match type = HIGHERRANK): {', '.join(matched_names)}"
            )
            return matched_names
        else:
            print("no species match found in GBIF (only a higher rank)")
            return None
    elif gbif_results["matchType"] == "NONE" and "alternatives" in gbif_results:
        matched_names = []
        for alt in gbif_results["alternatives"]:
            if alt["rank"] == "UNRANKED":
                continue
            matched_synonym = get_name_by_rank_from_gbif_results(alt)
            if not matched_synonym:
                continue
            if matched_synonym not in matched_names:
                matched_names.append(matched_synonym)
            matched_sci_name = alt["canonicalName"]
            if matched_sci_name not in matched_names:
                matched_names.append(matched_sci_name)
        print(f"found these uncertain matches in GBIF: {', '.join(matched_names)}")
        return matched_names
    else:
        matched_names = []
        if gbif_results["status"] == "ACCEPTED":
            matched_names.append(gbif_results["canonicalName"])
        else:
            primary_name = get_name_by_rank_from_gbif_results(gbif_results)
            if primary_name is not None:
                matched_names.append(primary_name)
            matched_names.append(gbif_results["canonicalName"])
        for alt in gbif_results.get("alternatives", []):
            if alt["rank"] == "UNRANKED":
                continue
            matched_synonym = get_name_by_rank_from_gbif_results(alt)
            if not matched_synonym:
                continue
            if matched_synonym not in matched_names:
                matched_names.append(matched_synonym)
            matched_sci_name = alt["canonicalName"]
            if matched_sci_name not in matched_names:
                matched_names.append(matched_sci_name)
        print(f"found these matches in GBIF: {', '.join(matched_names)}")
        return matched_names


def get_name_by_rank_from_gbif_results(gbif_results):
    try:
        match gbif_results["rank"]:
            case "SPECIES":
                return gbif_results["species"]
            case "GENUS":
                return gbif_results["genus"]
            case "SUBFAMILY":
                return gbif_results["subfamily"]
            case "FAMILY":
                return gbif_results["family"]
            case "SUPERFAMILY":
                return gbif_results["superfamily"]
            case "ORDER":
                return gbif_results["order"]
            case "INFRAORDER":
                return gbif_results["infraorder"]
            case "CLASS":
                return gbif_results["class"]
            case _:
                print(f"Unsupported rank: {gbif_results}")
    except KeyError:
        print(
            f"Couldn't extract name from this taxon object (tried to extract '{gbif_results.get('rank', 'unknown rank')}'): {gbif_results}"
        )
        return None


def main(dataset_directory_name):
    dataset_dir = ALL_DATASETS_DIR / dataset_directory_name

    df_all_taxa = pd.read_csv(dataset_dir / "taxa.csv")

    if not (dataset_dir / "problematic_taxa.csv").exists():
        print(
            f"Looks like you forgot to create a file named 'problematic_taxa.csv' inside the '{dataset_dir}' directory. Create it, then re-run this script."
        )
        return

    problematic_taxon_names = pd.read_csv(dataset_dir / "problematic_taxa.csv")[
        "scientificName"
    ].values

    taxa_synonym_enhanced = []

    for problematic_taxon_sci_name in problematic_taxon_names:
        print(f"=== Processing {problematic_taxon_sci_name} ===")

        taxa = df_all_taxa[
            df_all_taxa.apply(
                lambda taxon: get_scientific_name(taxon)
                == problematic_taxon_sci_name.lower(),
                axis=1,
            )
        ]
        if len(taxa):
            full_problematic_taxon = taxa.iloc[0].to_dict()
            full_problematic_taxon["synonyms"] = fetch_synonym_from_gbif(
                full_problematic_taxon
            )
            taxa_synonym_enhanced.append(full_problematic_taxon)
        else:
            print(
                f"the scientific name '{problematic_taxon_sci_name}' can't be found in the list of all taxa from your data source. did you mis-type the scientific name?"
            )

    pd.DataFrame(taxa_synonym_enhanced).to_json(
        dataset_dir / "problematic_taxa_with_synonyms.json", orient="records"
    )


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("data_source")
    args = arg_parser.parse_args()

    main(args.data_source)
