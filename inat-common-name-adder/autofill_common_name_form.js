function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const DATA_KEY = "inat-common-name-data";

function createNote(scientificName) {
  var note = null;
  // note = `Adding a missing common name for ${scientificName}. Source: ZOZNAM MOTÝĽOV (LEPIDOPTERA) ZISTENÝCH NA SLOVENSKU (CHECKLIST OF LEPIDOPTERA RECORDED IN SLOVAKIA). Entomofauna carpathica, 2022, 34 (Supplementum 2): 1-181. Accessed at https://entomospol.sk/suplements/priloha-c-2/`;
  // note = `Adding a missing common name for ${scientificName}. Source: Ferianc, O. (1975). Slovenské mená hmyzu. Slovensko: Veda.`;
  note = `Adding a missing common name. Source: Kliment J., Hrabovský M., Letz D. R., Eliáš P. ml., Kučera J., Mártonfi P., Guričanová D., Vančová I., Feráková V., Goliašová K., Hodálová I., Kochjarová J., Marhold K., Turisová I. 2024+: Databáza slovenského botanického menoslovia – cievnaté rastliny. https://slovakplantnames.sav.sk Accessed November 2025. Database entry for ${scientificName}`;
  if (note == null) {
    alert("Looks like you forgot to define a note for this taxon change in the file 'autofill_common_name_form.js'!")
  }
  return note;
}

const scientificNamesMatch = (searchedName, iNatName) => {
  if (searchedName.toLowerCase() == iNatName.toLowerCase()) return true;
  if (iNatName.includes(" f.") && iNatName.replace(/ f.\s*/, " ").toLowerCase() == searchedName.toLowerCase()) return true;
  if (iNatName.includes(" var.") && iNatName.replace(/ var.\s*/, " ").toLowerCase() == searchedName.toLowerCase()) return true;
  if (iNatName.includes(" ssp.") && iNatName.replace(/ ssp.\s*/, " ").toLowerCase() == searchedName.toLowerCase()) return true;
  return false;
}

const taxonNameAlreadyExists = () => {
  const errorExplanationElement = document.querySelector("#error_explanation");
  if (errorExplanationElement && errorExplanationElement.innerText.includes("Name already exists for this taxon in this lexicon")) return true;
  return false;
}

const closeTab = () => {
  localStorage.removeItem(DATA_KEY);
  window.close();
}

async function autofillCommonName() {
  if (taxonNameAlreadyExists()) {
    console.log("Looks like the common name already exists, let's auto-close the name adding form.")
    closeTab();
    return;
  }

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
      scientificNamesMatch(data.sci, document.querySelector("h2 .sciname").innerText)
    ) {
      const saveBtn = document.querySelector('input[name="commit"]');
      if (saveBtn) {
        saveBtn.click();
      }
    }
  }
}

autofillCommonName();
