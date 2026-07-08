"""
Organize PDF feature: reorders and/or rotates pages of an uploaded PDF.
Route: POST /api/organize
"""
import os
from flask import Blueprint, request, send_file, jsonify

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    PdfReader = None
    PdfWriter = None

from modules.config import UPLOAD_FOLDER

organize_pdf_bp = Blueprint('organize_pdf', __name__)


@organize_pdf_bp.route('/api/organize', methods=['POST'])
def organize_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    page_order_str = request.form.get('page_order', '').strip()
    try:
        rotate_angle = int(request.form.get('rotate', 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Rotation must be an integer"}), 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(input_path)
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        if page_order_str:
            try:
                page_indices = [int(x.strip()) for x in page_order_str.split(',') if x.strip() != '']
            except ValueError:
                return jsonify({"error": "Page order must be comma-separated integers"}), 400
        else:
            page_indices = list(range(total_pages))

        writer = PdfWriter()
        for idx in page_indices:
            if 0 <= idx < total_pages:
                page = reader.pages[idx]
                if rotate_angle != 0:
                    page.rotate(rotate_angle)
                writer.add_page(page)
            else:
                return jsonify({"error": f"Index out of bounds: {idx}"}), 400

        output_path = os.path.join(UPLOAD_FOLDER, "organized_output.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)
        return send_file(output_path, as_attachment=True, download_name="organized.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
