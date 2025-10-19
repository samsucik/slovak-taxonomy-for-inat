# iNaturalist Common Name Adder Chrome extension

A Google Chrome extension which runs on the iNaturalist website and automatically adds Slovak (or possibly other) common names to taxa from a pre-defined list.

The extension simulates the flow a logged-in user of iNaturalist would go through on the iNat web: Use the taxon search box to find taxa, open their dedicated taxon pages, and add the common names therein.

## How to install and run

Before using the extension, make sure it's going to fill the Note field appropriately in the common name-adding form: Add your note template by editing the `createNote` function in [autofill_common_name_form.js](./autofill_common_name_form.js).

Now install the extension:

1. in your Google Chrome browser, navigate to [chrome://extensions](chrome://extensions)
2. enable "Developer mode"
3. click "Load unpacked" and choose this directory
4. visit [inaturalist.org/taxa](https://inaturalist.org/taxa)
5. open the DevTools (press F12)
6. watch the extension automatically go through the list of taxa, looking them up, opening their taxon pages, and adding the common names.
_Note: When the extension is certain that it's adding a common name to the right taxon, it even dares to auto-save the common name and close the taxon page. Otherwise, you have to double-check and save the common name manually._
7. watch the Console in the DevTools panel – the extension adds a warning (or error) message therein whenever it can't find a taxon in iNat (or in case of some other issues)
8. once you're done, you can deactivate (or remove) the extension on the [chrome://extensions](chrome://extensions) page if you don't plan to use it any further
9. whenever you make changes to the extension's source files (essentially, to any files within this directory), before running the extension, reload it from the [chrome://extensions](chrome://extensions) page
