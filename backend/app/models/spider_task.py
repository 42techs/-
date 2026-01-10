from app import db
from datetime import datetime

class SpiderTask(db.Model):
    __tablename__ = "spider_tasks"

    id = db.Column(db.String(64), primary_key=True)  # task_id
    status = db.Column(db.String(20), nullable=False, default="PENDING")  # PENDING/RUNNING/SUCCESS/FAILED
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    result_json = db.Column(db.Text)   # 成功结果
    error = db.Column(db.Text)         # 失败原因
