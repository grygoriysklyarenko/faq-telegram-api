from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fuzzywuzzy import fuzz
import json
import os

app = Flask(__name__)

# Настройка доступа к Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
google_creds = json.loads(os.environ['GOOGLE_CREDS'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(creds)

# Открываем таблицу по URL или ID
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1CucLDyFCUhOwov-oZ-4udVHmJJF4XheLb-OEaumMKnQ/edit#gid=1737292423'
worksheet = client.open_by_url(SHEET_URL).sheet1

@app.route('/faq', methods=['POST'])
def faq():
    data = request.get_json()
    user_question = data.get('question', '')

    rows = worksheet.get_all_records()
    max_ratio = 0
    best_answer = None

    for row in rows:
        ratio = fuzz.token_set_ratio(user_question.lower(), row['question'].lower())
        if ratio > max_ratio:
            max_ratio = ratio
            best_answer = row

    if best_answer and max_ratio > 50:
        return jsonify({
            'answer': best_answer['answer'],
            'image_link': best_answer['image_link'],
            'similarity': max_ratio
        })
    else:
        return jsonify({'answer': 'Извините, не смог найти ответ.', 'similarity': max_ratio})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
