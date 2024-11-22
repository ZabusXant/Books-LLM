import pandas as pd
import numpy as np

data = pd.read_csv('../data/browser_data.csv', dtype='str', sep='^', encoding='utf-8')

# Removing duplicates, there were no duplicate rows while exploring the data
print('Original size is', data.shape[0])
data.dropna(inplace=True)
print('Size after dropping rows with null values is', data.shape[0])

# Auxiliary dict that will be used in transforming the ratings
ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

# Applying the simple transformations on the dataframe
data['category'] = np.where(data['category'].isin(["Default", "Add a comment"]), "Uncategorized", data['category'])
data['price'] = data['price'].str.replace("£", "", regex=False).astype(float)
data['description'] = data['description'].apply(
    lambda st: st[:-8] if isinstance(st, str) and st.endswith("...more") else st)
data['rating'] = data['rating'].map(ratings)
data['availability'] = data['availability'].str.extract(r"(\d+)").astype(int)

data.to_csv("../data/processed_data.csv", index=False, sep='^', encoding="utf-8")
print("Data has been processed successfully")
