import os, io
from datetime import datetime
from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from app.models.exercise import Exercise
from app.models.exercise_submission import ExerciseSubmission
from app.models.lesson import Lesson
from app.models.lesson_progress import LessonProgress
from ..extensions import db
from app.models.certificate import Certificate
from app.models.user import User
from app.models.topic_lesson import TopicLesson

from reportlab.lib.colors import HexColor, lightgrey


def check_topic_complete(user_id: int, topic_id: int) -> bool:
    """
    Trả về True nếu user đã hoàn thành mọi lesson và exercise trong topic.
    """
    # 1) Kiểm tra tất cả các lesson thuộc topic_lesson_id
    lessons = Lesson.query.filter_by(topic_lesson_id=topic_id).all()
    for l in lessons:
        prog = LessonProgress.query.filter_by(
            user_id=user_id,
            lesson_id=l.id,
            completed=True
        ).first()
        if not prog:
            return False

    # 2) Kiểm tra tất cả các exercise thuộc các lesson đó
    exercises = (
        Exercise.query
        .join(Lesson, Exercise.lesson_id == Lesson.id)
        .filter(Lesson.topic_lesson_id == topic_id)
        .all()
    )
    for ex in exercises:
        sub = ExerciseSubmission.query.filter_by(
            user_id=user_id,
            exercise_id=ex.id,
            is_correct=True
        ).first()
        if not sub:
            return False

    return True

def issue_certificate(user_id: int, topic_id: int) -> Certificate:
    # 1) Lấy user và topic
    user  = User.query.get(user_id)
    topic = TopicLesson.query.get(topic_id)
    if not user or not topic:
        raise ValueError("Invalid user or topic")

    # 2) Tạo record (chưa có pdf_path)
    cert = Certificate(
        user_id   = user_id,
        topic_id  = topic_id,
        issued_at = datetime.utcnow(),
        pdf_path  = ''
    )
    db.session.add(cert)
    db.session.flush()  # để cert.id được gán

     # 3) Vẽ PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # -- nền nhạt --
    c.setFillColor(lightgrey)
    c.rect(30, 30, w-60, h-60, fill=1, stroke=0)
    c.setFillColor(HexColor('#000000'))

    # -- logo (nếu có) --
    logo_path = os.path.join(current_app.root_path, 'static', 'logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 50, h-100, width=100, preserveAspectRatio=True, mask='auto')

    # -- khung viền --
    c.setLineWidth(4)
    c.setStrokeColor(HexColor('#004080'))
    c.rect(20, 20, w-40, h-40, fill=0)

    # -- tiêu đề --
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(HexColor('#004080'))
    c.drawCentredString(w/2, h-120, "Certificate of Completion")

    # -- dòng phụ đề --
    c.setFont("Helvetica-Oblique", 14)
    c.setFillColor(HexColor('#333333'))
    c.drawCentredString(w/2, h-160, "This certifies that")

    # -- tên người nhận --
    c.setFont("Times-BoldItalic", 22)
    c.setFillColor(HexColor('#000000'))
    c.drawCentredString(w/2, h-200, f"{user.username}")

    # -- nội dung chính --
    c.setFont("Helvetica", 16)
    c.drawCentredString(w/2, h-240, f"has successfully completed the mini-course")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w/2, h-270, f"“{topic.name}”")

    # -- ngày và ID --
    date_str = cert.issued_at.strftime("%Y-%m-%d")
    c.setFont("Helvetica", 12)
    c.drawCentredString(w/2, h-320, f"Issued at: {date_str}    |    Certificate ID: {cert.id}")

    # -- chữ ký hoặc seal --
    sig_path = os.path.join(current_app.root_path, 'static', 'signature.png')
    if os.path.exists(sig_path):
        c.drawImage(sig_path, w-200, 60, width=120, preserveAspectRatio=True, mask='auto')
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(w-200, 50, "Instructor Signature")

    c.showPage()
    c.save()

    # 4) Ghi file
    filename = f"cert_{user_id}_{topic_id}_{cert.id}.pdf"
    folder   = current_app.config['CERT_FOLDER']
    os.makedirs(folder, exist_ok=True)
    path     = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(buffer.getvalue())

    # c.setFont("Helvetica-Bold", 60)
    # c.setFillColor(HexColor('#CCCCCC'))
    # c.saveState()
    # c.translate(w/2, h/2)
    # c.rotate(45)
    # c.drawCentredString(0, 0, "DRAFT")
    # c.restoreState()

    # 5) Cập nhật pdf_path và commit
    cert.pdf_path = filename
    db.session.commit()
    return cert
