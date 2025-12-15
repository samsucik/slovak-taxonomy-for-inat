import pandas as pd
import datetime

df_all_inat_names = pd.read_csv("VernacularNames-slovak-dec.csv", parse_dates=["created"])
df_all_inat_names["vernacularNameLowerCase"] = df_all_inat_names["vernacularName"].str.lower()
df_existing_names = pd.read_csv("data-sources/slovenske-botanicke-menoslovie-2024/existing_names_not_covered.csv")

attributions = {}

for _, taxon_with_existing_name in df_existing_names.iterrows():
    # sciName,commonNameSBM,commonNameINat,differenceCategory
    new_name = taxon_with_existing_name["commonNameSBM"]
    previous_name = taxon_with_existing_name["commonNameINat"]
    previous_name_context = df_all_inat_names[df_all_inat_names["vernacularNameLowerCase"] == previous_name.lower()]
    if len(previous_name_context) == 0:
        print(f"oh no – no records found for this previous name being added: '{previous_name}'")
        continue
    elif len(previous_name_context) > 1:
        print(f"Wow, multiple records found for the name '{previous_name}' being added previously (we wanted to add '{new_name}'):")
        [print(f"- '{row['vernacularName']}' added by '{row['contributor']}' on {row['created'].strftime('%d/%m/%Y')} (https://www.inaturalist.org/taxa/{row['id']})") for _, row in previous_name_context.iterrows()]
        continue
    else:
        previous_name_context = previous_name_context.iloc[0]
    
    contributor = previous_name_context['contributor']
    if contributor not in attributions:
        attributions[contributor] = []
    attributions[contributor].append({
        "sciName": taxon_with_existing_name["sciName"],
        "id": previous_name_context["id"],
        "date": previous_name_context["created"],
        "new_name": new_name,
        "previous_name": previous_name_context["vernacularName"]
    })

for contributor, items in attributions.items():
    print(f"Contributor '{contributor}'")
    name_mapping = dict()
    for item in sorted(items, key=lambda x: x['date']):
        print(f" - added '{item['previous_name']}' on {item['date'].strftime('%d/%m/%Y')}, should change to '{item['new_name']}' at https://www.inaturalist.org/taxa/{item['id']}")
        if item['date'].replace(tzinfo=None) < datetime.datetime(2025, 11, 24):
            name_mapping[item['previous_name']] = {"sciName": item["sciName"], "newCommonName": item['new_name']}
    print(name_mapping)

