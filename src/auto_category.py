
import json
import os

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import pickle

from .frame_csv import frame_csv, frame_dir, save_reconciled_data

from dotenv import load_dotenv
load_dotenv()


model_pickle_path = 'data/naive_bayes_model.pkl'


def load_categories():
    lookup_json_path = os.getenv("CATEGORY_LOOKUP_PATH")
    with open(lookup_json_path, 'r') as f:
        lookup_table = json.load(f)
    return list(lookup_table.keys())    

def load_lookup_table():
    lookup_json_path = os.getenv("CATEGORY_LOOKUP_PATH")
    with open(lookup_json_path, 'r') as f:
        lookup_table = json.load(f)
    return lookup_table

def desc2category(description, lookup_table):
    for cat, keywords in lookup_table.items():
        filtered_keywords = [kw for kw in keywords if kw]
        if not filtered_keywords:
            continue
        if any(keyword.lower() in description.lower() for keyword in filtered_keywords):
            return cat
    return "other"


def category_from_lookup(input_dir, output_dir, lookup_table):
    os.makedirs(output_dir, exist_ok=True)

    for csv_file in os.listdir(input_dir):
        if csv_file.endswith(".csv"):
            file_path = os.path.join(input_dir, csv_file)
            df = frame_csv(file_path)

            df['category'] = df['description'].apply(lambda x: desc2category(x, lookup_table))
            other_count = (df['category']== 'other').sum()

            output_file_path = os.path.join(output_dir, csv_file)
            df.to_csv(output_file_path, index=False)
            print(f"{csv_file}: {other_count:<2} rows categorized as 'other'")



class CategoryClassifier:
    def __init__(self, csv_dir):
        
        self.categories = load_categories()
        self.lookup_table = load_lookup_table()
        self.vectorizer = None
        self.model = None
        self.model_path = None

        self.df = frame_dir(csv_dir)
        
    def build_X_y(self):
        y = self.df['category']
        X = self.df['description'].astype(str)
        return X, y

    def train(self):
        X, y = self.build_X_y()
        non_other_indices = y != "other"
        X_train, y_train = X[non_other_indices], y[non_other_indices]
        
        self.vectorizer = CountVectorizer()
        X_transformed = self.vectorizer.fit_transform(X_train)

        self.model = MultinomialNB()
        self.model.fit(X_transformed, y_train)

        if self.model_path:
            with open(self.model_path, 'wb') as f:
                pickle.dump((self.vectorizer, self.model), f)

        y_train_pred = self.model.predict(X_transformed)
        accuracy = accuracy_score(y_train, y_train_pred)
        print(f"Training completed with an accuracy of: {accuracy:.4f}")


    def predict(self, inplace=False):
        if not self.model or not self.vectorizer:
            raise ValueError("Model is not trianed or loaded. Please train the model first.")

        X, y = self.build_X_y()

        other_indices = y == "other"
        X_other = X[other_indices]

        X_transformed = self.vectorizer.transform(X_other)
        yhat = self.model.predict(X_transformed)

        if inplace:
            self.df.loc[other_indices, 'category'] = yhat
            save_reconciled_data(self.df)        
        return yhat
    
        
    def load_model(self, model_path):
        self.model_path = model_path
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.vectorizer, self.model = pickle.load(f)
            print("Model loaded successfully.")
        else:
            print("No pre-trained model found. Please train the model first")

            
