function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const DATA_KEY = "inat-common-name-data";

const relevantSlovakTaxonRankNames = [
  "Rad",
  "Podrad",
  "Nadčeľaď",
  "Čeľaď",
  "Podčeľaď",
  "Rod",
  "Druh",
];

function taxonMatchesScientificName(taxonHeaderText, scientificName) {
  if (taxonHeaderText.toLowerCase() == scientificName.toLowerCase()) {
    return true;
  }

  if (
    relevantSlovakTaxonRankNames.some(
      (taxonRank) =>
        taxonHeaderText
          .toLowerCase()
          .replace(taxonRank.toLowerCase(), "")
          .trim() == scientificName.toLowerCase()
    )
  ) {
    return true;
  }

  return false;
}

async function closeTabIfApplicable() {
  const dataRaw = localStorage.getItem(DATA_KEY);
  console.log("We've just read the data from the local storage:", dataRaw);
  if (dataRaw) {
    const data = JSON.parse(dataRaw);

    if (document.querySelector("#TaxonHeader .sciname")) {
      // we're on a taxon's page. if we got here from the page where we added a new common name for this taxon, let's close the tab
      if (
        taxonMatchesScientificName(
          document.querySelector("#TaxonHeader .sciname").innerText,
          data.sci
        )
      ) {
        console.log("We're on a taxon's page and should now auto-close it!");
        localStorage.removeItem(DATA_KEY);
        window.close();
        return;
      }
    }
  }
}

closeTabIfApplicable();
