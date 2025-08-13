from flask import Flask, request, Response
import requests
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

# رابط الهدف
TARGET = "https://past-pinniped-uuuuuu7gco-5c3491b7.koyeb.app/"

# دالة للطباعة
def g(k):
    print(k)

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy(path):
    url = f"{TARGET}/{path}"
    g(f"Request URL: {url}")
    
    # نسخ رؤوس الطلب بدون Host
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    g(f"Request Headers: {headers}")
    
    # قراءة جسم الطلب إذا لم يكن GET أو HEAD
    body = request.get_data() if request.method not in ["GET", "HEAD"] else None
    if body:
        g(f"Request Body: {body}")
    
    # إرسال الطلب للـ TARGET
    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=body,
        cookies=request.cookies,
        allow_redirects=False
    )

    g(f"Response Status: {resp.status_code}")
    g(f"Response Headers: {dict(resp.headers)}")
    g(f"Response Body (first 500 bytes): {resp.content[:500]}
