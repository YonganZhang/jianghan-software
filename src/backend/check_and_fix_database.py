#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查并修复数据库 - 完整诊断和修复工具
"""
import sqlite3
import os
import sys
from werkzeug.security import generate_password_hash

def main():
    print("=" * 70)
    print("数据库诊断和修复工具")
    print("=" * 70)
    print()
    
    # 获取数据库路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'instance', 'wenjie.db')
    
    print(f"数据库路径: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ 错误: 数据库文件不存在!")
        print(f"   请先运行后端服务以创建数据库")
        input("\n按回车键退出...")
        sys.exit(1)
    
    try:
        # 连接数据库
        print("\n正在连接数据库...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 检查users表是否存在
        print("\n" + "=" * 70)
        print("步骤1: 检查users表")
        print("=" * 70)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ 错误: users表不存在!")
            input("\n按回车键退出...")
            sys.exit(1)
        print("✓ users表存在")
        
        # 2. 检查表结构
        print("\n" + "=" * 70)
        print("步骤2: 检查表结构")
        print("=" * 70)
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"当前字段: {', '.join(column_names)}")
        
        # 3. 检查并添加role字段
        print("\n" + "=" * 70)
        print("步骤3: 检查role字段")
        print("=" * 70)
        
        if 'role' not in column_names:
            print("⚠ role字段不存在，正在添加...")
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'")
                conn.commit()
                print("✓ 成功添加role字段")
            except sqlite3.Error as e:
                print(f"❌ 添加role字段失败: {e}")
                conn.rollback()
        else:
            print("✓ role字段已存在")
        
        # 4. 检查admin用户
        print("\n" + "=" * 70)
        print("步骤4: 检查admin用户")
        print("=" * 70)
        
        cursor.execute("SELECT id, username, email, password_hash, role FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            user_id, username, email, password_hash, role = admin_user
            print(f"✓ 找到admin用户:")
            print(f"  - ID: {user_id}")
            print(f"  - 用户名: {username}")
            print(f"  - 邮箱: {email}")
            print(f"  - 角色: {role}")
            print(f"  - 密码哈希: {password_hash[:50]}...")
            
            # 检查并更新role
            if role != 'admin':
                print("\n⚠ admin用户的role不是'admin'，正在更新...")
                cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
                conn.commit()
                print("✓ 已更新admin用户的role为'admin'")
            
            # 检查密码是否正确
            print("\n正在验证admin密码...")
            from werkzeug.security import check_password_hash
            if check_password_hash(password_hash, 'admin'):
                print("✓ admin密码正确 (admin)")
            elif check_password_hash(password_hash, 'admin123'):
                print("⚠ admin密码是旧密码 (admin123)，正在更新为新密码 (admin)...")
                new_hash = generate_password_hash('admin')
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (new_hash,))
                conn.commit()
                print("✓ 已更新admin密码为 'admin'")
            else:
                print("⚠ admin密码未知，正在重置为 'admin'...")
                new_hash = generate_password_hash('admin')
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (new_hash,))
                conn.commit()
                print("✓ 已重置admin密码为 'admin'")
                
        else:
            print("⚠ 未找到admin用户，正在创建...")
            password_hash = generate_password_hash('admin')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, created_at)
                VALUES ('admin', 'admin@example.com', ?, 'admin', datetime('now'))
            """, (password_hash,))
            conn.commit()
            print("✓ 已创建admin用户 (用户名: admin, 密码: admin)")
        
        # 5. 显示所有用户
        print("\n" + "=" * 70)
        print("步骤5: 当前所有用户")
        print("=" * 70)
        
        cursor.execute("SELECT id, username, email, role, created_at FROM users")
        users = cursor.fetchall()
        
        if users:
            print(f"\n共 {len(users)} 个用户:")
            print("-" * 70)
            for user in users:
                user_id, username, email, role, created_at = user
                print(f"ID: {user_id:3d} | 用户名: {username:15s} | 邮箱: {email:30s} | 角色: {role:8s}")
            print("-" * 70)
        else:
            print("(无用户)")
        
        # 6. 测试登录
        print("\n" + "=" * 70)
        print("步骤6: 测试admin登录")
        print("=" * 70)
        
        cursor.execute("SELECT password_hash FROM users WHERE username = 'admin'")
        result = cursor.fetchone()
        if result:
            from werkzeug.security import check_password_hash
            if check_password_hash(result[0], 'admin'):
                print("✓ 登录测试成功！用户名: admin, 密码: admin")
            else:
                print("❌ 登录测试失败！密码验证不通过")
        else:
            print("❌ 登录测试失败！未找到admin用户")
        
        conn.close()
        
        # 7. 初始化用户目录结构
        print("\n" + "=" * 70)
        print("步骤7: 初始化用户目录结构")
        print("=" * 70)
        
        print("\n正在为所有用户创建必要的目录结构...")
        try:
            import subprocess
            result = subprocess.run(
                ['python', 'init_user_directories.py'],
                capture_output=True,
                text=True,
                cwd=script_dir
            )
            if result.returncode == 0:
                print("✓ 目录结构初始化完成")
            else:
                print("⚠ 目录初始化可能有问题，请手动运行: python init_user_directories.py")
        except Exception as e:
            print(f"⚠ 无法自动初始化目录: {e}")
            print("请手动运行: python init_user_directories.py")
        
        # 8. 总结
        print("\n" + "=" * 70)
        print("修复完成！")
        print("=" * 70)
        print("\n现在可以使用以下信息登录:")
        print("  用户名: admin")
        print("  密码: admin")
        print("\n请重启后端服务，然后尝试登录。")
        print("=" * 70)
        
    except sqlite3.Error as e:
        print(f"\n❌ 数据库错误: {e}")
        import traceback
        traceback.print_exc()
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
