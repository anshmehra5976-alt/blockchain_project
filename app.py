from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from blockchain import Blockchain
import hashlib
import qrcode
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)
blockchain = Blockchain()

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def hash_document(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    file_bytes = file.read()
    doc_hash = hash_document(file_bytes)
    existing = blockchain.find_document(doc_hash)
    if existing:
        return jsonify({
            "status": "already_exists",
            "message": "Document already registered in blockchain!",
            "block_index": existing.index,
            "document_hash": doc_hash
        })
    block_data = {
        "type": "document",
        "filename": file.filename,
        "document_hash": doc_hash,
        "uploaded_by": "Ansh | CGC Landran"
    }
    new_block = blockchain.add_block(block_data)
    qr_data = f"Block:{new_block.index}|Hash:{doc_hash}|Time:{new_block.timestamp}|By:Ansh-CGC"
    qr_code = generate_qr(qr_data)
    return jsonify({
        "status": "success",
        "message": "Document registered on blockchain!",
        "block_index": new_block.index,
        "document_hash": doc_hash,
        "block_hash": new_block.hash,
        "timestamp": new_block.timestamp,
        "qr_code": qr_code
    })

@app.route("/verify", methods=["POST"])
def verify():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    file_bytes = file.read()
    doc_hash = hash_document(file_bytes)
    block = blockchain.find_document(doc_hash)
    chain_valid = blockchain.is_chain_valid()
    if block:
        qr_data = f"VERIFIED|Block:{block.index}|Hash:{doc_hash}|Time:{block.timestamp}|By:Ansh-CGC"
        qr_code = generate_qr(qr_data)
        return jsonify({
            "status": "verified",
            "message": "Document is AUTHENTIC and found on blockchain!",
            "block_index": block.index,
            "document_hash": doc_hash,
            "block_hash": block.hash,
            "timestamp": block.timestamp,
            "chain_integrity": chain_valid,
            "qr_code": qr_code
        })
    return jsonify({
        "status": "not_found",
        "message": "Document NOT found on blockchain. May be tampered or unregistered.",
        "document_hash": doc_hash,
        "chain_integrity": chain_valid
    })

@app.route("/chain", methods=["GET"])
def get_chain():
    return jsonify({
        "chain": blockchain.get_chain_data(),
        "length": len(blockchain.chain),
        "is_valid": blockchain.is_chain_valid()
    })

if __name__ == "__main__":
    app.run(debug=True)