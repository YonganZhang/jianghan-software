#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复登录错误 - 添加role字段
直接运行此脚本即可修复登录500错误
"""
import sqlite3
import os
import sys

def main():
    print("=" * 60)
    print("修复登录错误 - 添加role字段到users表")
    print("=" * 60)
    print()
    
    # 获取数据库路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'instance', 'wenjie.db')
    
    print(f"数据库路径: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ 错误: 数据库文件不存在!")
        print(f"   请确认路径是否正确: {db_path}")
        input("\n按回车键退出...")
        sys.exit(1)
    
    try:
        # 连接数据库
        print("\n正在连接数据库...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查users表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ 错误: users表不存在!")
            input("\n按回车键退出...")
            sys.exit(1)
        
        # 检查role字段是否存在
        print("正在检查role字段...")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"当前users表的字段: {', '.join(column_names)}")
        
        if 'role' in column_names:
            print("\n✓ role字段已存在")
        else:
            print("\n正在添加role字段...")
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'")
            print("✓ 成功添加role字段")
        
        # 检查并更新admin用户
        print("\n正在检查admin用户...")
        cursor.execute("SELECT id, username, role FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            user_id, username, role = admin_user
            print(f"找到admin用户: ID={user_id}, 用户名={username}, 角色={role}")
            
            if role != 'admin':
                print("正在更新admin用户角色...")
                cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
                print("✓ 已将admin用户的role设置为'admin'")
            else:
                print("✓ admin用户的role已经是'admin'")
        else:
            print("⚠ 警告: 未找到admin用户")
        
        # 提交更改
        conn.commit()
        print("\n" + "=" * 60)
        print("✓ 修复完成！所有更改已保存")
        print("=" * 60)
        
        # 显示所有用户
        print("\n当前数据库中的用户列表:")
        print("-" * 60)
        cursor.execute("SELECT id, username, email, role FROM users")
        users = cursor.fetchall()
        
        if users:
            for user in users:
                user_id, username, email, role = user
                print(f"  ID: {user_id:3d} | 用户名: {username:15s} | 邮箱: {email:25s} | 角色: {role}")
        else:
            print("  (无用户)")
        
        print("-" * 60)
        print(f"\n共 {len(users)} 个用户")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("现在可以重启后端服务并尝试登录了！")
        print("登录信息: 用户名=admin, 密码=admin")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"\n❌ 数据库错误: {e}")
        input("\n按回车键退出...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)
    
    input("\n按回车键退出...")

if __name__ == '__main__':
    main()
