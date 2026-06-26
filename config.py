import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fitai-secret-key-2025-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
       'mysql+pymysql://syKrtU8ssxbajhq.root:1P5MLsiNAsAEThMe@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/ai_diet_planner?ssl_verify_cert=true&ssl_verify_identity=true'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max upload

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}