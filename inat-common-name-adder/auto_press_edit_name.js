function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function findAndPressEditNameButtons() {
  await sleep(2000);
  const tableCellsWithLinks = document.querySelectorAll(".TaxonomyTab tbody td a");
  const editButtons = Array.from(tableCellsWithLinks).filter(el => el.innerText == "Upraviť");
  if (editButtons.length != 1) {
    console.log(`Found ${editButtons.length} edit button(s)`);
  } else {
    console.log("Found one button and will click it", editButtons[0]);
    editButtons[0].click();
  }
}

findAndPressEditNameButtons();
