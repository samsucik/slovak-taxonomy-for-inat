function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// given a search term that is a scientific name:
// when SK name exists, .subtitle contains the primary scientific name.
// the .title element contains the SK name if it exists and the primary scientific name otherwise. in both case, it also contains the scientific name we searched for if it's a synonym.
// the .subtitle element ALWAYS contains the taxon rank except for when the taxon rank is "species" ("druh") and a common name exists.
function lacksCommonName(subtitleStr, taxonRankEn) {
  return subtitleStr == taxonRankMappingEnSk[taxonRankEn];
}

function extractTitleFromSearchResult(searchResultElem) {
  // <li class="ac-result taxon ui-menu-item" role="presentation">
  //   <div class="ac" data-taxon-id="57512">
  //     <div class="ac-thumb">
  //       <img src="https://inaturalist-open-data.s3.amazonaws.com/photos/117465980/square.jpg">
  //     </div>
  //     <div class="ac-label">
  //       <div>
  //         <span class="title">Imelo Biele</span>
  //         <span class="subtitle">
  //           <i>Viscum album</i>
  //         </span>
  //       </div>
  //     </div>
  //     <a class="ac-view" target="_blank" rel="noopener noreferrer" href="/taxa/57512">Zobraziť</a>
  //   </div>
  // </li>
  return searchResultElem.querySelector(".title").innerText.trim();
}

function extractSubtitleFromSearchResult(searchResultElem) {
  return searchResultElem
    .querySelector(".subtitle")
    .innerText.replace("Zobraziť", "")
    .trim();
}

function extractCommonNameFromSearchResult(searchResultElem) {
  const title = extractTitleFromSearchResult(searchResultElem);
  const subtitle = extractSubtitleFromSearchResult(searchResultElem);
  const subtitleWithoutRankName = slovakTaxonRankNames.reduce((subtitle, rankName) => subtitle.replace(rankName, "").trim(), subtitle);
  if (!subtitleWithoutRankName.length) {
    // the subtitle contained just a taxon rank name, implying the taxon doesn't have a common name assigned
    return null;
  }

  // remove the parenthesised part – when present, it contains just a synonym
  return title.replace(/\(.*\)/, '').trim();
}

function extractRankFromSearchResult(searchResultElem) {
  const subtitle = extractSubtitleFromSearchResult(searchResultElem);
  const foundRanks = taxonRankInatNames.filter((rank) => subtitle.startsWith(rank));
  if (!foundRanks.length) {
    // the rank could be species, subspecies, hybrid, form, ...
    console.warn(`This subtitle doesn't seem to start with a rank: ${subtitle}.`)
    return null
  } else {
    return taxonRankMappingSkEn[foundRanks[0]];
  }
  // if (taxonRank != "species") {
  //   return startsWithSpecificTaxonRankName(subtitleText, taxonRank);
  // } else {
  //   return (
  //     !startsWithATaxonRank(subtitleText) ||
  //     startsWithSpecificTaxonRankName(subtitleText, taxonRank)
  //   );
  // }
}

const taxonRankMappingEnSk = {
  order: "Rad",
  infraorder: "Podrad",
  superfamily: "Nadčeľaď",
  family: "Čeľaď",
  subfamily: "Podčeľaď",
  genus: "Rod",
  species: "Druh",
  section: "Sekcia",
  genushybrid: "Hybridný rod",
  subspecies: "Poddruh",
  form: "Forma",
  hybrid: "Kríženec"
};
const taxonRankInatNames = Object.values(taxonRankMappingEnSk);

const taxonRankMappingSkEn = Object.fromEntries(
  Object.entries(taxonRankMappingEnSk).map(entry => entry.reverse())
);


const SearchResultCommonNameAlreadyExists = "commonNameAlreadyExists";
const SearchResultNoTaxaFound = "noTaxaFound";
const SearchResultMultipleTaxaFound = "multipleTaxaFound";
const SearchResultOneTaxonFound = "oneTaxonFound";

const REPORT_EXISTING_WRONGLY_CASED_NAMES = true;
const REPORT_EXISTING_DIFFERENT_COMMON_NAMES = true;

function findMatchingDropdownTaxonElement(
  elements,
  scientificName,
  taxonRank,
  allowedTaxaIdsList
) {
  // match scientific name (approximate match)
  const elementsMatchingScientificName = elements.filter((el) => {
    return el.innerText.toLowerCase().includes(scientificName.toLowerCase());
  });
  if (!elementsMatchingScientificName.length) {
    console.log(
      `Nothing found for '${scientificName}' (${taxonRank}) (scientific name approximate match)`
    );
    return { result: SearchResultNoTaxaFound, elems: [] };
  }

  // match taxon rank
  const elementsMatchingTaxonRank = elementsMatchingScientificName.filter(
    (el) => searchResultMatchesTaxonRank(el, taxonRank)
  );
  if (!elementsMatchingTaxonRank.length) {
    console.log(
      `Nothing found for '${scientificName}' (${taxonRank}) (taxon rank match)`
    );
    return { result: SearchResultNoTaxaFound, elems: [] };
  }

  // filter based on list of allowed taxon IDs
  var elementsMatchingIdFilter = elementsMatchingTaxonRank;
  if (allowedTaxaIdsList) {
    elementsMatchingIdFilter = elementsMatchingTaxonRank.filter((elem) =>
      allowedTaxaIdsList.includes(parseInt(dropdownItemToTaxonId(elem)))
    );
  }
  if (!elementsMatchingIdFilter.length) {
    console.log(
      `Nothing found for '${scientificName}' (${taxonRank}) (allowed IDs list filter)`
    );
    return { result: SearchResultNoTaxaFound, elems: [] };
  }

  // filter out taxa with common name already defined
  const elementsLackingCommonName = elementsMatchingIdFilter.filter((el) => {
    const subtitleText = extractSubtitleFromSearchResult(el)
    return !containsCommonName(subtitleText, taxonRank);
  });
  if (elementsLackingCommonName.length == 0) {
    console.log(
      `Common name seems to exist already for '${scientificName}' (${taxonRank})`
    );
    return { result: SearchResultCommonNameAlreadyExists, elems: [] };
  }

  // match scientific name (exact match)
  const elementsWithExactScientificNameMatch = elementsLackingCommonName.filter(
    (el) => {
      const title = el.querySelector(".title").innerText.toLowerCase();
      return (
        title == scientificName.toLowerCase() ||
        title.includes(`(${scientificName.toLowerCase()})`)
      );
    }
  );
  if (elementsWithExactScientificNameMatch.length == 0) {
    console.log(
      `No taxa lack a common name and match exactly the scientific name for '${scientificName}' (${taxonRank})`
    );
    return { result: SearchResultNoTaxaFound, elems: [] };
  } else if (elementsWithExactScientificNameMatch.length > 1) {
    console.warn(
      `More than one match found for '${scientificName}' (${taxonRank}): ${elementsWithExactScientificNameMatch.map(
        (el) => el.innerText
      )}`
    );
    return { result: SearchResultMultipleTaxaFound, elems: [] };
  } else {
    return {
      result: SearchResultOneTaxonFound,
      elems: elementsWithExactScientificNameMatch,
    };
  }
}

function getScientificName(taxon) {
  return taxon.rank == "order"
    ? taxon.order_scientific
    : taxon.rank == "infraorder"
      ? taxon.infraorder_scientific
      : taxon.rank == "superfamily"
        ? taxon.superfamily_scientific
        : taxon.rank == "family"
          ? taxon.family_scientific
          : taxon.rank == "subfamily"
            ? taxon.subfamily_scientific
            : taxon.rank == "genus"
              ? taxon.genus_scientific
              : taxon.rank == "species"
                ? taxon.species_scientific
                : undefined;
}

function getScientificSynonym(taxon) {
  if (taxon["synonyms"] != undefined) {
    return taxon.synonyms[0];
  } else {
    return null;
  }
}

function getCommonName(taxon) {
  return taxon.rank == "order"
    ? taxon.order_common
    : taxon.rank == "infraorder"
      ? taxon.infraorder_common
      : taxon.rank == "superfamily"
        ? taxon.superfamily_common
        : taxon.rank == "family"
          ? taxon.family_common
          : taxon.rank == "subfamily"
            ? taxon.subfamily_common
            : taxon.rank == "genus"
              ? taxon.genus_common
              : taxon.rank == "species"
                ? taxon.species_common
                : undefined;
}

function startsWithSpecificTaxonRankName(str, taxonRankEn) {
  return (
    str == taxonRankMappingEnSk[taxonRankEn] ||
    str.startsWith(`${taxonRankMappingEnSk[taxonRankEn]} `)
  );
}

function startsWithATaxonRank(str) {
  for (taxonRank of slovakTaxonRankNames) {
    if (str == taxonRank || str.startsWith(`${taxonRank} `)) {
      return true;
    }
  }
  return false;
}

function containsCommonName(subtitleStr, taxonRankEn) {
  return subtitleStr != taxonRankMappingEnSk[taxonRankEn];
}

function dropdownItemToTaxonId(item) {
  const link = item.querySelector("a");
  if (!link || !link.href) {
    return null;
  }

  const taxonIdMatch = link.href.match(/\/taxa\/(\d+)/);
  if (!taxonIdMatch) {
    return null;
  }

  return taxonIdMatch[1];
}

async function clearSearchInputBox(inputBoxElem) {
  inputBoxElem.value = "";
  inputBoxElem.dispatchEvent(new Event("input", { bubbles: true }));
  await sleep(500);
}

function fillSearchInputBox(inputBoxElem, inputStr) {
  inputBoxElem.value = inputStr;
  inputBoxElem.dispatchEvent(new Event("input", { bubbles: true }));
  inputBoxElem.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true }));
}

async function getInputBoxResultsContainer() {
  let resultsContainer;
  let attemptCounter = 0;
  while (
    (!resultsContainer ||
      Array.from(resultsContainer.querySelectorAll("li")).length == 0) &&
    attemptCounter < 10
  ) {
    await sleep(500); // Wait for results to appear
    resultsContainer = document.querySelector(".ac-menu.open");
    attemptCounter = attemptCounter + 1;
    if (resultsContainer) {
      break;
    }
  }
  return resultsContainer;
}

async function loadListOfTaxa() {
  const taxaListPath = chrome.runtime.getURL("taxa.json");
  return await (await fetch(taxaListPath)).json();
}

async function loadAllowedInatIdsList() {
  const allowedIdListPath = chrome.runtime.getURL(
    "allowed_inat_taxon_ids.json"
  );
  return await (await fetch(allowedIdListPath)).json();
}

async function loadTaxaNotInInat() {
  const taxaListPath = chrome.runtime.getURL("taxa_not_in_inat.json");
  return (await (await fetch(taxaListPath)).json()).map(
    (record) => record.scientificName
  );
}

async function loadTaxaAlreadyHavingACommonName() {
  const taxaListPath = chrome.runtime.getURL(
    "taxa_already_assigned_common_name_in_inat.json"
  );
  return (await (await fetch(taxaListPath)).json()).map(
    (record) => record.scientificName
  );
}

async function loadIncorrectScientificNameSynonyms() {
  const taxaListPath = chrome.runtime.getURL("incorrect_synonym_matches.json");
  return await (await fetch(taxaListPath)).json();
}

function getSearchInputElem() {
  const inputBoxElem = document.querySelector("#q");
  if (!inputBoxElem) {
    throw Error("❌ Search input box not found.");
  } else {
    return inputBoxElem;
  }
}

function searchResultMatchesTaxonRank(searchResultElem, taxonRank) {
  const subtitleText = searchResultElem
    .querySelector(".subtitle")
    .innerText.replace("Zobraziť", "")
    .trim();
  if (taxonRank != "species") {
    return startsWithSpecificTaxonRankName(subtitleText, taxonRank);
  } else {
    return (
      !startsWithATaxonRank(subtitleText) ||
      startsWithSpecificTaxonRankName(subtitleText, taxonRank)
    );
  }
}

async function exactCommonNameAlreadyExists(
  inputBoxElem,
  commonName,
  scientificName,
  taxonRank,
  relevantTaxaIds
) {
  await clearSearchInputBox(inputBoxElem);
  fillSearchInputBox(inputBoxElem, commonName);
  const resultsContainer = await getInputBoxResultsContainer();

  if (!resultsContainer || !resultsContainer.querySelectorAll("li").length) {
    return false;
  }

  const matchingSearchResults = Array.from(resultsContainer.querySelectorAll("li")).filter((el) => {
    if (relevantTaxaIds && !relevantTaxaIds.includes(parseInt(dropdownItemToTaxonId(el)))) {
      return false;
    }

    const iNatCommonName = extractCommonNameFromSearchResult(el);
    const iNatRank = extractRankFromSearchResult(el);
    if (iNatCommonName.toLowerCase() == commonName.toLowerCase()) {
      console.log(`The common name for ${scientificName} already exists.`);
      const ranksMatch = iNatRank == taxonRank;
      if (REPORT_EXISTING_WRONGLY_CASED_NAMES && iNatCommonName != commonName) {
        console.warn(`Common name exists for ${scientificName} but doesn't match the official casing. ${ranksMatch ? 'Ranks match.' : `Ranks don't match: ${taxonRank} vs ${iNatRank}`}`);
      }
      if (!ranksMatch) {
        console.warn(`Ranks for '${commonName}' don't match: ${taxonRank} vs ${iNatRank}`);
      }
    }

    return (
      iNatRank == taxonRank &&
      iNatCommonName.toLowerCase() == commonName.toLowerCase()
    )
  });
  return matchingSearchResults.length > 0;
}

async function fetchSearchResults(
  inputBoxElem,
  scientificName,
  scientificNameLogStr,
  taxonRank
) {
  await clearSearchInputBox(inputBoxElem);
  fillSearchInputBox(inputBoxElem, scientificName);

  const resultsContainer = await getInputBoxResultsContainer();
  if (!resultsContainer) {
    console.log(
      `❌ No search results container for ${scientificNameLogStr} (${taxonRank})`
    );
    return [];
  }

  const items = Array.from(resultsContainer.querySelectorAll("li"));
  if (items.length === 0) {
    console.log(
      `❌ No results in the results container for ${scientificNameLogStr} (${taxonRank})`
    );
    return [];
  }

  return items;
}

async function findTaxaWithoutCommonName() {
  const taxaList = await loadListOfTaxa();

  // these are all the IDs that are relevant to our current effort,
  // e.g. all insect taxon IDs if we're adding common names of insects.
  // used for filtering out irrelevant taxa that might otherwise match
  // the scientific (or even common) name we're after because names
  // aren't unique across different classes (example: Triodia, Stigmella).
  const allowedIdsList = await loadAllowedInatIdsList();

  const taxaNotInInat = await loadTaxaNotInInat();
  const taxaAlreadyHavingACommonName = await loadTaxaAlreadyHavingACommonName();
  const incorrectScientificNameSynonyms =
    await loadIncorrectScientificNameSynonyms();

  // give the website enough time to finish initialising everything
  await sleep(2000);

  const inputBoxElem = getSearchInputElem();

  for (const taxon of taxaList) {
    // a taxon looks like this:
    //   {
    //     "rank": "superfamily",
    //     "superfamily_scientific": "micropterigoidea",
    //     "family_scientific": null,
    //     "family_common": null,
    //     "subfamily_scientific": null,
    //     "genus_scientific": null,
    //     "species_scientific": null,
    //     "species_common": null
    //     "synonyms": null | ['Scientificnamesynonym1', 'Scientificnamesynonym2', ...]
    //   }
    const originalScientificName = getScientificName(taxon);
    const commonName = getCommonName(taxon);
    if (!originalScientificName) {
      console.warn(
        `No scientific name provided for this taxon (${taxon}), skipping it.`
      );
      continue;
    }
    if (!commonName) {
      console.log(
        `No common name provided for ${originalScientificName} (${taxon.rank}), skipping it.`
      );
      continue;
    }

    if (taxaNotInInat.includes(originalScientificName)) {
      console.log(
        `Skipping ${originalScientificName} as it has been marked as not found in iNat.`
      );
      continue;
    } else if (taxaAlreadyHavingACommonName.includes(originalScientificName)) {
      console.log(
        `Skipping ${originalScientificName} as it has been marked as already having a common name assigned in iNat.`
      );
      continue;
    }

    var taxonFound = false;

    if (
      await exactCommonNameAlreadyExists(
        inputBoxElem,
        commonName,
        originalScientificName,
        taxon.rank,
        allowedIdsList
      )
    ) continue;

    continue;

    var scientificNameCandidates =
      taxon["synonyms"] != undefined
        ? [...new Set([originalScientificName, ...taxon["synonyms"]])]
        : [originalScientificName];
    for (const scientificName of scientificNameCandidates) {
      if (
        [
          incorrectScientificNameSynonyms
            .filter((record) => record.scientificName == originalScientificName)
            .map((record) => record.incorrectSynonym),
        ].includes(scientificName)
      ) {
        console.log(
          `Not processing ${scientificName} as a synonym of ${originalScientificName} because it has been marked as an incorrect synonym.`
        );
        continue;
      }

      const scientificNameLogStr = `${scientificName} (${originalScientificName})`;

      const allSearchResults = await fetchSearchResults(
        inputBoxElem,
        scientificName,
        scientificNameLogStr,
        taxon.rank
      );
      if (allSearchResults.length == 0) {
        continue;
      }

      const filteredSearchResults = findMatchingDropdownTaxonElement(
        allSearchResults,
        scientificName,
        taxon.rank,
        allowedIdsList
      );
      if (
        [SearchResultNoTaxaFound, SearchResultMultipleTaxaFound].includes(
          filteredSearchResults["result"]
        )
      ) {
        continue;
      } else if (
        filteredSearchResults["result"] == SearchResultCommonNameAlreadyExists
      ) {
        taxonFound = true;
        break;
      }

      const taxonId = dropdownItemToTaxonId(filteredSearchResults["elems"][0]);
      if (taxonId == null) {
        console.warn("Could not extract taxon ID.");
        continue;
      }

      await sleep(2000);

      // save common name so another script can pick it up and use on the common-name-adding page
      localStorage.setItem(
        "inat-common-name-data",
        JSON.stringify({ sk: commonName, sci: originalScientificName })
      );

      const addNameUrl = `https://www.inaturalist.org/taxa/${taxonId}/taxon_names/new`;
      console.log(
        `📝 Opening common-name-adding form for ${scientificNameLogStr} (${commonName})`
      );
      window.open(addNameUrl, "_blank");

      await sleep(3000); // Wait before moving to next taxon
      taxonFound = true;
      break;
    }

    if (taxonFound) {
      continue;
    } else {
      console.warn(
        `We couldn't find a matching taxon for ${originalScientificName} (${taxon.rank}), skipping it.`
      );
    }
  }

  console.log("✅ All taxa processed.");
}

findTaxaWithoutCommonName();
