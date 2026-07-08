"""
Split PDF feature: extracts a single page from an uploaded PDF.
Route: POST /api/split
"""
import os
from flask import Blueprint, request, send_file, jsonify

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    PdfReader = None
    PdfWriter = None

from modules.config import UPLOAD_FOLDER

split_pdf_bp = Blueprint('split_pdf', __name__)


@split_pdf_bp.route('/api/split', methods=['POST'])
def split_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    page_target = request.form.get('page_number', 1)
    try:
        page_idx = int(page_target) - 1
    except ValueError:
        return jsonify({"error": "Page number must be an integer."}), 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(input_path)
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        if page_idx < 0 or page_idx >= total_pages:
            return jsonify({"error": f"Requested page {page_target} out of range (Total pages: {total_pages})."}), 400

        writer = PdfWriter()
        writer.add_page(reader.pages[page_idx])

        output_path = os.path.join(UPLOAD_FOLDER, "split_output.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)

        return send_file(output_path, as_attachment=True, download_name=f"split_page_{page_idx + 1}.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
