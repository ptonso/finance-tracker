from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import pickle


# class CategoryClassifier:
#     def __init__(self, csv_dir):
#         self.categories = load_categories()
#         self.lookup_table = load_category_lookup()
#         self.vectorizer = None
#         self.model = None
#         self.model_path = None

#         self.df = frame_dir(csv_dir)
        
#     def build_X_y(self):
#         y = self.df['category']
#         X = self.df['description'].astype(str)
#         return X, y

#     def train(self):
#         X, y = self.build_X_y()
#         non_default_indices = y != DEFAULT_CATEGORY
#         X_train, y_train = X[non_default_indices], y[non_default_indices]
        
#         self.vectorizer = CountVectorizer()
#         X_transformed = self.vectorizer.fit_transform(X_train)

#         self.model = MultinomialNB()
#         self.model.fit(X_transformed, y_train)

#         if self.model_path:
#             with open(self.model_path, 'wb') as f:
#                 pickle.dump((self.vectorizer, self.model), f)

#         y_train_pred = self.model.predict(X_transformed)
#         accuracy = accuracy_score(y_train, y_train_pred)
#         print(f"Training completed with an accuracy of: {accuracy:.4f}")


#     def predict(self, inplace=False):
#         if not self.model or not self.vectorizer:
#             raise ValueError("Model is not trianed or loaded. Please train the model first.")

#         X, y = self.build_X_y()

#         default_indices = y == DEFAULT_CATEGORY
#         X_default = X[default_indices]

#         X_transformed = self.vectorizer.transform(X_default)
#         yhat = self.model.predict(X_transformed)

#         if inplace:
#             self.df.loc[default_indices, 'category'] = yhat
#             save_reconciled_data(self.df)        
#         return yhat
    
        
#     def load_model(self, model_path):
#         self.model_path = model_path
#         if os.path.exists(self.model_path):
#             with open(self.model_path, 'rb') as f:
#                 self.vectorizer, self.model = pickle.load(f)
#             print("Model loaded successfully.")
#         else:
#             print("No pre-trained model found. Please train the model first")

            
