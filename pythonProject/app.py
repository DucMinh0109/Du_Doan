from flask import Flask, render_template, request, jsonify
from fuzzywuzzy import process
from docx import Document
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer

# Initialize Flask app
app = Flask(__name__)

# Load the disease data from the Word document
def read_data_from_word(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File không tồn tại: {file_path}")

        doc = Document(file_path)
        data = []
        current_disease = {}

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text.startswith("Tên bệnh:"):
                if current_disease:
                    data.append(current_disease)
                current_disease = {"Disease": text.replace("Tên bệnh:", "").strip()}
            elif text.startswith("Triệu chứng:"):
                current_disease["Symptoms"] = text.replace("Triệu chứng:", "").strip()
            elif text.startswith("Nguyên nhân:"):
                current_disease["Cause"] = text.replace("Nguyên nhân:", "").strip()
            elif text.startswith("Phòng ngừa:"):
                current_disease["Prevention"] = text.replace("Phòng ngừa:", "").strip()
            elif text.startswith("Điều trị:"):
                current_disease["Treatment"] = text.replace("Điều trị:", "").strip()

        if current_disease:
            data.append(current_disease)
        return data
    except Exception as e:
        print(f"Error reading Word file: {e}")
        return []

# Hàm tìm kiếm dựa trên triệu chứng (khớp hoàn toàn)
def search_diseases_by_symptom(input_symptom, disease_data):
    results = []
    input_symptoms = [sym.strip() for sym in input_symptom.split(",")]

    for disease in disease_data:
        disease_symptoms = [sym.strip().lower() for sym in disease["Symptoms"].split(",")]

        matched_symptoms = [sym for sym in input_symptoms if sym in disease_symptoms]

        if matched_symptoms:
            probability = (len(matched_symptoms) / len(disease_symptoms)) * 80  # Max 80%
            results.append({
                "Disease": disease["Disease"],
                "Probability": probability,
                "Matched Symptoms": ", ".join(matched_symptoms),
                "Symptoms": disease["Symptoms"],
                "Cause": disease["Cause"],
                "Prevention": disease["Prevention"],
                "Treatment": disease["Treatment"]
            })

    results.sort(key=lambda x: x["Probability"], reverse=True)

    for result in results:
        result["Probability"] = min(result["Probability"], 90)

    return results

# Load dữ liệu bệnh từ file Word
disease_data_path = "disease_data.docx"
disease_data = read_data_from_word(disease_data_path)

# Load mô hình và vectorizer
try:
    with open("models/vectorizer.pkl", "rb") as vec_file:
        vectorizer = pickle.load(vec_file)
    with open("models/model.pkl", "rb") as model_file:
        model = pickle.load(model_file)
except Exception as e:
    print(f"Lỗi khi tải mô hình hoặc vectorizer: {e}")
    vectorizer = None
    model = None

@app.route("/")
def home():
    return render_template("index.html", diseases=disease_data)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        symptoms = request.form.get("symptoms", "").lower().strip()
        if not symptoms:
            return render_template("index.html", error="Vui lòng nhập triệu chứng.")

        # Sử dụng hàm tìm kiếm với triệu chứng
        search_results = search_diseases_by_symptom(symptoms, disease_data)

        # Lọc triệu chứng không khớp
        matched_symptoms = {res["Matched Symptoms"] for res in search_results}
        unmatched_symptoms = [sym for sym in symptoms.split(",") if sym not in matched_symptoms]

        ml_results = []
        if unmatched_symptoms and vectorizer and model:
            symptoms_vectorized = vectorizer.transform([",".join(unmatched_symptoms)])
            predictions = model.predict_proba(symptoms_vectorized)[0]

            # Map dự đoán từ mô hình vào kết quả
            ml_results = []
            for disease, prob in zip(model.classes_, predictions):
                if prob > 0.01:  # Chỉ hiển thị bệnh với xác suất > 1%
                    ml_results.append({
                        "Disease": disease,
                        "Probability": f"{prob * 100:.2f}%",
                        "Cause": next((d["Cause"] for d in disease_data if d["Disease"] == disease), "Không có thông tin"),
                        "Symptoms": next((d["Symptoms"] for d in disease_data if d["Disease"] == disease),
                                         "Không có thông tin"),
                        "Prevention": next((d["Prevention"] for d in disease_data if d["Disease"] == disease),
                                           "Không có thông tin"),
                        "Treatment": next((d["Treatment"] for d in disease_data if d["Disease"] == disease),
                                          "Không có thông tin"),
                    })

        # Kết hợp kết quả từ hàm và mô hình
        combined_results = search_results + ml_results

        if not combined_results:
            return render_template("index.html", error="Không tìm thấy bệnh nào phù hợp với triệu chứng của bạn.")

        return render_template("index.html", results=combined_results)

    except Exception as e:
        print(f"Lỗi trong quá trình dự đoán: {e}")
        return render_template("index.html", error="Đã xảy ra lỗi. Vui lòng thử lại.")

if __name__ == "__main__":
    app.run(debug=True)
