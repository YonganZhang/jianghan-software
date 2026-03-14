"""
手动添加role字段到users表
运行方式: python add_role_field.py
"""
import sqlite3
import os

# 数据库文件路径
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'wenjie.db')

print(f"正在连接数据库: {db_path}")

try:
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查role字段是否已存在
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"当前users表的字段: {column_names}")
    
    if 'role' in column_names:
        print("✓ role字段已存在")
    else:
        print("× role字段不存在，正在添加...")
        
        # 添加role字段
        cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'")
        print("✓ 成功添加role字段")
    
    # 确保admin用户的role为'admin'
    cursor.execute("SELECT id, username, role FROM users WHERE username = 'admin'")
    admin_user = cursor.fetchone()
    
    if admin_user:
        print(f"找到admin用户: id={admin_user[0]}, username={admin_user[1]}, role={admin_user[2]}")
        if admin_user[2] != 'admin':
            cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
            print("✓ 已将admin用户的role设置为'admin'")
        else:
            print("✓ admin用户的role已经是'admin'")
    else:
        print("⚠ 未找到admin用户")
    
    # 提交更改
    conn.commit()
    print("\n✓ 所有更改已成功保存到数据库")
    
    # 显示所有用户
    cursor.execute("SELECT id, username, email, role FROM users")
    users = cursor.fetchall()
    print(f"\n当前数据库中的用户列表 (共{len(users)}个):")
    print("-" * 60)
    for user in users:
        print(f"ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: {user[3]}")
    print("-" * 60)
    
except sqlite3.Error as e:
    print(f"❌ 数据库错误: {e}")
except Exception as e:
    print(f"❌ 发生错误: {e}")
finally:
    if conn:
        conn.close()
        print("\n数据库连接已关闭")

print("\n完成！现在可以重启后端服务并尝试登录。")
