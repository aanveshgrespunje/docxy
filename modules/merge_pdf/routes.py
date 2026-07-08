"""
Merge PDF feature: combines multiple uploaded PDF files into one.
Route: POST /api/merge
"""
import os
from flask import Blueprint, request, send_file, jsonify

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    PdfReader = None
    PdfWriter = None

from modules.config import UPLOAD_FOLDER

merge_pdf_bp = Blueprint('merge_pdf', __name__)


@merge_pdf_bp.route('/api/merge', methods=['POST'])
def merge_pdf():
    if 'files' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
    if PdfReader is None or PdfWriter is None:
        return jsonify({"error": "pypdf library unavailable on host environment."}), 500

    files = request.files.getlist('files')
    saved_paths = []
    writer = PdfWriter()

    try:
        for file in files:
            if file.filename == '':
                continue
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)
            saved_paths.append(path)

            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)

        output_path = os.path.join(UPLOAD_FOLDER, "merged_output.pdf")
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        return send_file(output_path, as_attachment=True, download_name="merged.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        for path in saved_paths:
            if os.path.exists(path):
                os.remove(path)
