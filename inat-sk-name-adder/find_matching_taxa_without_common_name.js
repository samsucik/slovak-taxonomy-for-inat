function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// given a search term that is a scientific name:
// when SK name exists, .subtitle contains the primary scientific name.
// the .title element contains the SK name if it exists and the primary scientific name otherwise. in both case, it also contains the scientific name we searched for if it's a synonym.
// the .subtitle element ALWAYS contains the taxon rank except for when the taxon rank is "species" ("druh") and a common name exists.
function lacksCommonName(subtitleStr, taxonRankEn) {
    return subtitleStr == taxonRankMappingEnSk[taxonRankEn];
}

const taxonRankMappingEnSk = {
    "order": "Rad",
    "infraorder": "Podrad",
    "superfamily": "Nadčeľaď",
    "family": "Čeľaď",
    "subfamily": "Podčeľaď",
    "genus": "Rod",
    "species": "Druh"
}

const slovakTaxonRankNames = Object.values(taxonRankMappingEnSk);

// taxon rank and scientific name must match
function findMatchingDropdownTaxonElement(elements, scientificName, taxonRank) {
  const elementsMatchingScientificName = elements.filter(el => {
    // console.log(`inner text '${el.innerText.toLowerCase()}' vs '${scientificName.toLowerCase()}'`, el.innerText.toLowerCase().includes(scientificName.toLowerCase()));
    return el.innerText.toLowerCase().includes(scientificName.toLowerCase());
  });
  if (elementsMatchingScientificName.length == 0) {
    console.warn(`Nothing found for '${scientificName}' (scientific name match)`);
    return null;
  }

  const elementsMatchingTaxonRank = elementsMatchingScientificName.filter(el => {
    const subtitleText = el.querySelector('.subtitle').innerText.replace("Zobraziť", "").trim();
    if (taxonRank != "species") {
      return startsWithSpecificTaxonRankName(subtitleText, taxonRank);
    } else {
      return !startsWithATaxonRank(subtitleText) || startsWithSpecificTaxonRankName(subtitleText, taxonRank);
    }
  })
  if (elementsMatchingTaxonRank.length == 0) {
    console.warn(`Nothing found for '${scientificName}' (${taxonRank}) (taxon rank match)`);
    return null;
  }

  const elementsLackingCommonName = elementsMatchingTaxonRank.filter(el => {
    const subtitleText = el.querySelector('.subtitle').innerText.replace("Zobraziť", "").trim();
    return !containsCommonName(subtitleText, taxonRank);
  })
  if (elementsLackingCommonName.length == 0) {
    console.info(`Common name seems to exist already for '${scientificName}' (${taxonRank})`);
    return null;
  }

  const elementsWithExactScientificNameMatch = elementsLackingCommonName.filter(el => {
    const title = el.querySelector('.title').innerText.toLowerCase();
    return title == scientificName.toLowerCase() || title.includes(`(${scientificName.toLowerCase()})`);
  });

  if (elementsWithExactScientificNameMatch.length == 0) {
    console.info(`No taxa lack a common name and match exactly the scientific name for '${scientificName}' (${taxonRank})`);
    return null;
  }

  if (elementsWithExactScientificNameMatch.length > 1) {
    console.warn(`More than one match found for '${scientificName}' (${taxonRank}): ${elementsWithExactScientificNameMatch.map(el => el.innerText)}`);
    return null;
  }

  return elementsWithExactScientificNameMatch[0];
}

function getScientificName(taxon) {
    return taxon.rank == "superfamily" ? taxon.superfamily_scientific : taxon.rank == "family" ? taxon.family_scientific : taxon.rank == "subfamily" ? taxon.subfamily_scientific : taxon.rank == "genus" ? taxon.genus_scientific : taxon.rank == "species" ? taxon.species_scientific : undefined;
}

function getCommonName(taxon) {
    return taxon.rank == "superfamily" ? taxon.superfamily_common : taxon.rank == "family" ? taxon.family_common : taxon.rank == "subfamily" ? taxon.subfamily_common : taxon.rank == "genus" ? taxon.genus_common : taxon.rank == "species" ? taxon.species_common : undefined;
}

function startsWithSpecificTaxonRankName(str, taxonRankEn) {
    return str == taxonRankMappingEnSk[taxonRankEn] || str.startsWith(`${taxonRankMappingEnSk[taxonRankEn]} `);
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

async function processTaxa() {
    const taxaListPath = chrome.runtime.getURL('taxa.json');
    const taxaList = await (await fetch(taxaListPath)).json();

    await sleep(2000); // give the website enough time to finish initialising everything

  const input = document.querySelector('#q');
  if (!input) {
    console.error("❌ Search input #q not found.");
    return;
  }

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
    //   }
    const scientificName = getScientificName(taxon);
    // console.info(`Processing "${scientificName}"`);

    const commonName = getCommonName(taxon);
    if (!commonName) {
        continue;
    }

    // Clear previous value
    input.value = '';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    await sleep(500);

    // Type the scientific name
    input.value = scientificName;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));

    let resultsContainer;
    let attemptCounter = 0;
    while ((!resultsContainer || Array.from(resultsContainer.querySelectorAll('li')).length == 0) && attemptCounter < 10) {
        await sleep(500); // Wait for results to appear
        resultsContainer = document.querySelector('.ac-menu.open');
        attemptCounter = attemptCounter + 1;
        if (resultsContainer) {
            break;
        } else {
          // console.log(attemptCounter);
        }
    }
    if (!resultsContainer) {
      console.warn(`❌ No search results container for "${scientificName}"`);
      continue;
    }

    const items = Array.from(resultsContainer.querySelectorAll('li'));
    if (items.length === 0) {
      console.warn(`❌ No results in the results container for "${scientificName}"`);
      continue;
    }

    const matchingItem = findMatchingDropdownTaxonElement(items, scientificName, taxon.rank);
    if (matchingItem == null) {
      continue;
    }

    // Extract the taxon ID from the link
    const link = matchingItem.querySelector('a');
    if (!link || !link.href) {
      console.warn(`❌ Could not extract link for "${scientificName}"`);
      continue;
    }

    const taxonIdMatch = link.href.match(/\/taxa\/(\d+)/);
    if (!taxonIdMatch) {
      console.warn(`❌ Could not extract taxon ID from URL: ${link.href}`);
      continue;
    }

    const taxonId = taxonIdMatch[1];
    
    await sleep(2000);

    // Save Slovak name for use in the next page
    localStorage.setItem('inat-sk-name-data', JSON.stringify({ sk: commonName, sci: scientificName }));

    const addNameUrl = `https://www.inaturalist.org/taxa/${taxonId}/taxon_names/new`;
    console.log(`📝 Opening name form for "${scientificName}" (${commonName})`);
    window.open(addNameUrl, '_blank');

    await sleep(3000); // Wait before moving to next taxon
  }

  console.log("✅ All taxa processed.");
}

processTaxa();
