"""
在app启动时自动初始化role字段
"""
import sqlite3
import os

def init_role_field(app):
    """初始化role字段"""
    try:
        # 获取数据库路径
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if not db_uri:
            print("⚠ 无法获取数据库URI")
            return
            
        # 处理不同格式的数据库URI
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            db_path = db_uri.replace('sqlite://', '')
        
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.root_path, db_path)
        
        if not os.path.exists(db_path):
            print(f"⚠ 数据库文件不存在: {db_path}")
            return
        
        print(f"正在检查数据库: {db_path}")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 检查role字段是否存在
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'role' not in column_names:
                print("检测到users表缺少role字段，正在添加...")
                cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'")
                cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
                conn.commit()
                print("✓ 成功添加role字段并设置admin用户角色")
            else:
                print("✓ role字段已存在")
                # 确保admin用户的role为admin
                cursor.execute("SELECT role FROM users WHERE username = 'admin'")
                result = cursor.fetchone()
                if result and result[0] != 'admin':
                    cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
                    conn.commit()
                    print("✓ 已更新admin用户的角色为admin")
                    
        except sqlite3.Error as e:
            print(f"❌ 数据库操作失败: {e}")
            conn.rollback()
        finally:
            conn.close()
            
    except Exception as e:
        print(f"❌ 初始化role字段时出错: {e}")
        print("请手动运行 add_role_field.py 脚本或查看修复登录错误.md文档")
