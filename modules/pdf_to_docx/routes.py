"""
PDF -> Word (docx) feature.
Route: POST /api/pdf-to-docx
"""
import io
from flask import Blueprint, request, send_file, jsonify
import pdfplumber
from docx import Document

pdf_to_docx_bp = Blueprint('pdf_to_docx', __name__)


@pdf_to_docx_bp.route('/api/pdf-to-docx', methods=['POST'])
def pdf_to_docx():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    try:
        pdf_bytes = file.read()
        doc = Document()
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        if line.strip():
                            doc.add_paragraph(line)

        doc_buffer = io.BytesIO()
        doc.save(doc_buffer)
        doc_buffer.seek(0)
        return send_file(doc_buffer, as_attachment=True, download_name="reverse_parsed.docx", mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
