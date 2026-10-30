
import os
import json
from dotenv import load_dotenv, find_dotenv
from google import genai
from flask import Flask, render_template, request,session

print("ENV PATH:", find_dotenv(), flush=True)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
print("API KEY LOADED:", bool(os.getenv("GEMINI_API_KEY")), flush=True)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
app.secret_key = os.urandom(32)

# 新增 AI 出題函式10-23
def generate_question(topic):
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=(
            f"請根據「{topic}」產生一道 Python 初學者的四選一選擇題。"
            "只能有一個正確答案。"
            "請回傳 JSON 格式，包含 question、A、B、C、D、answer、explanation 七個欄位。"
            "answer 只能填入 A、B、C 或 D。"
            "explanation 請用繁體中文解釋正確答案，50字以內。"
        ),
        config={"response_mime_type": "application/json"}
    )

    return json.loads(response.text)


# -----------------------------------------------------------
@app.route("/",methods=["POST","GET"])
def home():
    topic = ""
    feedback=""
    student_answer=""
    question_text = "請先選擇學習主題"
    action = ""
    if request.method == "POST":
        topic = request.form.get("topic","")
        action = request.form.get("action", "")
        print("我選擇的主題:",topic)
        # 我選擇的按鈕(幫我出題或檢查答案)
    if action == "generate":
        if topic == "":
            question_text = "請先選擇學習主題"
        else:
            try:
                question_data = generate_question(topic)
                session["question_data"] = question_data
                session["topic"] = topic
                question_text = question_data["question"]
            except Exception as e:
                print("AI 出題失敗：", e)
                feedback = "AI 目前無法出題，請稍後再試。"

        # 10-23 新增檢查答案功能
    if action == "check":
        question_data = session.get("question_data", {})
        student_answer = request.form.get("student_answer", "")

        if not question_data:
            feedback = "目前尚未產生題目，請先點擊幫我出題。"
        else:
            question_text = question_data["question"]

            if student_answer == "":
                feedback = "請先選擇答案。"
            elif student_answer == question_data["answer"]:
                feedback = "答對了！" + question_data["explanation"]
            else:
                feedback = (
                    "答錯了！正確答案是 "
                    + question_data["answer"]
                    + "。" + question_data["explanation"]
                )

    return render_template("index.html",
                           topic=topic,
                           question_text=question_text,
                           feedback=feedback,
                           question_data=session.get("question_data", {})
                           )

if __name__ == "__main__":
    app.run(debug=True, port=5001)
