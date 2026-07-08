"""
JPG / Image -> PDF feature: combines uploaded images into a single PDF.
Route: POST /api/jpg-to-pdf
(this same route handles any image type, so it covers "image to pdf" too)
"""
import io
from flask import Blueprint, request, send_file, jsonify
from PIL import Image

jpg_to_pdf_bp = Blueprint('jpg_to_pdf', __name__)


@jpg_to_pdf_bp.route('/api/jpg-to-pdf', methods=['POST'])
def jpg_to_pdf():
    if 'files' not in request.files:
        return jsonify({"error": "No images uploaded"}), 400
    files = request.files.getlist('files')
    try:
        image_list = []
        for file in files:
            if file.filename != '':
                img = Image.open(file.stream).convert('RGB')
                image_list.append(img)

        if not image_list:
            return jsonify({"error": "No valid images processed"}), 400

        pdf_buffer = io.BytesIO()
        image_list[0].save(pdf_buffer, format='PDF', save_all=True, append_images=image_list[1:])
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name="converted_images.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
