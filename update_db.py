from app import create_app, db
from app.models.user import User
from sqlalchemy import text

app = create_app()
with app.app_context():
    # 创建数据库表结构
    db.create_all()

    # 检查数据库类型，如果是SQLite使用特殊方法修改字段类型
    try:
        # 获取数据库连接信息
        db_url = str(db.engine.url)
        
        if 'sqlite' in db_url:
            print("检测到SQLite数据库，使用SQLite兼容的方法修改字段类型")
            
            # SQLite修改字段类型的标准方法：创建新表、复制数据、重命名
            # 1. 创建临时表
            db.session.execute(text("""
                CREATE TABLE user_temp (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR(64),
                    email VARCHAR(120),
                    level INTEGER DEFAULT 0,
                    password VARCHAR(128),
                    password_hash VARCHAR(128),
                    vip_type INTEGER DEFAULT 0,
                    vip_start_time BIGINT DEFAULT 0,
                    vip_end_time BIGINT DEFAULT 0,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """))
            
            # 2. 复制数据到临时表，转换level字段类型
            db.session.execute(text("""
                INSERT INTO user_temp 
                (id, username, email, level, password, password_hash, vip_type, vip_start_time, vip_end_time, created_at, updated_at)
                SELECT 
                    id, username, email, 
                    CASE 
                        WHEN level IS NULL THEN 0
                        WHEN level = '' THEN 0
                        ELSE CAST(level AS INTEGER)
                    END,
                    password, password_hash, vip_type, vip_start_time, vip_end_time, created_at, updated_at
                FROM user
            """))
            
            # 3. 删除原表
            db.session.execute(text("DROP TABLE user"))
            
            # 4. 重命名临时表
            db.session.execute(text("ALTER TABLE user_temp RENAME TO user"))
            
            db.session.commit()
            print("已成功修改level字段类型为INTEGER（SQLite兼容方法）")
        else:
            # 对于其他数据库使用标准ALTER TABLE语法
            db.session.execute(text("ALTER TABLE user MODIFY COLUMN level INTEGER DEFAULT 0"))
            db.session.commit()
            print("已成功修改level字段类型为INTEGER")
            
    except Exception as e:
        print(f"修改字段类型时出错: {e}")
    
    # 更新所有用户的level字段为0
    users = User.query.all()
    for user in users:
        if user.id == 1:
            user.level = 1
        else:
            user.level = 0
    db.session.commit()
    print(f"已更新 {len(users)} 个用户的level字段为0")