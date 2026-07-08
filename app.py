"""
Main Flask entry point.
Every feature (merge, split, organize, summarize, image/pdf
conversions, word/pptx/xlsx/html conversions...) lives in its
own folder under modules/. This file only creates the app and
registers each feature's Blueprint.
"""
from flask import Flask, render_template

from modules.merge_pdf.routes import merge_pdf_bp
from modules.split_pdf.routes import split_pdf_bp
from modules.organize_pdf.routes import organize_pdf_bp
from modules.summarize_pdf.routes import summarize_pdf_bp
from modules.pdf_to_images.routes import pdf_to_images_bp
from modules.jpg_to_pdf.routes import jpg_to_pdf_bp
from modules.docx_to_pdf.routes import docx_to_pdf_bp
from modules.pptx_to_pdf.routes import pptx_to_pdf_bp
from modules.xlsx_to_pdf.routes import xlsx_to_pdf_bp
from modules.html_to_pdf.routes import html_to_pdf_bp
from modules.pdf_to_docx.routes import pdf_to_docx_bp
from modules.pdf_to_pptx.routes import pdf_to_pptx_bp
from modules.pdf_to_xlsx.routes import pdf_to_xlsx_bp

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# Register every feature module's blueprint.
app.register_blueprint(merge_pdf_bp)
app.register_blueprint(split_pdf_bp)
app.register_blueprint(organize_pdf_bp)
app.register_blueprint(summarize_pdf_bp)
app.register_blueprint(pdf_to_images_bp)
app.register_blueprint(jpg_to_pdf_bp)
app.register_blueprint(docx_to_pdf_bp)
app.register_blueprint(pptx_to_pdf_bp)
app.register_blueprint(xlsx_to_pdf_bp)
app.register_blueprint(html_to_pdf_bp)
app.register_blueprint(pdf_to_docx_bp)
app.register_blueprint(pdf_to_pptx_bp)
app.register_blueprint(pdf_to_xlsx_bp)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
