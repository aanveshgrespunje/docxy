"""
Word (docx) -> PDF feature.
Route: POST /api/docx-to-pdf
"""
import io
from flask import Blueprint, request, send_file, jsonify
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

docx_to_pdf_bp = Blueprint('docx_to_pdf', __name__)


@docx_to_pdf_bp.route('/api/docx-to-pdf', methods=['POST'])
def docx_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Missing file payload"}), 400
    file = request.files['file']
    try:
        doc = Document(file.stream)
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        y_position = 750

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y_position, "Docxy Compiled PDF View")
        y_position -= 40
        c.setFont("Helvetica", 11)

        for p in doc.paragraphs:
            if p.text.strip():
                c.drawString(50, y_position, p.text[:90])
                y_position -= 20
                if y_position < 50:
                    c.showPage()
                    y_position = 750
                    c.setFont("Helvetica", 11)

        c.save()
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name="word_converted.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
