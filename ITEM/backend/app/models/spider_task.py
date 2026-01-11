from app import db
from datetime import datetime

class SpiderTask(db.Model):
    __tablename__ = "spider_tasks"
    
    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="PENDING")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    result_json = db.Column(db.Text)
    error = db.Column(db.Text)

    params_json = db.Column(db.Text)  # 存储爬虫参数的JSON字符串
    
    user = db.relationship('User', backref=db.backref('spider_tasks', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'error': self.error,
            'params_json': self.params_json  # 新增
        }