from flask import Flask, request, Response
import requests
from urllib.parse import urljoin, urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# عطلت static_folder علشان ميبقاش فيه تعارض مع /static/
app = Flask(__name__, static_folder=None)

TARGET = "https://past-pinniped-uuuuuu7gco-5c3491b7.koyeb.app/"

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy(path):
    if path:
        url = f"{TARGET}{path}"
    else:
        url = TARGET.rstrip('/')
    
    headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'content-length']}
    if request.query_string:
        url += f"?{request.query_string.decode()}"
    
    body = request.get_data() if request.method not in ["GET", "HEAD"] else None
    
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=body,
            cookies=request.cookies,
            allow_redirects=False,
            stream=True,
            timeout=60
        )

        excluded_headers = ['transfer-encoding', 'connection', 'content-encoding']
        response_headers = []
        
        for name, value in resp.headers.items():
            if name.lower() not in excluded_headers:
                if name.lower() == "location":
                    parsed = urlparse(value)
                    if parsed.netloc and TARGET in value:
                        new_location = urljoin(request.host_url, parsed.path.lstrip("/"))
                        if parsed.query:
                            new_location += f"?{parsed.query}"
                        response_headers.append((name, new_location))
                    else:
                        response_headers.append((name, value))
                else:
                    response_headers.append((name, value))

        content_type = resp.headers.get('content-type', '').lower()
        
        # stream للملفات الكبيرة أو media
        if (any(media_type in content_type for media_type in ['audio/', 'video/', 'image/', 'application/octet-stream']) or 
            path.endswith(('.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mov', '.jpg', '.png', '.gif', '.pdf'))):
            
            range_header = request.headers.get('Range')
            if range_header:
                response_headers.append(('Accept-Ranges', 'bytes'))
                if 'Content-Range' in resp.headers:
                    response_headers.append(('Content-Range', resp.headers['Content-Range']))
            
            def generate():
                try:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                except:
                    pass
            
            response = Response(generate(), resp.status_code, response_headers)
            if not range_header:
                response.headers['Accept-Ranges'] = 'bytes'
            return response
        else:
            return Response(resp.content, resp.status_code, response_headers)
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {str(e)}")
        return Response(f"Proxy Error: {str(e)}", 502)
    except Exception as e:
        print(f"General error for {url}: {str(e)}")
        return Response(f"Server Error: {str(e)}", 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
