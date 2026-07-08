"""
PDF -> images feature: rasterizes every page of a PDF into PNG
images and returns them zipped.
Routes: POST /api/pdf-to-images, POST /api/pdf-to-jpg (alias)
"""
import os
import io
import zipfile
from flask import Blueprint, request, send_file, jsonify

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from modules.config import UPLOAD_FOLDER

pdf_to_images_bp = Blueprint('pdf_to_images', __name__)


def _pdf_to_images():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(input_path)
        if fitz is None:
            return jsonify({"error": "PyMuPDF (fitz) library missing on server."}), 500

        document = fitz.open(input_path)
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for page_num in range(len(document)):
                page = document.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                zip_file.writestr(f"page_{page_num + 1}.png", pix.tobytes("png"))

        document.close()
        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name="rasterized_pages.zip", mimetype="application/zip")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)


@pdf_to_images_bp.route('/api/pdf-to-images', methods=['POST'])
def pdf_to_images():
    return _pdf_to_images()


@pdf_to_images_bp.route('/api/pdf-to-jpg', methods=['POST'])
def pdf_to_jpg_alternate():
    return _pdf_to_images()
