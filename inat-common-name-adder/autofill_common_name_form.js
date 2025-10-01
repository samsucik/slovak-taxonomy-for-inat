function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const DATA_KEY = "inat-common-name-data";

function createNote(scientificName) {
  // return `Adding a missing common name for ${scientificName}. Source: ZOZNAM MOTÝĽOV (LEPIDOPTERA) ZISTENÝCH NA SLOVENSKU (CHECKLIST OF LEPIDOPTERA RECORDED IN SLOVAKIA). Entomofauna carpathica, 2022, 34 (Supplementum 2): 1-181. Accessed at https://entomospol.sk/suplements/priloha-c-2/`;
  // return `Adding a missing common name for ${scientificName}. Source: Ferianc, O. (1975). Slovenské mená hmyzu. Slovensko: Veda.`;
  return `My note for the taxon '${scientificName}' (change this note template!)`;
}

async function autofillCommonName() {
  const dataRaw = localStorage.getItem(DATA_KEY);
  if (dataRaw) {
    const data = JSON.parse(dataRaw);

    // fill in the name field
    const nameInput = document.querySelector("#taxon_name_name");
    if (nameInput) {
      nameInput.value = data.sk;
    }

    // fill in the note field
    const noteInput = document.querySelector("#taxon_name_audit_comment");
    if (noteInput) {
      noteInput.value = createNote(data.sci);
    }

    // if the scientific name matches exactly the one we searched for,
    // we're certain enough to submit the common name automatically,
    // i.e. without a human checking it first
    if (
      document.querySelector("h2 .sciname").innerText.toLowerCase() ==
      data.sci.toLowerCase()
    ) {
      const saveBtn = document.querySelector('input[name="commit"]');
      if (saveBtn) {
        saveBtn.click();
      }
    }
  }
}

autofillCommonName();
