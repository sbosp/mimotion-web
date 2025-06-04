from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()
    print("数据库表结构已更新") 