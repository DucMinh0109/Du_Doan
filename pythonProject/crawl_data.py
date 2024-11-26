import requests
from bs4 import BeautifulSoup
import pandas as pd

# Từ điển ánh xạ tên bệnh (nếu cần dịch từ tiếng Việt sang tiếng Anh)
disease_mapping = {
    "COVID-19": "COVID-19",
    "Bệnh tiểu đường": "Diabetes_mellitus",
    "Cúm": "Influenza",
    "Viêm phổi": "Pneumonia",
    "Viêm khớp dạng thấp": "Rheumatoid_arthritis",
    "Bệnh tim mạch": "Heart_disease",
    "Huyết áp cao": "Hypertension",
    "Hen suyễn": "Asthma",
    "Lao phổi": "Tuberculosis",
    "Viêm gan B": "Hepatitis_B",
    "Trầm cảm": "Depression",
    "Rối loạn lo âu": "Anxiety_disorder",
    "Béo phì": "Obesity",
    "Đột quỵ": "Stroke",
    "Bệnh Alzheimer": "Alzheimer_disease"
}

# Từ khóa mở rộng
keywords = {
    "Nguyên nhân": ["nguyên nhân", "cause", "etiology", "origin", "reason"],
    "Triệu chứng": ["triệu chứng", "symptom", "clinical features", "manifestation", "signs"],
    "Điều trị": ["điều trị", "treatment", "therapy", "management", "care"],
    "Phòng ngừa": ["phòng ngừa", "prevention", "protection", "avoidance"],
}

# Hàm tìm kiếm thông tin
def search_content(content, keywords):
    for paragraph in content.find_all(["p", "li"]):  # Mở rộng tìm trong cả danh sách
        text = paragraph.text.lower()
        if any(keyword in text for keyword in keywords):
            return paragraph.text.strip()
    return "Không tìm thấy"

# Crawl dữ liệu từ Wikipedia
def fetch_wikipedia_data(disease_name, language="en"):
    base_url = f"https://{language}.wikipedia.org/wiki/{disease_name.replace(' ', '_')}"
    response = requests.get(base_url)

    if response.status_code != 200:
        print(f"Không thể truy cập {base_url}")
        return {"Tên bệnh": disease_name, "Nguyên nhân": "Không tìm thấy", "Triệu chứng": "Không tìm thấy", "Điều trị": "Không tìm thấy", "Phòng ngừa": "Không tìm thấy"}

    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find("div", {"class": "mw-parser-output"})

    if not content:
        print(f"Không tìm thấy nội dung trên trang {base_url}")
        return {"Tên bệnh": disease_name, "Nguyên nhân": "Không tìm thấy", "Triệu chứng": "Không tìm thấy", "Điều trị": "Không tìm thấy", "Phòng ngừa": "Không tìm thấy"}

    disease_data = {"Tên bệnh": disease_name}

    for field, kw_list in keywords.items():
        disease_data[field] = search_content(content, kw_list)

    return disease_data

# Crawl dữ liệu từ nhiều nguồn
def crawl_disease_data(diseases):
    data = []

    for disease in diseases:
        disease_name = disease_mapping.get(disease, disease)
        print(f"Đang crawl dữ liệu cho {disease} ({disease_name}) từ Wikipedia...")

        wiki_data = fetch_wikipedia_data(disease_name)

        if all(value == "Không tìm thấy" for key, value in wiki_data.items() if key != "Tên bệnh"):
            print(f"Thử tìm kiếm {disease} bằng tiếng Việt...")
            wiki_data = fetch_wikipedia_data(disease, language="vi")

        data.append(wiki_data)

    return data

# Danh sách bệnh mở rộng
disease_list = [
    "COVID-19", "Bệnh tiểu đường", "Cúm", "Viêm phổi", "Viêm khớp dạng thấp",
    "Bệnh tim mạch", "Huyết áp cao", "Hen suyễn", "Lao phổi", "Viêm gan B",
    "Trầm cảm", "Rối loạn lo âu", "Béo phì", "Đột quỵ", "Bệnh Alzheimer"
]

# Crawl dữ liệu
disease_data = crawl_disease_data(disease_list)

# Lưu dữ liệu vào file CSV
df = pd.DataFrame(disease_data)
df.to_csv("disease_data_crawled.csv", index=False, encoding="utf-8")
print("Dữ liệu đã được lưu vào 'disease_data_crawled.csv'")
