# ocr_service/server.py
# Microserviço OCR mínimo — P3 expande daqui

from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io, base64

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/ocr/imagem', methods=['POST'])
def ocr_imagem():
    """Recebe imagem base64, retorna texto extraído"""
    data = request.get_json()
    img_bytes = base64.b64decode(data['imagem'])
    img = Image.open(io.BytesIO(img_bytes))
    texto = pytesseract.image_to_string(img, lang='por')
    return jsonify({'texto': texto.strip()})

@app.route('/ocr/pdf', methods=['POST'])
def ocr_pdf():
    """Recebe PDF base64, retorna texto de todas as páginas"""
    data = request.get_json()
    pdf_bytes = base64.b64decode(data['pdf'])
    paginas = convert_from_bytes(pdf_bytes, dpi=200)
    texto_total = ''
    for pagina in paginas:
        texto_total += pytesseract.image_to_string(pagina, lang='por') + '\n'
    return jsonify({'texto': texto_total.strip()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)