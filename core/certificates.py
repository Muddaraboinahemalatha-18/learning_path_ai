from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.conf import settings
import os
from datetime import date

def generate_certificate_pdf(user, course, certificate_id):
    path = os.path.join(settings.MEDIA_ROOT, 'certificates')
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, f"{certificate_id}.pdf")

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # 🌈 Background
    c.setFillColor(colors.whitesmoke)
    c.rect(20, 20, width - 40, height - 40, fill=1)

    # 🔲 Border
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(4)
    c.rect(30, 30, width - 60, height - 60, fill=0)

    # 🏆 Title
    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, 750, "Certificate of Completion")

    # ─── Line under title
    c.setLineWidth(2)
    c.line(150, 735, width - 150, 735)

    # 📄 Content
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, 680, "This is to certify that")

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, 640, user.full_name)

    c.setFont("Helvetica", 14)
    c.drawCentredString(
        width / 2, 600,
        "has successfully completed the course"
    )

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, 560, course.course_name)

    # 📅 Date & Certificate ID
    c.setFont("Helvetica", 12)
    c.drawString(80, 480, f"Date: {date.today().strftime('%d %B %Y')}")
    c.drawRightString(width - 80, 480, f"Certificate ID: {certificate_id}")

    # ✍ Signatures
    c.line(100, 400, 250, 400)
    c.drawCentredString(175, 380, "Instructor")

    c.line(width - 250, 400, width - 100, 400)
    c.drawCentredString(width - 175, 380, "Authorized Signature")

    c.showPage()
    c.save()

    return file_path
