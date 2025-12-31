# TO-DO list

- see where we added more than one name to a taxon: run `detect_multiple_added_names_per_taxon.py`
- for slovak names belonging to more than 1 taxon: wait for resolution from DRL
- groups: see if they exist under a different rank (form/variety), otherwise move on
- search by synonyms: first from the DB then from GBIF/POWO
- where a taxon is missing and could be requested to be created, send a list to DRL first (as some taxa are questionable in the first place)
- contact others based on the results of running `filter_existing_names.py` and then `attribute_existing_names.py` (keep track of resolved cases in `existing_names_covered.csv`)
- names of orders! (MFS)
- check all the names assigned with the help of synonyms (`sbm_to_inat_sci_name_mapping.csv`) and auto-detect those that are based on heterotypic (taxonomical) rather than homotypic (nomenclatural) synonyms. POWO should serve as a guide here.

## Handling tough-to-find taxa

- go through ALL synonyms (but only accepted ones??) until scientific name match found
- accept similar taxon ranks in SOME cases: family/subfamily/superfamily, species/subspecies (BUT only if exact rank match is not found!)


# Preklepy, ktore som nevedel jednoznacne opravit

Colchicum cilicicum je jesienka cilícijská, ale Abies cilicica je jedľa cilicijská
Alseis yucatanensis je alzea yucatánska, ale Agave fourcroydes je agáva yukatánska
Physalis franchetii je machovka Franchettova, ale Cotoneaster franchetii je skalník Franchetov
Robinia ×margarettae je agát Margaretin, ale Lapidaria margaretae je lapidária Margarethina (nehovorim, ze je to zle, len to vyzera len trosku podozrivo)
Elodea nuttallii je vodomor Nuttallov, ale Cornus nuttallii je svíb Nuttalov
Rosa roxburghii je ruža Roxburghova, ale Pinus roxburghii je borovica Roxburgova
Glycydendron amazonicum je sladovník amazónsky, ale Nidularium amazonicum je nidulárium amazonské
Dalbergia cearensis je dalbergia cearská, ale Amburana cearensis je amburana cearáska
tilandsia bradatcovitá ("lousianský mach") (chcelo byt "louisianský mach"?)

Reflecting the newest corrections made in the online version of the new Slovak nomenclature of vascular plants (Kliment J., Hrabovský M., Letz D. R., Eliáš P. ml., Kučera J., Mártonfi P., Guričanová D., Vančová I., Feráková V., Goliašová K., Hodálová I., Kochjarová J., Marhold K., Turisová I. 2024+: Databáza slovenského botanického menoslovia – cievnaté rastliny. https://slovakplantnames.sav.sk).

# Taxony, ktore sa nedaju jednoznacne najst

ku comu priradit meno "voškovník polabský"? lebo Xanthium albinum nie uplne existuje, resp. je to komplikovane...

# Opravovane mena, ktore sa nedaju v iNat lahko najst
Chamaesium jiulongense (chamézium jiugonské → ch. ťioukunské)
Cyclea longgangensis (cyklea longganská → c. lungkanská)
Hieracium pietroszenze (jastrabník pietrošský → j. pietrosulský)
Neolemonniera ogouensis (neolemoniéra ogouéska → n. ogoouéska)
Pseudopanax chatmanicus (paženšen chatamský → p. chathamský)
Ranunculus niepolomicensis (iskerník niepolomický → i. niepołomický)
Portulaca oleracea subsp. zaffranii – portulac(k)a zeleninová Zaffranova


# Preklepy vo vedeckych menach
- Mesophaerum pectinatum (Mesosphaerum pectinatum)
- Haworthiopsis tesselata (Haworthiopsis tessellata)
- Eustoma russelianum (Eustoma russellianum)
- Cochemiea mazatlensis (Cochemiea mazatlanensis)
- Myrceugenia  exsucca (Myrceugenia exsucca)
- Pseudobombax  septenatum (Pseudobombax septenatum)
- Hymenopus  macrophyllus (Hymenopus macrophyllus)
- Myrceugenia  exsucca (Myrceugenia exsucca)
- Pseudobombax  septenatum (Pseudobombax septenatum)

# Preklepy v slovenskych menach
- žltuškovaté (Marek Hrusovsky)
