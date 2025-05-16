from app import create_app, db

from app.models import Practice
import re
import unicodedata

def slugify(text):
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

app = create_app()  # 👈 tạo app từ factory

with app.app_context():
    practices = Practice.query.all()
    for p in practices:
        if not p.slug:
            p.slug = slugify(p.title)
            print(f"✔ {p.title} → {p.slug}")
    db.session.commit()
    print("✅ Hoàn tất cập nhật slug.")
