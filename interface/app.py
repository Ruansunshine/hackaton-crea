# Interface web demo para o Motor RAGFlow
# Servida via Flask para fácil integração e comunicação HTTP
from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")

# URL do endpoint do motor RAGFlow (pode ser configurada via variável de ambiente)
RAGFLOW_URL = os.environ.get("RAGFLOW_URL", "http://rag-service:8001/analisar")
N8N_URL = os.environ.get("N8N_URL")  # opcional, se quiser enviar para o n8n

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analisar", methods=["POST"])
def analisar():
    data = request.json
    # Envia para o motor RAGFlow
    try:
        resp = requests.post(RAGFLOW_URL, json=data, timeout=20)
        resp.raise_for_status()
        resultado = resp.json()
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    # Opcional: encaminhar para o n8n
    if N8N_URL:
        try:
            requests.post(N8N_URL, json=resultado, timeout=10)
        except Exception:
            pass
    return jsonify(resultado)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
