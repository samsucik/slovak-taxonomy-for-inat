from pathlib import Path
import pandas as pd
import argparse

# add a function here to support another data source
filter_functions = {
    "slovenske-mena-hmyzu-1975": lambda taxon: taxon["class"] == "Entognatha"
    or taxon["class"] == "Insecta",
    "checklist-of-lepidoptera-recorded-in-Slovakia-2022": lambda taxon: taxon["order"]
    == "Lepidoptera",
    "slovenske-botanicke-menoslovie-2024": lambda taxon: taxon["phylum"] == "Tracheophyta"
}


def main(data_source_name):
    if data_source_name not in filter_functions:
        print(
            f"Looks like you haven't defined a filter function for the data source '{data_source_name}'. "
            f"Define it right in this script, then run the script."
        )
        return
    filter_func = filter_functions[data_source_name]

    df_all = pd.read_csv("all_inat_taxa.csv")

    allowed_ids_df = df_all[df_all.apply(filter_func, axis=1)][["id"]]
    allowed_ids_df.to_csv(
        Path("data-sources") / data_source_name / "allowed_inat_taxon_ids.csv",
        index=False,
    )


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("data_source")
    args = arg_parser.parse_args()

    main(args.data_source)
