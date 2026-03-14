#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为所有用户初始化目录结构
确保每个用户都有根目录和默认子目录
"""
import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User, Directory, ModelConfig
from exts import db

def init_user_directories():
    """为所有用户初始化目录结构"""
    with app.app_context():
        print("=" * 70)
        print("为用户初始化目录结构")
        print("=" * 70)
        print()
        
        # 获取所有用户
        users = User.query.all()
        print(f"找到 {len(users)} 个用户")
        print()
        
        for user in users:
            print(f"检查用户: {user.username} (ID: {user.id})")
            
            # 检查是否有根目录
            root_dir = user.get_root_directory()
            
            if not root_dir:
                print(f"  ⚠ 用户 {user.username} 没有根目录，正在创建...")
                
                try:
                    # 创建根目录
                    root_dir = Directory.create_root(user)
                    db.session.add(root_dir)
                    db.session.flush()
                    print(f"  ✓ 已创建根目录 (ID: {root_dir.id})")
                    
                    # 创建默认子目录
                    subdir_names = ["训练数据", "测试数据", "公式映射数据", "预处理数据"]
                    for name in subdir_names:
                        sub_dir = Directory(
                            name=name,
                            parent_id=root_dir.id,
                            root_id=root_dir.id,
                            user_id=user.id,
                            root_user_id=user.id
                        )
                        db.session.add(sub_dir)
                    
                    db.session.flush()
                    print(f"  ✓ 已创建 {len(subdir_names)} 个默认子目录")
                    
                    # 检查是否有模型配置
                    config = ModelConfig.query.filter_by(user_id=user.id).first()
                    if not config:
                        print(f"  ⚠ 用户 {user.username} 没有模型配置，正在创建...")
                        config = ModelConfig(
                            user_id=user.id,
                            model_name="Transformer",
                            hidden_size=8,
                            num_layers=5,
                            dropout=0.1,
                            grid_size=200,
                            num_channels='25,50,25',
                            kernel_size=3,
                            num_heads=4,
                            hidden_space=8,
                            e_layers=2,
                            d_ff=64,
                            moving_avg=24,
                            factor=4,
                            activation="tanh",
                            use_layer_norm=False,
                            seq_len=64,
                            num_epochs=150,
                            learning_rate=0.0005,
                            input_directory="训练数据",
                            predict_target='RD',
                            input_size=15,
                            batch_size=1024,
                            output_size=1,
                            sequence_length=64,
                            scaler_type="standard",
                            loss="mae",
                            phy_equation=None,
                            phy_loss_type='mse',
                            phy_loss_weight=0,
                            phy_loss_lower=0,
                            phy_loss_upper=0,
                            number=1
                        )
                        db.session.add(config)
                        print(f"  ✓ 已创建默认模型配置")
                    
                    db.session.commit()
                    print(f"  ✓ 用户 {user.username} 的目录结构初始化完成")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"  ❌ 初始化失败: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"  ✓ 用户 {user.username} 已有根目录 (ID: {root_dir.id})")
                
                # 检查子目录
                subdirs = Directory.query.filter_by(
                    parent_id=root_dir.id,
                    deleted_at=None
                ).all()
                
                if len(subdirs) == 0:
                    print(f"  ⚠ 根目录下没有子目录，正在创建...")
                    try:
                        subdir_names = ["训练数据", "测试数据", "公式映射数据", "预处理数据"]
                        for name in subdir_names:
                            sub_dir = Directory(
                                name=name,
                                parent_id=root_dir.id,
                                root_id=root_dir.id,
                                user_id=user.id,
                                root_user_id=user.id
                            )
                            db.session.add(sub_dir)
                        db.session.commit()
                        print(f"  ✓ 已创建 {len(subdir_names)} 个默认子目录")
                    except Exception as e:
                        db.session.rollback()
                        print(f"  ❌ 创建子目录失败: {e}")
                else:
                    print(f"  ✓ 已有 {len(subdirs)} 个子目录: {', '.join([d.name for d in subdirs])}")
                
                # 检查模型配置
                config = ModelConfig.query.filter_by(user_id=user.id).first()
                if not config:
                    print(f"  ⚠ 没有模型配置，正在创建...")
                    try:
                        config = ModelConfig(
                            user_id=user.id,
                            model_name="Transformer",
                            hidden_size=8,
                            num_layers=5,
                            dropout=0.1,
                            grid_size=200,
                            num_channels='25,50,25',
                            kernel_size=3,
                            num_heads=4,
                            hidden_space=8,
                            e_layers=2,
                            d_ff=64,
                            moving_avg=24,
                            factor=4,
                            activation="tanh",
                            use_layer_norm=False,
                            seq_len=64,
                            num_epochs=150,
                            learning_rate=0.0005,
                            input_directory="训练数据",
                            predict_target='RD',
                            input_size=15,
                            batch_size=1024,
                            output_size=1,
                            sequence_length=64,
                            scaler_type="standard",
                            loss="mae",
                            phy_equation=None,
                            phy_loss_type='mse',
                            phy_loss_weight=0,
                            phy_loss_lower=0,
                            phy_loss_upper=0,
                            number=1
                        )
                        db.session.add(config)
                        db.session.commit()
                        print(f"  ✓ 已创建默认模型配置")
                    except Exception as e:
                        db.session.rollback()
                        print(f"  ❌ 创建模型配置失败: {e}")
                else:
                    print(f"  ✓ 已有模型配置")
            
            print()
        
        print("=" * 70)
        print("✓ 所有用户的目录结构检查完成")
        print("=" * 70)
        print()
        print("现在可以重启后端服务并登录了！")

if __name__ == '__main__':
    try:
        init_user_directories()
        input("\n按回车键退出...")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)
