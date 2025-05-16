from app import create_app, db

from app import models

app = create_app()

with app.app_context():
    db.create_all()  # tạo tất cả bảng nếu chưa có

if __name__ == "__main__":
    app.run(debug=True)
