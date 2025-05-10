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

    # 3) Vẽ PDF vào bộ nhớ
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w/2, h-100, "Certificate of Completion")

    c.setFont("Helvetica", 16)
    c.drawCentredString(w/2, h-160, f"This certifies that {user.username}")

    c.setFont("Helvetica", 14)
    c.drawCentredString(w/2, h-200, f"has completed the mini-course “{topic.name}”")

    date_str = cert.issued_at.strftime("%Y-%m-%d")
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(w/2, h-260, f"Issued at: {date_str} | Certificate ID: {cert.id}")

    c.showPage()
    c.save()

    # 4) Ghi file ra đĩa
    filename = f"cert_{user_id}_{topic_id}_{cert.id}.pdf"
    folder   = current_app.config['CERT_FOLDER']
    os.makedirs(folder, exist_ok=True)             # tạo folder nếu chưa có
    path     = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(buffer.getvalue())

    # 5) Cập nhật lại pdf_path và commit
    cert.pdf_path = filename
    db.session.commit()
    return cert
