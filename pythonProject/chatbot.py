from flask import Flask, request, jsonify

app = Flask(__name__)

# Câu trả lời mẫu cho chatbot
RESPONSES = {
    "hello": "Xin chào! Tôi có thể giúp gì cho bạn hôm nay?",
    "triệu chứng": "Hãy mô tả triệu chứng của bạn. Ví dụ: 'đau khớp', 'sốt', hoặc 'khó thở'.",
    "phòng ngừa": "Bạn có thể giảm nguy cơ mắc bệnh bằng cách duy trì lối sống lành mạnh, ăn uống điều độ, và tập thể dục thường xuyên.",
    "dự đoán": "Nếu bạn muốn dự đoán nguy cơ mắc bệnh, hãy nhập triệu chứng, độ tuổi và các thông tin khác vào form chính.",
    "default": "Xin lỗi, tôi không hiểu câu hỏi của bạn. Hãy thử diễn đạt lại!"
}

# Hàm xử lý tin nhắn từ người dùng
def get_chatbot_response(message):
    message = message.lower().strip()
    if "hello" in message or "xin chào" in message:
        return RESPONSES["hello"]
    elif "triệu chứng" in message:
        return RESPONSES["triệu chứng"]
    elif "phòng ngừa" in message:
        return RESPONSES["phòng ngừa"]
    elif "dự đoán" in message:
        return RESPONSES["dự đoán"]
    else:
        return RESPONSES["default"]

# API xử lý tin nhắn từ chatbot frontend
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "").strip()
        if not user_message:
            return jsonify({"response": "Vui lòng nhập tin nhắn."})
        bot_response = get_chatbot_response(user_message)
        return jsonify({"response": bot_response})
    except Exception as e:
        print(f"Error in chatbot: {e}")
        return jsonify({"response": "Có lỗi xảy ra. Vui lòng thử lại sau."})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
