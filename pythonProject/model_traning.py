import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pickle
import cloudpickle as pickle


# Định nghĩa hàm tokenizer
def custom_tokenizer(text):
    return text.split(",")

# Đọc dữ liệu từ file CSV
data_path = "data/disease_data.csv"  # Thay đường dẫn file cho phù hợp
df = pd.read_csv(data_path)

# Chuẩn bị dữ liệu
X = df["Symptoms"]  # Cột triệu chứng
y = df["Disease"]   # Cột bệnh

# Vector hóa triệu chứng bằng TF-IDF
vectorizer = TfidfVectorizer(tokenizer=custom_tokenizer)  # Sử dụng hàm thay vì lambda
X_vectorized = vectorizer.fit_transform(X)

# Chia dữ liệu train/test
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

# Huấn luyện mô hình Logistic Regression
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# Lưu vectorizer và mô hình vào file
with open("models/vectorizer.pkl", "wb") as vec_file:
    pickle.dump(vectorizer, vec_file)

with open("models/model.pkl", "wb") as model_file:
    pickle.dump(model, model_file)

print("Mô hình đã được huấn luyện và lưu.")
