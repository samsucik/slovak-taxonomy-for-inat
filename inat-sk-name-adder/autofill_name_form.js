function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const DATA_KEY = 'inat-sk-name-data';

async function closeTabIfApplicable() {
  const dataRaw = localStorage.getItem(DATA_KEY);
  if (dataRaw) {
    const data = JSON.parse(dataRaw);

    // Fill in the "Názov" (Name) field
    const nameInput = document.querySelector('#taxon_name_name');
    if (nameInput) {
      nameInput.value = data.sk;
    }

    // Fill in the "Poznámka" (Note) field
    const noteInput = document.querySelector('#taxon_name_audit_comment');
    if (noteInput) {
      noteInput.value = `Adding a missing common name for ${data.sci}. Source: ZOZNAM MOTÝĽOV (LEPIDOPTERA) ZISTENÝCH NA SLOVENSKU (CHECKLIST OF LEPIDOPTERA RECORDED IN SLOVAKIA). Entomofauna carpathica, 2022, 34 (Supplementum 2): 1-181. Accessed at https://entomospol.sk/suplements/priloha-c-2/`;
    }

    const saveBtn = document.querySelector('input[name="commit"]');
    if (saveBtn) {
      // saveBtn.focus();
      if (document.querySelector('h2 .sciname').innerText.toLowerCase() == data.sci.toLowerCase()) {
        saveBtn.click();
      }
    }

    // Clear stored data so it doesn’t persist unnecessarily
    // localStorage.removeItem(DATA_KEY);
  }
}

closeTabIfApplicable()
