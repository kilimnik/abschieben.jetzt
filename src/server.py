from http.server import BaseHTTPRequestHandler, HTTPServer
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

hostName = "0.0.0.0"
serverPort = 8080

width = 800
height = 400

class MyServer(BaseHTTPRequestHandler):
    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self.request.settimeout(60)

        abschieben = Image.open("src/abschiebung.png")
        self.abschieben = abschieben.resize((500,375), Image.Resampling.LANCZOS)

        self.font = ImageFont.truetype("src/XTypewriter-Regular.ttf", size=50)

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            header = self.headers.get("HOST")
            splits = header.split(".")

            who = ""
            if len(splits) == 2:
                who = "Alle"
            else:
                who = " ".join(splits[:-2])

            title = f"{who} abschieben jetzt"

            body = ""
            
            body += f"<html><head>\n"
            body += f'<meta property="og:title" content="{title}"/>\n'
            body += f'<meta property="og:description" content="{title}"/>\n'
            body += f'<meta property="og:site_name" content="{title}"/>\n'
            body += f'<meta property="og:image" content="/img/{who}.png"/>\n'
            body += f'<meta name="twitter:card" content="summary_large_image"/>\n'
            body += f"<title>{title}</title>\n"
            body += f"</head>\n\n"

            body += "<body>\n"
            body += f'<img src="img/{who}.png">\n'
            body += "</body></html>\n"

            self.wfile.write(bytes(body, "utf-8"))
        elif self.path.startswith("/img/"):
            img_name = self.path.replace("/img/", "")
            img_name = img_name.replace(".png", "")

            img = self._generate_image(img_name)
            buffered = BytesIO()
            img.save(buffered, format="PNG")

            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()

            self.wfile.write(buffered.getvalue())

        elif self.path == "/favicon.ico":
            self.send_response(404)
        else:
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()

    def _generate_image(self, who):
        img = Image.new(mode="RGBA", size=(width, height), color=(255, 255, 255, 255))

        draw = ImageDraw.Draw(img)
        draw.text((250, 250), who, fill=(0, 0, 0, 255), font=self.font)

        img.alpha_composite(self.abschieben, (0, 0))

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
