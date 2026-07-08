"""
PDF -> Excel (xlsx) feature.
Route: POST /api/pdf-to-xlsx
"""
import io
from flask import Blueprint, request, send_file, jsonify
import pdfplumber
from openpyxl import Workbook

pdf_to_xlsx_bp = Blueprint('pdf_to_xlsx', __name__)


@pdf_to_xlsx_bp.route('/api/pdf-to-xlsx', methods=['POST'])
def pdf_to_xlsx():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    try:
        pdf_bytes = file.read()
        wb = Workbook()
        ws = wb.active
        ws.title = "Extracted Text Grid"

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        ws.append([line])

        xlsx_buffer = io.BytesIO()
        wb.save(xlsx_buffer)
        xlsx_buffer.seek(0)
        return send_file(xlsx_buffer, as_attachment=True, download_name="reverse_parsed_grid.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
