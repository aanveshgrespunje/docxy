"""
Summarize PDF feature: extracts text and produces a summary,
returned as a nicely formatted PDF (not a plain .txt) so the
frontend can display it inline on the same page.

Uses Gemini if a GEMINI_API_KEY is set AND the google-genai
package is installed. Otherwise it runs a real local
(frequency-based extractive) summarizer -- no external API or
key needed.
Route: POST /api/summarize
"""
import os
import io
import re
import string
from collections import Counter
from flask import Blueprint, request, send_file, jsonify

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from google import genai
except ImportError:
    genai = None

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit

from modules.config import UPLOAD_FOLDER

summarize_pdf_bp = Blueprint('summarize_pdf', __name__)

_STOPWORDS = set("""
a an the and or but if while is are was were be been being of to in on for
with as by at from this that these those it its it's they them their he she
his her him we us our you your i me my not no do does did doing have has had
having can could will would shall should may might must than then so such
there here when where why how what which who whom into over under again
further once about above below out up down off very s t can will just don
should now
""".split())


def _summarize_text(text, max_sentences=8):
    """Simple, dependency-free extractive summarizer.
    Scores each sentence by the frequency of its (non-stopword) words
    and keeps the top N sentences, in their original order."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]

    if len(sentences) <= max_sentences:
        return sentences

    word_freq = Counter()
    for sentence in sentences:
        words = re.findall(r"[a-zA-Z']+", sentence.lower())
        for w in words:
            w = w.strip(string.punctuation)
            if w and w not in _STOPWORDS and len(w) > 1:
                word_freq[w] += 1

    if not word_freq:
        return sentences[:max_sentences]

    max_freq = max(word_freq.values())
    for w in word_freq:
        word_freq[w] /= max_freq

    sentence_scores = {}
    for idx, sentence in enumerate(sentences):
        words = re.findall(r"[a-zA-Z']+", sentence.lower())
        if not words:
            continue
        score = sum(word_freq.get(w.strip(string.punctuation), 0) for w in words)
        score = score / len(words)
        sentence_scores[idx] = score

    top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    top_indices.sort()

    return [sentences[i] for i in top_indices]


def _to_bullet_list(text_or_lines):
    """Normalize either a list of sentences or a raw text blob (e.g. from
    Gemini) into a clean list of bullet-point strings."""
    if isinstance(text_or_lines, list):
        lines = [l.strip() for l in text_or_lines if l.strip()]
    else:
        raw = text_or_lines.strip()
        if '\n' in raw:
            lines = [l.strip() for l in raw.split('\n') if l.strip()]
        else:
            lines = re.split(r'(?<=[.!?])\s+', raw)
            lines = [l.strip() for l in lines if l.strip()]
    return lines


def _build_summary_pdf(title, bullet_lines):
    """Render the bullet-point summary into a properly wrapped,
    readable PDF (instead of a raw dumped text file)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    page_width, page_height = letter
    margin_x = 50
    max_width = page_width - (2 * margin_x)
    y = page_height - 60

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin_x, y, title)
    y -= 35

    body_font = "Helvetica"
    body_size = 11
    line_height = 16
    bullet_gap = 10

    c.setFont(body_font, body_size)

    for line in bullet_lines:
        bullet_text = f"\u2022  {line}"
        wrapped = simpleSplit(bullet_text, body_font, body_size, max_width)

        # Page-break check: make sure the whole bullet fits, else start a new page
        needed_height = len(wrapped) * line_height + bullet_gap
        if y - needed_height < 50:
            c.showPage()
            c.setFont(body_font, body_size)
            y = page_height - 60

        for wrapped_line in wrapped:
            c.drawString(margin_x, y, wrapped_line)
            y -= line_height

        y -= bullet_gap

    c.save()
    buffer.seek(0)
    return buffer


@summarize_pdf_bp.route('/api/summarize', methods=['POST'])
def summarize_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(input_path)
        reader = PdfReader(input_path)
        full_text = [p.extract_text() for p in reader.pages if p.extract_text()]
        extracted_text = "\n".join(full_text)

        if not extracted_text.strip():
            return jsonify({"error": "No readable text found inside the PDF."}), 400

        gemini_key = os.environ.get("GEMINI_API_KEY")
        summary_source = None

        if genai is not None and gemini_key:
            try:
                client = genai.Client(api_key=gemini_key)
                prompt = f"Provide a clean structured summary of this document:\n\n{extracted_text[:30000]}"
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                summary_source = response.text
            except Exception:
                summary_source = None

        if not summary_source:
            summary_source = _summarize_text(extracted_text, max_sentences=10)

        bullet_lines = _to_bullet_list(summary_source)
        pdf_buffer = _build_summary_pdf("Document Summary", bullet_lines)

        return send_file(pdf_buffer, as_attachment=False, download_name="summary.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
