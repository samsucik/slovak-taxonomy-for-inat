import argparse
import json
from pathlib import Path
import shutil
import pandas as pd

ALL_DATASETS_DIR = Path("data-sources")
TARGET_DIR = Path("inat-common-name-adder")


def main(dataset_directory_name):
    dataset_dir = ALL_DATASETS_DIR / dataset_directory_name

    if not dataset_dir.exists():
        print(f"The data directory {dataset_dir} doesn't exist.")
        return

    if not (dataset_dir / "taxa.json").exists():
        print(
            f"The file 'taxa.json' is not found inside {dataset_dir}. Looks like you forgot to generate it."
        )
        return

    shutil.copyfile(dataset_dir / "taxa.json", TARGET_DIR / "taxa.json")

    for file_name in [
        "incorrect_synonym_matches",
        "taxa_not_in_inat",
        "taxa_already_assigned_common_name_in_inat",
        "allowed_inat_taxon_ids",
    ]:
        file_path = dataset_dir / f"{file_name}.csv"
        if file_path.exists():
            df = pd.read_csv(file_path)
        else:
            df = pd.DataFrame({"dummy_column": []})
        if len(df.columns) > 1:
            df.to_json(TARGET_DIR / f"{file_name}.json", orient="records")
        else:
            with open(TARGET_DIR / f"{file_name}.json", "w") as f:
                json.dump(df[df.columns[0]].values.tolist(), f)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("data_source")
    args = arg_parser.parse_args()

    main(args.data_source)
