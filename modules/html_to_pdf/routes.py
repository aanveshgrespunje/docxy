"""
HTML -> PDF feature.
Route: POST /api/html-to-pdf
"""
import io
from flask import Blueprint, request, send_file, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

html_to_pdf_bp = Blueprint('html_to_pdf', __name__)


@html_to_pdf_bp.route('/api/html-to-pdf', methods=['POST'])
def html_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No HTML file uploaded"}), 400
    file = request.files['file']
    try:
        raw_html = file.stream.read().decode('utf-8', errors='ignore')
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        c.setFont("Helvetica", 10)

        y_pos = 750
        c.drawString(50, 770, "Compiled HTML Markup Content Vector Layout:")
        for line in raw_html.split('\n')[:45]:
            if line.strip():
                c.drawString(50, y_pos, line.strip()[:95])
                y_pos -= 15

        c.save()
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name="markup_compiled.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
