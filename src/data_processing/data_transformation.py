import pandas as pd
import numpy as np
from src.utils.minio_interaction import MinIO
from src.utils.postgres_interaction import Database


class Transformer(Database, MinIO):

    data: pd.DataFrame
    # Auxiliary dict that will be used in transforming the ratings
    ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def __init__(self):
        Database.__init__(self)
        MinIO.__init__(self)
        csv_file = self.download_csv_file_from_minio(bucket='test-bucket', file_name='test_raw_data.csv')
        self.data = pd.read_csv(csv_file, dtype='str', sep='^', encoding='utf-8')

    def remove_duplicates(self):
        # Removing duplicates, there were no duplicate rows while exploring the data
        print('Original size is', self.data.shape[0])
        self.data.dropna(inplace=True)
        print('Size after dropping rows with null values is', self.data.shape[0])

    def apply_transformations(self):
        # Applying the simple transformations on the dataframe
        self.data['category'] = np.where(self.data['category'].isin(["Default", "Add a comment"]),
                                         "Uncategorized", self.data['category'])
        self.data['price'] = self.data['price'].str.replace("£", "", regex=False).astype(float)
        self.data['description'] = self.data['description'].apply(
            lambda st: st[:-8] if isinstance(st, str) and st.endswith("...more") else st)
        self.data['rating'] = self.data['rating'].map(self.ratings)
        self.data['availability'] = self.data['availability'].str.extract(r"(\d+)").astype(int)

    def store_clean_data(self):
        self.upload_df_to_minio(bucket='processed-data', file_name='test_processed_data.csv', df=self.data)
        self.upload_df_to_table(table_name='test_clean_data', data=self.data)
        print("Data has been processed successfully")

    def run_transformer(self):
        self.remove_duplicates()
        self.apply_transformations()
        self.store_clean_data()


if __name__ == "__main__":
    transformer = Transformer()
    transformer.run_transformer()
