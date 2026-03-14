#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查删除用户问题 - 不依赖Flask
"""
import sqlite3
import os
import glob

def find_database():
    """查找数据库文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 可能的数据库路径
    possible_paths = [
        os.path.join(script_dir, 'instance', 'wenjie.db'),
        os.path.join(script_dir, 'instance', 'database.db'),
        os.path.join(script_dir, 'wenjie.db'),
        os.path.join(script_dir, 'database.db'),
    ]
    
    # 查找第一个存在的数据库文件
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 如果都不存在，尝试搜索所有.db文件
    db_files = glob.glob(os.path.join(script_dir, '**', '*.db'), recursive=True)
    if db_files:
        print(f"\n找到以下数据库文件:")
        for i, db_file in enumerate(db_files, 1):
            print(f"  {i}. {db_file}")
        
        if len(db_files) == 1:
            return db_files[0]
        else:
            choice = input(f"\n请选择要使用的数据库 (1-{len(db_files)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(db_files):
                    return db_files[idx]
            except ValueError:
                pass
    
    return None

def check_database():
    """检查数据库连接"""
    db_path = find_database()
    
    if not db_path:
        print("\n" + "="*70)
        print("错误: 找不到数据库文件")
        print("="*70)
        print("\n请确保:")
        print("  1. 后端已经运行过（会自动创建数据库）")
        print("  2. 数据库文件位于 backend/instance/ 目录下")
        print("  3. 数据库文件名为 wenjie.db 或 database.db")
        print("\n如果还没有运行过后端，请先运行:")
        print("  cd backend")
        print("  python app.py")
        print("="*70)
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        print(f"\n✓ 成功连接到数据库: {db_path}\n")
        return conn
    except Exception as e:
        print(f"\n✗ 连接数据库失败: {e}\n")
        return None

def list_users(conn):
    """列出所有用户"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role FROM users")
        users = cursor.fetchall()
        
        print("\n" + "="*70)
        print("所有用户列表:")
        print("="*70)
        print(f"{'ID':<5} {'用户名':<20} {'邮箱':<30} {'角色':<10}")
        print("-"*70)
        
        for user in users:
            user_id, username, email, role = user
            print(f"{user_id:<5} {username:<20} {email:<30} {role:<10}")
        
        print("="*70)
        print(f"共 {len(users)} 个用户\n")
        
        return users
    except Exception as e:
        print(f"查询用户失败: {e}")
        return []

def check_user_relations(conn, user_id):
    """检查用户的关联数据"""
    try:
        cursor = conn.cursor()
        
        # 获取用户信息
        cursor.execute("SELECT username, email, role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"\n用户 ID={user_id} 不存在")
            return
        
        username, email, role = user
        print(f"\n{'='*70}")
        print(f"用户信息: {username} (ID: {user_id}, 角色: {role})")
        print(f"邮箱: {email}")
        print("="*70)
        
        # 检查各种关联数据
        tables_to_check = [
            ('directories', 'user_id', '目录'),
            ('files', 'user_id', '文件'),
            ('model_config', 'user_id', '模型配置'),
            ('trainmodel', 'user_id', '训练模型'),
            ('smartformula', 'user_id', '智能公式'),
            ('lossimagemodel', 'user_id', '损失图片')
        ]
        
        for table, column, name in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} = ?", (user_id,))
                count = cursor.fetchone()[0]
                print(f"{name}: {count} 条记录")
            except sqlite3.OperationalError:
                print(f"{name}: 表不存在或列不存在")
        
        print("="*70)
        
    except Exception as e:
        print(f"检查用户关联数据失败: {e}")
        import traceback
        traceback.print_exc()

def check_foreign_keys(conn):
    """检查外键约束"""
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        print(f"\n外键约束状态: {'启用' if fk_status else '禁用'}")
        return fk_status
    except Exception as e:
        print(f"检查外键约束失败: {e}")
        return None

def get_table_info(conn, table_name):
    """获取表结构信息"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n表 {table_name} 的结构:")
        print("-"*70)
        for col in columns:
            col_id, name, col_type, not_null, default, pk = col
            print(f"  {name}: {col_type} {'NOT NULL' if not_null else ''} {'PRIMARY KEY' if pk else ''}")
        
        # 获取外键信息
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()
        if fks:
            print(f"\n外键约束:")
            for fk in fks:
                print(f"  {fk}")
        
    except Exception as e:
        print(f"获取表信息失败: {e}")

def main():
    print("\n" + "="*70)
    print(" "*20 + "删除用户问题诊断工具")
    print("="*70)
    
    # 检查数据库
    conn = check_database()
    if not conn:
        return
    
    try:
        # 检查外键约束
        check_foreign_keys(conn)
        
        # 列出所有用户
        users = list_users(conn)
        
        if not users:
            print("\n⚠ 数据库中没有用户")
            print("请先运行后端并注册用户")
            return
        
        # 交互式菜单
        while True:
            print("\n" + "-"*70)
            print("请选择操作:")
            print("  1. 查看用户关联数据（推荐：删除前先查看）")
            print("  2. 查看表结构")
            print("  3. 重新列出所有用户")
            print("  0. 退出")
            print("-"*70)
            
            choice = input("\n请输入选项 (0-3): ").strip()
            
            if choice == '0':
                print("\n退出工具")
                break
            elif choice == '1':
                user_id = input("\n请输入用户ID: ").strip()
                try:
                    user_id = int(user_id)
                    check_user_relations(conn, user_id)
                except ValueError:
                    print("\n✗ 无效的用户ID，请输入数字")
            elif choice == '2':
                print("\n可用的表:")
                print("  1. users        - 用户表")
                print("  2. directories  - 目录表")
                print("  3. files        - 文件表")
                print("  4. model_config - 模型配置表")
                print("  5. trainmodel   - 训练模型表")
                print("  6. smartformula - 智能公式表")
                table_choice = input("\n请选择表 (1-6): ").strip()
                tables = {
                    '1': 'users',
                    '2': 'directories',
                    '3': 'files',
                    '4': 'model_config',
                    '5': 'trainmodel',
                    '6': 'smartformula'
                }
                if table_choice in tables:
                    get_table_info(conn, tables[table_choice])
                else:
                    print("\n✗ 无效的选择")
            elif choice == '3':
                list_users(conn)
            else:
                print("\n✗ 无效的选项，请输入 0-3")
    
    finally:
        conn.close()
        print("\n✓ 数据库连接已关闭")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按回车键退出...")
