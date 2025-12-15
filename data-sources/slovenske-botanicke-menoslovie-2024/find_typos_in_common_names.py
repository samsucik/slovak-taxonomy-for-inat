import pandas as pd

df_common_names = pd.read_csv("common_names.csv")
common_names_words = []
for name in df_common_names["commonName"].values:
    for name_part in name.split():
        common_names_words.append(
            name_part.replace('"', "").replace("(", "").replace(")", "").strip()
        )
word_frequencies = pd.Series(common_names_words).value_counts()
infrequent_words = sorted([word for word, freq in word_frequencies.items() if freq == 1])
pd.DataFrame(sorted(infrequent_words)).to_csv("infrequent_common_name_words.csv", index=False)
