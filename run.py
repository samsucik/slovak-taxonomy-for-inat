import pandas as pd
from pygbif import species as gbif_species

df_all_taxa = pd.read_csv("taxa-slovenske-mena-hmyzu.csv")

unmatched_taxon_names = pd.read_csv("unmatched_taxa_names.csv")["scientificName"].values


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
    print(f"=== Processing {get_scientific_name(taxon)} ({taxon['rank']}) ===")

    gbif_results = gbif_species.name_backbone(
        name=get_scientific_name(taxon),
        rank=taxon["rank"],
        clazz="Insecta",
        strict=True,
        verbose=True,
    )

    if gbif_results["matchType"] == "NONE" and "alternatives" not in gbif_results:
        print("no match found")
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
            print(f"found these matches: {', '.join(matched_names)}")
            return matched_names
        else:
            print("no species match found (only a higher rank)")
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
        print(f"found these uncertain matches: {', '.join(matched_names)}")
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
        print(f"found these matches: {', '.join(matched_names)}")
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
        print(f"Couldn't extract name from this taxon object (tried to extract '{gbif_results['rank']}'): {gbif_results}")
        return None

taxa_synonym_enhanced = []

for unmatched_taxon_sci_name in unmatched_taxon_names:
    gbif_synonym = None
    taxa = df_all_taxa[
            df_all_taxa.apply(
                lambda taxon: get_scientific_name(taxon)
                == unmatched_taxon_sci_name.lower(),
                axis=1,
            )
        ]
    if len(taxa):
        full_unmatched_taxon = (taxa
            .iloc[0]
            .to_dict()
        )
        full_unmatched_taxon["synonyms"] = fetch_synonym_from_gbif(full_unmatched_taxon)
        taxa_synonym_enhanced.append(full_unmatched_taxon)

pd.DataFrame(taxa_synonym_enhanced).to_json(
    "unmatched_taxa_with_synonyms.json", orient="records"
)
pd.DataFrame(taxa_synonym_enhanced).to_csv("unmatched_taxa_with_synonyms.csv")
