from flask import Blueprint, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required
from sqlalchemy import extract, func
from app.models import User, Lesson, LessonProgress
from app.models.user_info import UserInfo
from datetime import datetime, timedelta
from sqlalchemy import extract, func
from app.models import LessonProgress
from sqlalchemy import extract, func
from app.models import UserInfo, LessonProgress, Lesson
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/lesson-completion', methods=['GET'])
@jwt_required()
def count_users_completed_all_lessons():
    # Tổng số lesson trong hệ thống
    total_lessons = db.session.query(func.count(Lesson.id)).scalar()

    # Subquery: lấy user_id có số bài học hoàn thành bằng total lesson
    full_completed_subquery = (
        db.session.query(
            LessonProgress.user_id
        )
        .filter(LessonProgress.completed == True)
        .group_by(LessonProgress.user_id)
        .having(func.count(LessonProgress.lesson_id) == total_lessons)
        .subquery()
    )

    # Đếm số người dùng hoàn thành toàn bộ
    completed_all = db.session.query(func.count()).select_from(full_completed_subquery).scalar()

    # Tổng số user
    total_users = db.session.query(func.count(User.id)).scalar()

    # Số user chưa hoàn thành toàn bộ
    not_completed_all = total_users - completed_all

    return jsonify({
        "completedAll": completed_all,
        "notCompletedAll": not_completed_all,
        "totalUsers": total_users
    })

@analytics_bp.route('/user/monthly-stats', methods=['GET'])
@jwt_required()
def get_monthly_user_stats():
    monthly_stats = (
        db.session.query(
            extract('month', UserInfo.start_date).label('month'),
            func.sum(func.if_(UserInfo.vip == True, 1, 0)).label('vip'),
            func.sum(func.if_(UserInfo.vip == False, 1, 0)).label('newUsers')
        )
        .filter(UserInfo.is_delete == False)
        .group_by(extract('month', UserInfo.start_date))
        .order_by(extract('month', UserInfo.start_date))
        .all()
    )

    result = []
    for row in monthly_stats:
        result.append({
            "month": f"Tháng {int(row.month)}",
            "newUsers": int(row.newUsers),
            "vip": int(row.vip)
        })

    return jsonify(result), 200


@analytics_bp.route('/analytics/heatmap-submission', methods=['GET'])
@jwt_required()
def get_heatmap_submission_data():
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    results = (
        db.session.query(
            func.dayofweek(LessonProgress.submit_time).label('weekday'),
            func.extract('hour', LessonProgress.submit_time).label('hour'),
            func.count().label('count')
        )
        .filter(LessonProgress.submit_time >= seven_days_ago)
        .group_by('weekday', 'hour')
        .all()
    )

    # MySQL: 1 = Sunday → convert về 0 = Monday, 6 = Sunday cho chart
    def convert_day(day):
        # 1 (Sun) -> 6, 2 (Mon) -> 0, ..., 7 (Sat) -> 5
        return (day + 5) % 7

    data = [
        { 'x': convert_day(row.weekday), 'y': int(row.hour), 'v': int(row.count) }
        for row in results
    ]

    return jsonify(data), 200


@analytics_bp.route('/analytics/registration-completion', methods=['GET'])
@jwt_required()
def get_monthly_user_data():
    from sqlalchemy.sql import extract, func

    # 1. Tổng số bài học trong hệ thống
    total_lessons = db.session.query(func.count(Lesson.id)).scalar()

    # 2. Người dùng mới đăng ký theo tháng
    new_users = (
        db.session.query(
            extract('month', UserInfo.start_date).label('month'),
            func.count(UserInfo.id).label('newUsers')
        )
        .filter(UserInfo.is_delete == False)
        .group_by(extract('month', UserInfo.start_date))
        .order_by(extract('month', UserInfo.start_date))
        .all()
    )

    # 3. Người dùng hoàn thành toàn bộ bài học: lấy user_id và thời điểm submit cuối cùng
    subquery = (
        db.session.query(
            LessonProgress.user_id,
            func.max(LessonProgress.submit_time).label('completed_date')
        )
        .filter(LessonProgress.completed == True)
        .group_by(LessonProgress.user_id)
        .having(func.count(LessonProgress.lesson_id) == total_lessons)
        .subquery()
    )

    # 4. Nhóm số người hoàn thành theo tháng hoàn thành (submit_time)
    completed_by_month = (
        db.session.query(
            extract('month', subquery.c.completed_date).label('month'),
            func.count(subquery.c.user_id).label('completedUsers')
        )
        .group_by(extract('month', subquery.c.completed_date))
        .order_by(extract('month', subquery.c.completed_date))
        .all()
    )

    # 5. Tổng hợp dữ liệu
    new_users_dict = {int(row.month): row.newUsers for row in new_users}
    completed_users_dict = {int(row.month): row.completedUsers for row in completed_by_month}

    result = []
    for month in range(1, 13):
        result.append({
            "month": f"Tháng {month}",
            "lineA": new_users_dict.get(month, 0),       # Số người đăng ký mới
            "lineB": completed_users_dict.get(month, 0)  # Số người hoàn thành (theo submit_time)
        })

    return jsonify(result), 200

