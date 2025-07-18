#!/usr/bin/env python3
"""
WSGI entry point for AIAPad production deployment
"""

import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables for production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('PYTHONPATH', project_dir)

from src.main import app

# Configure for production
app.config.update(
    DEBUG=False,
    TESTING=False,
    SECRET_KEY=os.environ.get('SECRET_KEY', 'production-secret-key-change-me'),
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', f'sqlite:///{project_dir}/database/production.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={
        'pool_pre_ping': True,
        'pool_recycle': 300,
    },
    MAX_CONTENT_LENGTH=5 * 1024 * 1024 * 1024,  # 5GB
    UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', '/opt/aiapad/uploads'),
    JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-me'),
    JWT_ACCESS_TOKEN_EXPIRES=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)),
    JWT_REFRESH_TOKEN_EXPIRES=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000)),
)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

