from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Slide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    scanner_type = db.Column(db.String(100))
    stain_type = db.Column(db.String(100))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    levels = db.Column(db.Integer)
    mpp_x = db.Column(db.Float)  # microns per pixel X
    mpp_y = db.Column(db.Float)  # microns per pixel Y
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processing, ready, error
    
    # Relacionamentos
    annotations = db.relationship('Annotation', backref='slide', lazy=True, cascade='all, delete-orphan')
    ai_analyses = db.relationship('AIAnalysis', backref='slide', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Slide {self.filename}>'

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'scanner_type': self.scanner_type,
            'stain_type': self.stain_type,
            'width': self.width,
            'height': self.height,
            'levels': self.levels,
            'mpp_x': self.mpp_x,
            'mpp_y': self.mpp_y,
            'uploaded_by': self.uploaded_by,
            'status': self.status
        }

class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slide_id = db.Column(db.Integer, db.ForeignKey('slide.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    annotation_type = db.Column(db.String(50), nullable=False)  # point, rectangle, polygon, etc.
    label = db.Column(db.String(255))
    description = db.Column(db.Text)
    coordinates = db.Column(db.Text)  # JSON string for complex shapes
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Annotation {self.id} on Slide {self.slide_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'slide_id': self.slide_id,
            'user_id': self.user_id,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'annotation_type': self.annotation_type,
            'label': self.label,
            'description': self.description,
            'coordinates': self.coordinates,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }

class AIAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slide_id = db.Column(db.Integer, db.ForeignKey('slide.id'), nullable=False)
    analysis_type = db.Column(db.String(100), nullable=False)  # disease_detection, classification, etc.
    model_name = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float)
    result = db.Column(db.Text)  # JSON string with detailed results
    processing_time = db.Column(db.Float)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    
    def __repr__(self):
        return f'<AIAnalysis {self.id} for Slide {self.slide_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'slide_id': self.slide_id,
            'analysis_type': self.analysis_type,
            'model_name': self.model_name,
            'confidence': self.confidence,
            'result': self.result,
            'processing_time': self.processing_time,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'status': self.status
        }

