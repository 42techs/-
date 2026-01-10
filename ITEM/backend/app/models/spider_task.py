from app import db
from datetime import datetime

class SpiderTask(db.Model):
    __tablename__ = "spider_tasks"

    id = db.Column(db.String(64), primary_key=True)  # task_id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 关联用户
    status = db.Column(db.String(20), nullable=False, default="PENDING")  # PENDING/RUNNING/SUCCESS/FAILED
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    result_json = db.Column(db.Text)   # 成功结果
    error = db.Column(db.Text)         # 失败原因
    
    # 关系
    user = db.relationship('User', backref=db.backref('spider_tasks', lazy='dynamic'))
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'error': self.error
        }