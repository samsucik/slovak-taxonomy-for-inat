# Automating the common name adding process on iNaturalist

In [iNaturalist](https://www.inaturalist.org/), many taxa don't have a common name defined in many languages. To easily fix this at scale, one needs to be able to:
1. extract lists of common names from existing literature/databases/etc.
2. bulk-upload the lists to iNaturalist

**Extracting common names** is often hard and this repository provides only _examples_ of how I extracted Slovak common names of Slovak _Lepidoptera_ and a subset of _Insecta_ from an article and a book.

**Bulk-uploading** common names to iNaturalist used to be officially supported but, as of January, 2024, it is no longer supported.
The recommended way is to manually enter the common names one by one via the iNaturalist website
([inaturalist.org/taxa/.../taxon_names/new](https://www.inaturalist.org/taxa/51131/taxon_names/new)).
Luckily, this part can be largely automated and this repository provides a Google Chrome extension just for that – more on how to install it and use it [here](inat-common-name-adder/README.md).

## General set-up

These steps are a prerequisite for everything else. If you struggle with completing them, reach out.
1. install [`pyenv`](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation),
   [`pipx`](https://pipx.pypa.io/stable/installation/), and poetry (install it using pipx as `pipx install poetry`)
2. in your terminal, navigate to this directory
3. run `pyenv local` (download the Python version if/when prompted)
4. run `poetry install --no-root`

## How to prepare common names for bulk-uploading

Before you use the Google Chrome extension to  auto-add the common names to iNat taxa, you need to go through these steps:
1. create a new directory for your data source under [`data-sources`](./data-sources/)
2. inside the directory, add the common names (along with scientific names and taxon ranks) as a CSV file named `taxa.csv` by following [this example](data-sources/slovenske-mena-hmyzu-1975/taxa.csv) (the required columns are `rank` and the columns which, for the given taxon, contain its scientific and common name)
    - alternatively, you could adapt the [existing script](data-sources/slovenske-mena-hmyzu-1975/extract_taxa.py) to extract such a CSV from the raw text you've copied from a book/article/website...
3. [optional but highly recommended] prepare a list of all iNat taxon IDs that are relevant for your data source, e.g. a list of all birds if you're processing bird names. Such a list helps the extension to ignore taxa which might match your bird taxa by their scientific name but aren't relevant (e.g. there is both a bird genus and a plant genus named _Oenanthe_). The list can be compiled quite easily if it has a simple enough criterion – e.g. "all taxa in the class _Insecta_". You should:
    1. download the complete iNaturalist taxonomy from [here](https://www.inaturalist.org/taxa/inaturalist-taxonomy.dwca.zip) (the most up-to-date version gets published at the beginning of every month)
    2. copy the `taxa.csv` file from there and place it in this directory under the name `all_inat_taxa.csv`
    3. add your criterion (filter function) into the[`extract_allowed_inat_taxon_ids.py`](./extract_allowed_inat_taxon_ids.py) script (follow the existing examples there in `filter_functions`)
    4. run the script: `poetry run python extract_allowed_inat_taxon_ids.py your-data-directory-name` (replace `your-data-directory-name` with the actual directory name, e.g. `slovenske-mena-hmyzu-1975`)
4. take the data you've prepared so far and provide them to the Chrome extension by running `poetry run prepare_dataset_for_chrome_extension.py your-data-directory-name`
5. now the Chrome extension is ready and you can install it and run it as described [here](./inat-common-name-adder/README.md)

## Handling non-trivial cases ("my taxon can't be found in iNat")

### Advanced taxon matching with scientific name synonyms

You'll soon find out that, as the Chrome extension works through a long list of taxa, there are cases where the taxon's scientific name can't be found in iNaturalist. Stay calm, this is expected. Quite often, a taxon appears in iNat under a slightly different name than in your data source. Luckily, the extension shows a warning in the DevTools Console whenever it cannot find a taxon – so that you can later give these "troublesome" taxa a closer look.

The first thing you should do is to collect the scientific names of all these taxa in a simple CSV file with just one column named `scientificName`. Save the file as `problematic_taxa.csv` in your data source's directory. Now you can easily fetch the known scientific synonyms for the problematic taxa by running `poetry run add_synonyms_to_problematic_taxa_using_gbif.py your-data-directory-name`. This will create a new file named `problematic_taxa_with_synonyms.json` in your data directory. It should be very similar to the `taxa.json` file used by the extension except for being enriched with lots of scientific synonyms fetched from GBIF. If you manually copy this file into the extension's directory and rename it to `taxa.json`, you can reload the extension in your browser and let it run again. Hopefully, a lot of the problematic taxa will now be successfully found in iNat by their synonym(s).

**If some of the synonyms turn out to be incorrect**, i.e. you notice that they're leading the extension to find an incorrect taxon, the best way to handle this is to note such incorrect name-synonym pairs in a CSV file named `incorrect_synonym_matches.csv` (save the file in your data source directory). The required columns you should include are `scientificName` and `incorrectSynonym`. Once you've created the file, re-run the `prepare_dataset_for_chrome_extension.py` script and then reload and re-run the extension if you want to see it nicely ignore the incorrect synonyms.

### When all else fails – manually finding the taxa in iNat

Occasionally, not even the synonyms from GBIF might suffice to find the taxon in iNat. When this happens, roll up your sleeves and try your best – you might find further synonyms on the internet or otherwise find the right iNat taxon.

### Getting to zero warnings from the Chrome extension

It might well be that your aim is to end up with 0 warnings when running the Chrome extension, indicating that all the taxa from your data source have been processed (assigned a common name where possible). To achieve the zero, you might need to use these tricks:

- For any taxa that you've had to look up manually, note them down in a CSV file named `taxa_already_assigned_common_name_in_inat.csv` (save this in your data source directory) – the only required column is `scientificName`.
- For any taxa that actually don't exist in iNat (this can happen!), note them down in `taxa_not_in_inat.csv` (required column `scientificName`).

Once ready, re-run the `prepare_dataset_for_chrome_extension.py` script and then reload and re-run the extension. Hopefully, you'll now see zero warnings.
