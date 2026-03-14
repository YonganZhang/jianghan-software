#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试删除用户功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User, Directory, File, ModelConfig, Trainmodel, Smartformula, Lossimagemodel
from exts import db

def check_user_relations(user_id):
    """检查用户的所有关联数据"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"用户 ID={user_id} 不存在")
            return
        
        print(f"\n检查用户: {user.username} (ID: {user_id}, 角色: {user.role})")
        print("=" * 60)
        
        # 检查目录
        directories = Directory.query.filter_by(user_id=user_id).all()
        print(f"目录数量: {len(directories)}")
        for d in directories:
            print(f"  - {d.name} (ID: {d.id})")
        
        # 检查文件
        files = File.query.filter_by(user_id=user_id).all()
        print(f"文件数量: {len(files)}")
        for f in files[:5]:  # 只显示前5个
            print(f"  - {f.name} (ID: {f.id})")
        if len(files) > 5:
            print(f"  ... 还有 {len(files) - 5} 个文件")
        
        # 检查模型配置
        config = ModelConfig.query.filter_by(user_id=user_id).first()
        print(f"模型配置: {'存在' if config else '不存在'}")
        
        # 检查训练模型
        train_models = Trainmodel.query.filter_by(user_id=user_id).all()
        print(f"训练模型数量: {len(train_models)}")
        
        # 检查智能公式
        formulas = Smartformula.query.filter_by(user_id=user_id).all()
        print(f"智能公式数量: {len(formulas)}")
        
        # 检查损失图片
        loss_images = Lossimagemodel.query.filter_by(user_id=user_id).all()
        print(f"损失图片数量: {len(loss_images)}")
        
        print("=" * 60)

def list_all_users():
    """列出所有用户"""
    with app.app_context():
        users = User.query.all()
        print("\n所有用户列表:")
        print("=" * 60)
        for user in users:
            print(f"ID: {user.id:3d} | 用户名: {user.username:15s} | 角色: {user.role:8s} | 邮箱: {user.email}")
        print("=" * 60)
        print(f"共 {len(users)} 个用户")

def test_delete_user(user_id):
    """测试删除用户"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"\n❌ 用户 ID={user_id} 不存在")
            return False
        
        if user.role == 'admin':
            print(f"\n❌ 不能删除管理员账号: {user.username}")
            return False
        
        print(f"\n准备删除用户: {user.username} (ID: {user_id})")
        print("检查关联数据...")
        check_user_relations(user_id)
        
        confirm = input("\n确定要删除这个用户吗？(yes/no): ")
        if confirm.lower() != 'yes':
            print("取消删除")
            return False
        
        try:
            # 删除关联数据
            print("\n开始删除...")
            
            # 1. 删除目录和文件
            print("删除目录和文件...")
            directories = Directory.query.filter_by(user_id=user_id).all()
            for directory in directories:
                files = File.query.filter_by(directory_id=directory.id).all()
                for file in files:
                    db.session.delete(file)
                db.session.delete(directory)
            print(f"  ✓ 删除了 {len(directories)} 个目录")
            
            # 2. 删除模型配置
            print("删除模型配置...")
            config = ModelConfig.query.filter_by(user_id=user_id).first()
            if config:
                db.session.delete(config)
                print("  ✓ 删除了模型配置")
            
            # 3. 删除训练模型
            print("删除训练模型...")
            train_models = Trainmodel.query.filter_by(user_id=user_id).all()
            for model in train_models:
                db.session.delete(model)
            print(f"  ✓ 删除了 {len(train_models)} 个训练模型")
            
            # 4. 删除智能公式
            print("删除智能公式...")
            formulas = Smartformula.query.filter_by(user_id=user_id).all()
            for formula in formulas:
                db.session.delete(formula)
            print(f"  ✓ 删除了 {len(formulas)} 个智能公式")
            
            # 5. 删除损失图片
            print("删除损失图片...")
            loss_images = Lossimagemodel.query.filter_by(user_id=user_id).all()
            for loss_image in loss_images:
                db.session.delete(loss_image)
            print(f"  ✓ 删除了 {len(loss_images)} 个损失图片")
            
            # 6. 删除用户
            print("删除用户...")
            db.session.delete(user)
            
            # 提交
            db.session.commit()
            print(f"\n✓ 成功删除用户: {user.username}")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 删除失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    print("=" * 60)
    print("用户删除功能测试工具")
    print("=" * 60)
    
    while True:
        print("\n请选择操作:")
        print("1. 列出所有用户")
        print("2. 检查用户关联数据")
        print("3. 删除用户")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-3): ").strip()
        
        if choice == '0':
            print("退出")
            break
        elif choice == '1':
            list_all_users()
        elif choice == '2':
            user_id = input("请输入用户ID: ").strip()
            try:
                user_id = int(user_id)
                check_user_relations(user_id)
            except ValueError:
                print("❌ 无效的用户ID")
        elif choice == '3':
            user_id = input("请输入要删除的用户ID: ").strip()
            try:
                user_id = int(user_id)
                test_delete_user(user_id)
            except ValueError:
                print("❌ 无效的用户ID")
        else:
            print("❌ 无效的选项")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
