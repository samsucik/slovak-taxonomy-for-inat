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
  const subtitleWithoutRankName = taxonRankInatNames.reduce(
    (subtitle, rankName) => subtitle.replace(rankName, "").trim(),
    subtitle
  );
  if (!subtitleWithoutRankName.length) {
    // the subtitle contained just a taxon rank name, implying the taxon doesn't have a common name assigned
    return null;
  }

  // remove the parenthesised part – when present, it contains just a synonym
  return title.replace(/\(.*\)/, "").trim();
}

const removeTaxonRankPrefix = (text) => {
  for (const rankName of taxonRankInatNames) {
    if (text.startsWith(rankName.toLowerCase())) {
      return text.slice(rankName.length);
    }
  }
  return text;
};

const removeWhiteSpaceAndSpecialChars = (text) => {
  return text.replace(/[\.\s×]/g, "");
};

const searchResultExactlyMatchesScientificName = (
  searchResultElem,
  scientificName,
  ignoreWhiteSpaceAndSpecialChars = false
) => {
  var title = extractTitleFromSearchResult(searchResultElem).toLowerCase();
  var subtitle =
    extractSubtitleFromSearchResult(searchResultElem).toLowerCase();
  var scientificNameProcessed = scientificName;
  if (ignoreWhiteSpaceAndSpecialChars) {
    title = removeWhiteSpaceAndSpecialChars(title);
    subtitle = removeWhiteSpaceAndSpecialChars(subtitle);
    scientificNameProcessed = removeWhiteSpaceAndSpecialChars(scientificName);
  }
  return (
    title == scientificNameProcessed.toLowerCase() ||
    title.includes(`(${scientificNameProcessed.toLowerCase()})`) ||
    subtitle == scientificNameProcessed.toLowerCase() ||
    removeTaxonRankPrefix(subtitle).trim() ==
      scientificNameProcessed.toLowerCase()
  );
};

const extractRankFromSearchResult = (searchResultElem, expectedRank) => {
  const subtitle = extractSubtitleFromSearchResult(searchResultElem);
  const foundRanks = taxonRankInatNames.filter((rank) =>
    subtitle.startsWith(rank)
  );
  if (!foundRanks.length) {
    // the rank could be species, subspecies, hybrid, form, ... for species we know the rank isn't part of the subtitle
    // if (expectedRank != "species") {
    //   console.log(`This subtitle doesn't seem to start with a rank: ${subtitle}. Expected rank: ${expectedRank} (${taxonRankMappingEnSk[expectedRank]})`)
    // }
    return null;
  } else {
    return taxonRankMappingSkEn[foundRanks[0]];
  }
};

const taxonRankMappingEnSk = {
  superorder: "Nadrad",
  order: "Rad",
  infraorder: "Podrad",
  suborder: "Podrad",
  superfamily: "Nadčeľaď",
  family: "Čeľaď",
  epifamily: "Epičeľaď",
  subfamily: "Podčeľaď",
  supertribe: "Nadkmeň",
  tribe: "Kmeň",
  subtribe: "Podkmeň",
  genus: "Rod",
  subgenus: "Podrod",
  complex: "Dokončiť", // TODO: change this in iNat!
  species: "Druh",
  section: "Sekcia",
  subsection: "Podsekcia",
  genushybrid: "Hybridný rod",
  subspecies: "Poddruh",
  form: "Forma",
  hybrid: "Kríženec",
  infrahybrid: "Infrahybrid",
  variety: "Varieta",
};
const taxonRankInatNames = Object.values(taxonRankMappingEnSk);

const taxonRankMappingSkEn = Object.fromEntries(
  Object.entries(taxonRankMappingEnSk).map((entry) => entry.reverse())
);

const SearchResultCommonNameAlreadyExists = "commonNameAlreadyExists";
const SearchResultNoTaxaFound = "noTaxaFound";
const SearchResultMultipleTaxaFound = "multipleTaxaFound";
const SearchResultOneTaxonFound = "oneTaxonFound";

const REPORT_EXISTING_DIFFERENT_COMMON_NAMES = true;

const filterByAllowedTaxonIds = (searchResultElements, allowedTaxaIdsList) => {
  if (allowedTaxaIdsList) {
    return searchResultElements.filter((elem) =>
      allowedTaxaIdsList.includes(parseInt(dropdownItemToTaxonId(elem)))
    );
  } else {
    return searchResultElements;
  }
};

const stringifyListOfSearchResultElems = (elems) => {
  return elems.map(
    (el) =>
      extractTitleFromSearchResult(el) +
      " | " +
      extractSubtitleFromSearchResult(el)
  );
};

function findMatchingDropdownTaxonElement(
  elements,
  scientificName,
  commonName,
  taxonRank,
  allowedTaxaIdsList
) {
  // filter based on list of allowed taxon IDs
  var filteredElements = filterByAllowedTaxonIds(elements, allowedTaxaIdsList);
  if (!filteredElements.length) {
    console.log(
      `Nothing found for '${scientificName}' (${taxonRank}) (filtering based on allowed IDs list)`
    );
    return { result: SearchResultNoTaxaFound, elems: [] };
  }

  // match scientific name
  const elementsFilteredBySciName = filteredElements.filter((el) => {
    return searchResultExactlyMatchesScientificName(el, scientificName);
  });
  if (!elementsFilteredBySciName.length) {
    const looselyFilteredElements = stringifyListOfSearchResultElems(
      filteredElements.filter((el) => {
        return searchResultExactlyMatchesScientificName(
          el,
          scientificName,
          true
        );
      })
    );

    console.log(
      `Nothing found for '${scientificName}' (${taxonRank}) (filtering based on scientific name). ${
        looselyFilteredElements.length ? looselyFilteredElements : ""
      }`
    );
    return { result: SearchResultNoTaxaFound, elems: looselyFilteredElements };
  } else {
    filteredElements = elementsFilteredBySciName;
  }

  // match taxon rank
  const elementsFilteredByTaxonRank = filteredElements.filter((el) =>
    searchResultMatchesTaxonRank(el, taxonRank)
  );
  if (!elementsFilteredByTaxonRank.length) {
    console.log(
      `Scientific name matches but taxon rank doesn't for these search results for ${scientificName} (${taxonRank}): ${stringifyListOfSearchResultElems(
        filteredElements
      )}`
    );
    return {
      result: SearchResultNoTaxaFound,
      elems: stringifyListOfSearchResultElems(filteredElements),
    };
  } else {
    filteredElements = elementsFilteredByTaxonRank;
  }

  // filter out taxa with common name already defined
  filteredElements = filteredElements.filter((el) => {
    const iNatCommonName = extractCommonNameFromSearchResult(el);
    if (
      REPORT_EXISTING_DIFFERENT_COMMON_NAMES &&
      iNatCommonName &&
      iNatCommonName.toLowerCase() != commonName.toLowerCase()
    ) {
      console.warn(
        `A common name exists for ${scientificName} and differs from the provided common name: iNat '${iNatCommonName}' vs provided '${commonName}'.`
      );
    }
    return iNatCommonName == null;
  });
  if (!filteredElements.length) {
    console.log(
      `No taxa with missing common name found for '${scientificName}' (${taxonRank})`
    );
    return { result: SearchResultCommonNameAlreadyExists, elems: [] };
  } else if (filteredElements.length > 1) {
    console.warn(
      `More than one match found for '${scientificName}' (${taxonRank}): ${filteredElements.map(
        (el) => el.innerText
      )}`
    );
    return { result: SearchResultMultipleTaxaFound, elems: [] };
  } else {
    return {
      result: SearchResultOneTaxonFound,
      elems: filteredElements,
    };
  }
}

function getScientificName(taxon) {
  return taxon[`${taxon.rank}_scientific`];
}

function getScientificSynonym(taxon) {
  if (taxon["synonyms"] != undefined) {
    return taxon.synonyms[0];
  } else {
    return null;
  }
}

function getCommonName(taxon) {
  return taxon[`${taxon.rank}_common`];
}

function startsWithSpecificTaxonRankName(str, taxonRankEn) {
  return (
    str == taxonRankMappingEnSk[taxonRankEn] ||
    str.startsWith(`${taxonRankMappingEnSk[taxonRankEn]} `)
  );
}

function startsWithATaxonRank(str) {
  for (taxonRank of taxonRankInatNames) {
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
    attemptCounter < 7
  ) {
    await sleep(300); // Wait for results to appear
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

// TODO continue here by correcting this function to account for things like forms, subspecies, etc. that don't include the taxon rank if common name exists.
function searchResultMatchesTaxonRank(searchResultElem, taxonRank) {
  const subtitleText = extractSubtitleFromSearchResult(searchResultElem);
  if (taxonRank != "species") {
    return startsWithSpecificTaxonRankName(subtitleText, taxonRank);
  } else {
    return (
      !startsWithATaxonRank(subtitleText) ||
      startsWithSpecificTaxonRankName(subtitleText, taxonRank)
    );
  }
}

function removeDiacritics(str) {
  return str.normalize("NFD").replace(/\p{Diacritic}/gu, "");
}

async function providedCommonNameAlreadyExists(
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

  const matchingSearchResults = Array.from(
    resultsContainer.querySelectorAll("li")
  ).filter((el) => {
    if (
      relevantTaxaIds &&
      !relevantTaxaIds.includes(parseInt(dropdownItemToTaxonId(el)))
    ) {
      return false;
    }

    const iNatCommonName = extractCommonNameFromSearchResult(el);
    const iNatRank = extractRankFromSearchResult(el, taxonRank);
    if (iNatCommonName == null) return false;
    const ranksMatch =
      iNatRank == null ? taxonRank == "species" : taxonRank == iNatRank; // for species we expect null iNat rank
    if (iNatCommonName.toLowerCase() == commonName.toLowerCase()) {
      console.log(
        `The common name for ${scientificName} already exists. ${
          ranksMatch
            ? "Ranks match."
            : `Ranks don't match: ${taxonRank} vs ${iNatRank}`
        }`
      );
      if (!iNatRank || iNatRank == taxonRank) return true;
    } else if (
      removeDiacritics(iNatCommonName.toLowerCase()) ==
      removeDiacritics(commonName.toLowerCase())
    ) {
      console.warn(
        `The common name for ${scientificName} already exists but differs in terms of diacritics: ${commonName} vs ${iNatCommonName}. ${
          ranksMatch
            ? "Ranks match."
            : `Ranks don't match: ${taxonRank} vs ${iNatRank}`
        }`
      );
      if (!iNatRank || iNatRank == taxonRank) return true;
    }

    return false;
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
        `No scientific name provided for this taxon (${JSON.stringify(
          taxon
        )}), skipping it.`
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
      await providedCommonNameAlreadyExists(
        inputBoxElem,
        commonName,
        originalScientificName,
        taxon.rank,
        allowedIdsList
      )
    )
      continue;

    var scientificNameCandidates =
      taxon["synonyms"] != undefined
        ? [...new Set([originalScientificName, ...taxon["synonyms"]])]
        : [originalScientificName];
    var closeSearchResults = [];
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
        commonName,
        taxon.rank,
        allowedIdsList
      );
      if (filteredSearchResults["result"] == SearchResultNoTaxaFound) {
        closeSearchResults = closeSearchResults.concat(
          filteredSearchResults["elems"]
        );
        continue;
      } else if (
        filteredSearchResults["result"] == SearchResultMultipleTaxaFound
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

      await sleep(3000);

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

      await sleep(2000); // Wait before moving to next taxon
      taxonFound = true;
      break;
    }

    if (taxonFound) {
      continue;
    } else {
      console.warn(
        `We couldn't find a matching taxon for ${originalScientificName} (${
          taxon.rank
        }), skipping it.${
          closeSearchResults.length
            ? ` The closest search results were: ${closeSearchResults}`
            : ""
        }`
      );
    }
  }

  console.log("✅ All taxa processed.");
}

findTaxaWithoutCommonName();
