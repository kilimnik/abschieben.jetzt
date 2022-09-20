from http.server import BaseHTTPRequestHandler, HTTPServer
from PIL import Image  
from PIL import ImageDraw 
import base64
from io import BytesIO
hostName = "0.0.0.0"
serverPort = 8080

width = 400
height = 400

class MyServer(BaseHTTPRequestHandler):
    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self.request.settimeout(60)

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            header = self.headers.get("HOST")
            splits = header.split(".")

            who = ""
            if len(splits) == 1:
                who = "Alle"
            else:
                who = " ".join(splits[:-1])

            title = f"{who} Abschieben Jetzt"

            img = self._generate_image(who)

            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            body = ""
            
            body += f"<html><head>\n"
            body += f'<meta property="og:title" content="{title}"/>\n'
            body += f'<meta property="og:image" content=data:image/png;base64,{img_str}"/>\n'
            body += f'<meta name="twitter:card" content="summary_large_image"/>\n'
            body += f"<title>{title}</title>\n"
            body += f"</head>\n\n"

            body += "<body>\n"
            body += f"<p>{title}</p>\n"
            body += f'<img src="data:image/png;base64,{img_str}">\n'
            body += "</body></html>\n"

            self.wfile.write(bytes(body, "utf-8"))
        elif self.path == "/favicon.ico":
            self.send_response(404)
        else:
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()

    def _generate_image(self, who):
        img = Image.new( mode="RGB", size=(width, height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.text((0, 0), who)

        return img

def main():
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


if __name__ == "__main__":        
    main()
