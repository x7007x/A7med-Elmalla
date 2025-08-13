from flask import Flask, request, Response
import requests

app = Flask(__name__)

TARGET = "https://ahmed.com"

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy(path):
    # المسار الكامل للموقع الهدف
    url = f"{TARGET}/{path}"

    # نسخ الهيدرز من الريكويست الأصلي
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}

    # إرسال الريكويست بنفس الميثود والبيانات
    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    # تجهيز الريسبونس بنفس الهيدرز
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    response_headers = [(name, value) for name, value in resp.headers.items() if name.lower() not in excluded_headers]

    # إعادة نفس الاستاتس كود والمحتوى
    return Response(resp.content, resp.status_code, response_headers)

# عشان Vercel يقدر يستدعيه
def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)
