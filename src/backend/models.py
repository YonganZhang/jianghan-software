from exts import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy.dialects.mysql import LONGBLOB, JSON
from sqlalchemy.dialects.sqlite import JSON
import os
from flask import current_app
from utils_path import resolve_content_path, to_relative_content_path
import hashlib
import pickle
import gzip
import uuid


# 辅助函数
def calculate_sha256(data):
    return hashlib.sha256(data).hexdigest()


# 用户表
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'admin' 或 'user'
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # User模型
    model_config = db.relationship(
        'ModelConfig',
        uselist=False,  # 关键：确保一对一
        back_populates='user',
        cascade='all, delete-orphan'
    )

    # 关系定义
    root_directory = db.relationship(
        'Directory',
        uselist=False,
        back_populates='root_owner',
        foreign_keys='Directory.root_user_id'
    )

    # # 与图片表1的关系
    # image1 = db.relationship(
    #     'ImageFile1',
    #     backref='ur1',
    #     lazy=True
    # )
    #
    # # 与图片表2的关系
    # image2 = db.relationship(
    #     'ImageFile2',
    #     backref='ur2',
    #     lazy=True
    # )
    # 与损失图片的关系
    # image3 = db.relationship(
    #     'Lossimagemodel',
    #     backref='ur3',
    #     lazy=True
    # )
    # 与训练模型的关系
    ttrain = db.relationship(
        'Trainmodel',
        backref='urw',
        lazy=True
    )

    # # 与坐标的关系Coordinate
    # Coord = db.relationship(
    #     'Coordinate',
    #     backref='uuhh',
    #     lazy=True
    # )
    #
    # # 与智能公式的一对多关系
    smart_formulas = db.relationship(
        'Smartformula',  # 关联的模型类名
        backref='owner',  # 在Smartformula中反向引用User的属性名
        lazy=True,  # 懒加载模式
        cascade='all, delete-orphan'  # 级联删除：删除用户时同时删除其所有智能公式记录
    )

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def password(self):
        raise AttributeError('密码是不可读的属性')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_root_directory(self):
        """获取用户的根目录"""
        return self.root_directory


# 文件目录表
class Directory(db.Model):
    __tablename__ = 'directories'

    id = db.Column(db.Integer, primary_key=True)
    root_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('directories.id'))
    name = db.Column(db.String(255), nullable=False)
    root_id = db.Column(db.Integer, nullable=False)

    deleted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow,
                           onupdate=datetime.datetime.utcnow)

    parent = db.relationship('Directory', remote_side=[id],
                             backref=db.backref('children', lazy='dynamic'))
    files = db.relationship('File', back_populates='directory', lazy='dynamic')
    owner = db.relationship('User', foreign_keys=[user_id], backref='directories')
    root_owner = db.relationship('User', foreign_keys=[root_user_id],
                                 back_populates='root_directory')

    def __repr__(self):
        return f'<Directory {self.name} (ID:{self.id})>'

    @property
    def is_root(self):
        return self.parent_id is None

    @classmethod
    def create_root(cls, user):
        """为用户创建根目录"""
        root = cls(
            name="Root",
            parent_id=None,
            user_id=user.id,
            root_user_id=user.id,
            root_id=0  # 临时值，稍后更新
        )
        db.session.add(root)
        db.session.flush()  # 获取ID但不提交

        # 设置root_id为自己ID
        root.root_id = root.id
        return root

    def add_child_directory(self, name, user):
        """添加子目录"""
        if user.id != self.user_id:
            raise ValueError("用户不拥有此目录")

        child = Directory(
            name=name,
            parent_id=self.id,
            root_id=self.root_id,
            user_id=user.id,
            root_user_id=self.root_user_id
        )
        db.session.add(child)
        return child

    def get_path(self):
        """获取目录的完整路径"""
        path_parts = []
        current = self

        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        return "/" + "/".join(path_parts)

    def soft_delete(self):
        """软删除当前目录及其所有子目录和子文件"""
        current_time = datetime.datetime.utcnow()
        # 递归删除所有子目录和文件
        stack = [self]
        while stack:
            current_dir = stack.pop()
            # 跳过已删除的目录（避免重复处理）
            if current_dir.deleted_at is not None:
                continue
            # 1. 标记当前目录为已删除
            current_dir.deleted_at = current_time
            # 2. 删除当前目录下的所有文件
            for file in current_dir.files.filter(File.deleted_at.is_(None)):
                file.deleted_at = current_time
            # 3. 将所有未删除的子目录加入处理栈
            children = current_dir.children.filter(Directory.deleted_at.is_(None)).all()
            stack.extend(children)
        return self


# 文件表
class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    # 用户关联
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 文件属性
    directory_id = db.Column(db.Integer, db.ForeignKey('directories.id'), nullable=False)
    root_id = db.Column(db.Integer, nullable=False)  # 冗余存储根目录ID
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum('xlsx', 'txt', 'las', name='file_type'), nullable=False)
    content = db.Column(db.String(512), nullable=False)
    # content = db.Column(db.LargeBinary, nullable=False)
    size = db.Column(db.Integer, nullable=False, default=0)
    file_hash = db.Column(db.String(64), nullable=False, index=True)  # 添加索引加速去重

    # 时间戳cotent
    deleted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow,
                           onupdate=datetime.datetime.utcnow)

    # 关系定义
    directory = db.relationship('Directory', back_populates='files')
    owner = db.relationship('User', backref='files')
    related_configs = db.relationship('ModelConfig', back_populates='original_file')
    errtab = db.relationship('Errtab', uselist=False, back_populates='file',
                             cascade='all, delete-orphan')


    def __repr__(self):
        return f'<File {self.name} (Type:{self.type}, Size:{self.size} bytes)>'

    @property
    def is_root_level(self):
        """判断文件是否在根目录层级"""
        return self.directory_id == self.root_id

    @property
    def full_path(self):
        """获取文件的完整路径"""
        return self.directory.get_path() + "/" + self.name

    @classmethod
    def create_file(cls, user, directory, file_data, file_type):
        """创建新文件 - 需要修改此方法"""
        if user.id != directory.user_id:
            raise ValueError("User does not own the target directory")

        # 计算文件哈希和大小
        file_content = file_data.read()  # 读取文件内容
        file_hash = calculate_sha256(file_content)
        file_size = len(file_content)

        # 生成文件保存路径
        file_path = cls._save_file_to_disk(file_data, file_content, user.id)

        new_file = cls(
            name=file_data.filename,
            directory_id=directory.id,
            root_id=directory.root_id,
            user_id=user.id,
            type=file_type,
            content=file_path,  # 存储文件路径而不是内容
            size=file_size,
            file_hash=file_hash
        )
        db.session.add(new_file)
        return new_file

    @classmethod
    def _save_file_to_disk(cls, file_data, file_content, user_id):
        """将文件保存到磁盘并返回文件路径"""
        # 1. 定义基础存储目录
        base_dir = os.path.join(current_app.root_path, 'uploads', str(user_id))

        # 2. 确保目录存在
        os.makedirs(base_dir, exist_ok=True)

        # 3. 生成唯一文件名避免冲突
        filename = file_data.filename
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        file_path = os.path.join(base_dir, unique_filename)

        # 4. 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # 5. 返回相对路径或绝对路径
        return file_path  # 或返回相对于项目根目录的相对路径

    def soft_delete(self):
        """软删除文件（可选：同时删除磁盘文件）"""
        if self.deleted_at is None:
            self.deleted_at = datetime.datetime.utcnow()
            # 可选：如果需要彻底删除文件，取消下面的注释
            if os.path.exists(self.content):
                os.remove(self.content)
        return self


# 模型参数表
class ModelConfig(db.Model):
    __tablename__ = 'model_config'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True  # 作为主键确保唯一性
    )
    model_name = db.Column(db.Enum('LSTM', 'GRU', 'BiLSTM', 'TCN', 'Transformer', 'Transformer_KAN', 'BP', 'Autoformer',
                                   name='model_type'), default='Transformer', nullable=False)
    hidden_size = db.Column(db.Integer, default=8)
    num_layers = db.Column(db.Integer, default=5)
    dropout = db.Column(db.Float, default=0.1)
    grid_size = db.Column(db.Integer, default=200)
    num_channels = db.Column(db.String(50), default='25,50,25')  # 存储逗号分隔的字符串
    kernel_size = db.Column(db.Integer, default=3)
    num_heads = db.Column(db.Integer, default=4)
    hidden_space = db.Column(db.Integer, default=8)
    e_layers = db.Column(db.Integer, default=2)
    d_ff = db.Column(db.Integer, default=64)
    moving_avg = db.Column(db.Integer, default=24)
    factor = db.Column(db.Integer, default=4)
    activation = db.Column(
        db.Enum('relu', 'leaky_relu', 'elu', 'gelu', 'sigmoid', 'tanh', 'softplus', 'silu', 'none', name='act_type'),
        default='tanh', nullable=False)
    use_layer_norm = db.Column(db.Boolean, default=False)
    seq_len = db.Column(db.Integer, default=64)
    num_epochs = db.Column(db.Integer, default=150)
    learning_rate = db.Column(db.Float, default=0.0005)
    input_directory = db.Column(db.String(255), default='data_save/套管栓测试数据')
    predict_target = db.Column(db.String(50), default='RD')
    input_size = db.Column(db.Integer, default=15)
    batch_size = db.Column(db.Integer, default=1024)
    output_size = db.Column(db.Integer, default=1)
    sequence_length = db.Column(db.Integer, default=64)
    scaler_type = db.Column(db.Enum('minmax', 'standard', 'robust', name='sca_type'), nullable=True)
    loss = db.Column(
        db.Enum('mse', 'mae', 'huber', 'smooth_l1', 'log_cosh', 'quantile', 'mape', 'smape', name='loss_type'),
        default='mae', nullable=False)
    phy_equation = db.Column(db.Text, default='')
    phy_loss_type = db.Column(db.Enum('mse', 'mae', name='phy_loss_type'), default='mse', nullable=False)
    phy_loss_weight = db.Column(db.Float, default=0.0)
    phy_loss_lower = db.Column(db.Float, default=0.0)
    phy_loss_upper = db.Column(db.Float, default=0.0)
    threshold = db.Column(db.Integer, default=4)

    # pkl文件保存字段 - 存储文件路径
    trainloaderpkl = db.Column(db.String(512), nullable=True)  # 存储trainloader的pkl文件路径
    valloaderpkl = db.Column(db.String(512), nullable=True)  # 存储valloader的pkl文件路径
    xpkl = db.Column(db.String(512), nullable=True)  # 存储x_scaler的pkl文件路径
    ypkl = db.Column(db.String(512), nullable=True)  # 存储y_scaler的pkl文件路径

    # 存放图片批次
    number = db.Column(db.Integer, nullable=True)

    # 关联字段
    dad_id = db.Column(db.Integer, db.ForeignKey('directories.id'), nullable=True)
    original_file_id = db.Column(
        db.Integer,
        db.ForeignKey('files.id'),
        nullable=True,
        comment="用户最初处理的原始文件ID，关联file表"
    )

    # 关系定义
    user = db.relationship('User', back_populates='model_config')
    original_file = db.relationship('File', back_populates='related_configs')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_value_dict(self):
        """转换为模型训练所需的字典格式，并进行类型转换"""
        value_dict = {}

        # 遍历所有数据库列
        for column in self.__table__.columns:
            # 跳过不需要的字段
            if column.name in ['user_id', 'updated_at']:
                continue

            value = getattr(self, column.name)

            # 特殊字段处理
            if column.name == 'num_channels':
                # 将逗号分隔的字符串转换为整数列表
                value_dict[column.name] = [int(x) for x in value.split(',')] if value else []
            elif column.type.python_type == bool:
                # 布尔类型直接转换
                value_dict[column.name] = bool(value)
            elif isinstance(value, (int, float)):
                # 数值类型保持原样
                value_dict[column.name] = value
            elif isinstance(value, str) and value.isdigit():
                # 整数字符串转换
                value_dict[column.name] = int(value)
            else:
                try:
                    # 尝试转换为浮点数
                    value_dict[column.name] = float(value)
                except (ValueError, TypeError):
                    # 其他类型保留字符串
                    value_dict[column.name] = str(value)

        return value_dict

    def _get_pkl_dir(self):
        """获取pkl文件的存储目录"""
        pkl_dir = os.path.join(current_app.root_path, 'uploads', str(self.user_id), 'model_pkl')
        os.makedirs(pkl_dir, exist_ok=True)
        return pkl_dir

    def save_pkl(self, pkl_type, data):
        """
        保存pkl数据到文件并记录路径，同时删除同类型旧文件
        pkl_type: 类型，可选值: 'trainloader', 'valloader', 'x', 'y'
        data: 要保存的对象数据
        """
        import pickle
        import gzip
        import uuid

        valid_types = ['trainloader', 'valloader', 'x', 'y']
        if pkl_type not in valid_types:
            raise ValueError(f"不支持的pkl类型: {pkl_type}，支持的类型为: {valid_types}")

        # 1. 确定对应的字段名
        field_name = f"{pkl_type}pkl"

        # 2. 清理旧文件
        try:
            old_file_path = getattr(self, field_name, None)
            if old_file_path:
                real_old = resolve_content_path(old_file_path)
                if real_old and os.path.exists(real_old):
                    os.remove(real_old)
            setattr(self, field_name, None)
            db.session.flush()
        except Exception:
            pass  # 即使清理失败，仍继续保存新文件

        # 3. 生成新文件路径
        pkl_dir = self._get_pkl_dir()
        filename = f"{pkl_type}_{uuid.uuid4().hex[:12]}.pkl.gz"
        new_file_path = os.path.join(pkl_dir, filename)

        # 4. 保存新文件
        with gzip.open(new_file_path, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

        # 5. 更新数据库路径字段（存相对路径）
        rel_path = to_relative_content_path(new_file_path)
        setattr(self, field_name, rel_path)
        db.session.flush()

        return new_file_path

    def load_pkl(self, pkl_type):
        """
        从文件加载pkl数据
        pkl_type: 类型，可选值: 'trainloader', 'valloader', 'x', 'y'
        """
        import pickle
        import gzip

        valid_types = ['trainloader', 'valloader', 'x', 'y']
        if pkl_type not in valid_types:
            raise ValueError(f"不支持的pkl类型: {pkl_type}，支持的类型为: {valid_types}")

        # 获取文件路径
        field_name = f"{pkl_type}pkl"
        stored_path = getattr(self, field_name)

        if not stored_path:
            raise FileNotFoundError(f"{pkl_type}的pkl文件路径未设置")

        file_path = resolve_content_path(stored_path)
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"{pkl_type}的pkl文件不存在: {stored_path}")

        with gzip.open(file_path, 'rb') as f:
            data = pickle.load(f)
        return data

    def delete_pkl_files(self):
        """删除所有关联的pkl文件并清除路径记录"""
        pkl_types = ['trainloader', 'valloader', 'x', 'y']
        for pkl_type in pkl_types:
            field_name = f"{pkl_type}pkl"
            stored_path = getattr(self, field_name)
            if stored_path:
                real_path = resolve_content_path(stored_path)
                if real_path and os.path.exists(real_path):
                    try:
                        os.remove(real_path)
                    except Exception:
                        pass
                setattr(self, field_name, None)
        db.session.flush()


# 存放每次训练对应的训练参数
class Trainingparameters(db.Model):
    __tablename__ = 'trainingparameters'

    # 1. 新增主键（必须，用于关联）
    id = db.Column(db.Integer, primary_key=True)

    model_name = db.Column(db.Enum('LSTM', 'GRU', 'BiLSTM', 'TCN', 'Transformer', 'Transformer_KAN', 'BP', 'Autoformer',
                                   name='model_type'), default='Transformer', nullable=False)
    hidden_size = db.Column(db.Integer, default=8)
    num_layers = db.Column(db.Integer, default=5)
    dropout = db.Column(db.Float, default=0.1)
    grid_size = db.Column(db.Integer, default=200)
    num_channels = db.Column(db.String(50), default='25,50,25')  # 存储逗号分隔的字符串
    kernel_size = db.Column(db.Integer, default=3)
    num_heads = db.Column(db.Integer, default=4)
    hidden_space = db.Column(db.Integer, default=8)
    e_layers = db.Column(db.Integer, default=2)
    d_ff = db.Column(db.Integer, default=64)
    moving_avg = db.Column(db.Integer, default=24)
    factor = db.Column(db.Integer, default=4)
    activation = db.Column(
        db.Enum('relu', 'leaky_relu', 'elu', 'gelu', 'sigmoid', 'tanh', 'softplus', 'silu', 'none', name='act_type'),
        default='tanh', nullable=False)
    use_layer_norm = db.Column(db.Boolean, default=False)
    num_epochs = db.Column(db.Integer, default=150)
    learning_rate = db.Column(db.Float, default=0.0005)
    loss = db.Column(
        db.Enum('mse', 'mae', 'huber', 'smooth_l1', 'log_cosh', 'quantile', 'mape', 'smape', name='loss_type'),
        default='mae', nullable=False)

    # 关系定义：与Trainmodel一对一
    train_model = db.relationship(
        'Trainmodel',
        back_populates='training_params',
        uselist=False,  # 一对一关键：禁用列表，只允许单个关联对象
        cascade='all, delete-orphan'  # 删除参数时，级联删除关联的模型
    )

    # 关系定义：与Lossimagemodel一对一
    loss_image_model = db.relationship(
        'Lossimagemodel',
        back_populates='training_params',
        uselist=False,  # 一对一关键：禁用列表
        cascade='all, delete-orphan'
    )


# 存放保存的模型
class Trainmodel(db.Model):
    __tablename__ = 'trainmodel'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_name = db.Column(db.String(100), comment="存放文件名")
    trainepoch_path = db.Column(db.String(512), nullable=True, comment="训练周期数据文件路径")
    avg_val_loss = db.Column(db.String(100), comment="存放损失")
    avg_train_loss = db.Column(db.String(100), comment="存放损失")
    filepicture_name = db.Column(db.String(100), comment="存放损失图片名")
    filepicture_path = db.Column(db.String(512), nullable=True, comment="损失图片文件路径")
    modelname = db.Column(db.String(100), default='自定义分类模型')
    batch_number = db.Column(db.Integer, nullable=False, comment="模型所属批次（第几批）")

    # 2. 添加外键：关联Trainingparameters（一对一关键）
    training_params_id = db.Column(
        db.Integer,
        db.ForeignKey('trainingparameters.id'),
        unique=True,  # 唯一约束：确保一个参数只对应一个Trainmodel
        nullable=False
    )

    # 关系定义：反向关联Trainingparameters
    training_params = db.relationship(
        'Trainingparameters',
        back_populates='train_model',
        uselist=False
    )

    # 原有方法保持不变
    def _get_storage_dir(self, subdir='models'):
        storage_dir = os.path.join(current_app.root_path, 'uploads', str(self.user_id), subdir)
        os.makedirs(storage_dir, exist_ok=True)
        return storage_dir

    def save_trainepoch(self, data):
        if self.trainepoch_path:
            real_old = resolve_content_path(self.trainepoch_path)
            if real_old and os.path.exists(real_old):
                try:
                    os.remove(real_old)
                except Exception:
                    pass
        dir_path = self._get_storage_dir('trainepoch')
        filename = f"trainepoch_{uuid.uuid4().hex[:12]}.pkl.gz"
        file_path = os.path.join(dir_path, filename)
        with gzip.open(file_path, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        self.trainepoch_path = to_relative_content_path(file_path)
        return file_path

    def save_picture(self, image_data, file_ext='png'):
        if self.filepicture_path:
            real_old = resolve_content_path(self.filepicture_path)
            if real_old and os.path.exists(real_old):
                try:
                    os.remove(real_old)
                except Exception:
                    pass
        dir_path = self._get_storage_dir('pictures')
        filename = f"picture_{uuid.uuid4().hex[:12]}.{file_ext}"
        file_path = os.path.join(dir_path, filename)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        self.filepicture_path = to_relative_content_path(file_path)
        return file_path

    def delete_files(self):
        if self.trainepoch_path:
            real_path = resolve_content_path(self.trainepoch_path)
            if real_path and os.path.exists(real_path):
                try:
                    os.remove(real_path)
                except Exception:
                    pass
            self.trainepoch_path = None
        if self.filepicture_path:
            real_path = resolve_content_path(self.filepicture_path)
            if real_path and os.path.exists(real_path):
                try:
                    os.remove(real_path)
                except Exception:
                    pass
            self.filepicture_path = None


# 存放最后得到的损失图和模型
class Lossimagemodel(db.Model):
    __tablename__ = 'lossimagemodel'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), comment="图片文件名，用于区分")
    file_path = db.Column(db.String(512), nullable=True, comment="图片文件路径")
    trainname = db.Column(db.String(100), comment="模型名")
    trainepoch_path = db.Column(db.String(512), nullable=True, comment="训练周期数据文件路径")
    zxl_loss = db.Column(db.String(100), comment="总训练损失")
    zyz_loss = db.Column(db.String(100), comment="总验证损失")
    modelname = db.Column(db.String(100), default='自定义分类模型')
    batch_number = db.Column(db.Integer, nullable=False, comment="图片所属批次（第几批）")

    # 3. 添加外键：关联Trainingparameters（一对一关键）
    training_params_id = db.Column(
        db.Integer,
        db.ForeignKey('trainingparameters.id'),
        unique=True,  # 唯一约束：确保一个参数只对应一个Lossimagemodel
        nullable=False
    )

    # 关系定义：反向关联Trainingparameters
    training_params = db.relationship(
        'Trainingparameters',
        back_populates='loss_image_model',
        uselist=False
    )

    # 原有方法保持不变
    def _get_storage_dir(self, subdir='loss_images'):
        storage_dir = os.path.join(current_app.root_path, 'uploads', str(self.user_id), subdir)
        os.makedirs(storage_dir, exist_ok=True)
        return storage_dir

    def save_image(self, image_data, file_ext='png'):
        import uuid
        if self.file_path:
            real_old = resolve_content_path(self.file_path)
            if real_old and os.path.exists(real_old):
                try:
                    os.remove(real_old)
                except Exception:
                    pass
        dir_path = self._get_storage_dir()
        filename = f"loss_image_{uuid.uuid4().hex[:12]}.{file_ext}"
        file_path = os.path.join(dir_path, filename)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        self.file_path = to_relative_content_path(file_path)
        return file_path

    def save_trainepoch(self, data):
        if self.trainepoch_path:
            real_old = resolve_content_path(self.trainepoch_path)
            if real_old and os.path.exists(real_old):
                try:
                    os.remove(real_old)
                except Exception:
                    pass
        dir_path = self._get_storage_dir('trainepoch')
        filename = f"trainepoch_{uuid.uuid4().hex[:12]}.pkl.gz"
        file_path = os.path.join(dir_path, filename)
        with gzip.open(file_path, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        self.trainepoch_path = to_relative_content_path(file_path)
        return file_path

    def delete_files(self):
        if self.file_path:
            real_path = resolve_content_path(self.file_path)
            if real_path and os.path.exists(real_path):
                try:
                    os.remove(real_path)
                except Exception:
                    pass
            self.file_path = None
        if self.trainepoch_path:
            real_path = resolve_content_path(self.trainepoch_path)
            if real_path and os.path.exists(real_path):
                try:
                    os.remove(real_path)
                except Exception:
                    pass
            self.trainepoch_path = None


# 误差表
class Errtab(db.Model):
    __tablename__ = 'errtabs'  # 建议添加表名（可选，但规范）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), unique=True, nullable=False)
    MSE = db.Column(db.Float)
    MAE = db.Column(db.Float)
    RMSE = db.Column(db.Float)
    R2 = db.Column(db.Float)
    file = db.relationship('File', back_populates='errtab')
    # user = db.relationship('User', backref=db.backref('errtabs', lazy=True))





# 智能公式存储模型（新增 config_params 字段）
class Smartformula(db.Model):
    __tablename__ = 'smartformula'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 存储图片路径（原有字段不变）
    file_name = db.Column(db.String(100), comment="预测对比图文件名，用于区分")
    file_path = db.Column(db.String(512), nullable=True, comment="预测对比图文件路径")
    formula_name = db.Column(db.String(100), comment="公式图片文件名，用于区分")
    formula_path = db.Column(db.String(512), nullable=True, comment="公式图片文件路径")

    # 存放坐标数据（原有字段不变）
    coordinate = db.Column(JSON, comment="真实值与预测值坐标数据")

    # 每级最优指标（原有字段不变）
    index = db.Column(db.String(255))
    complexity = db.Column(db.String(255))
    loss = db.Column(db.String(255))
    score = db.Column(db.String(255))
    r2 = db.Column(db.String(255))
    mae = db.Column(db.String(255))
    mse = db.Column(db.String(255))
    rmse = db.Column(db.String(255))
    latex = db.Column(db.String(255))

    # 逐级指标（原有字段不变）
    indexb = db.Column(db.String(255))
    complexityb = db.Column(db.String(255))
    lossb = db.Column(db.String(255))
    scoreb = db.Column(db.String(255))
    r2b = db.Column(db.String(255))
    maeb = db.Column(db.String(255))
    mseb = db.Column(db.String(255))
    rmseb = db.Column(db.String(255))
    latexb = db.Column(db.String(255))

    # 批次管理（原有字段不变）
    batch_number = db.Column(db.Integer, nullable=False, default=1, comment="图片所属批次（第几批）")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, comment="创建时间")

    # ---------------- 新增字段：存储前端完整配置参数 ----------------
    config_params = db.Column(JSON, nullable=True, comment="前端传来的完整配置参数（JSON格式）")

    # 原有方法（不变）
    def _get_storage_dir(self, subdir='formula_plots'):
        storage_dir = os.path.join(current_app.root_path, 'uploads', str(self.user_id), subdir)
        os.makedirs(storage_dir, exist_ok=True)
        return storage_dir

    def save_prediction_plot(self, image_data, file_ext='png'):
        if self.file_path:
            real_old = resolve_content_path(self.file_path)
            if real_old and os.path.exists(real_old):
                try:
                    os.remove(real_old)
                except Exception:
                    pass
        dir_path = self._get_storage_dir('prediction_plots')
        filename = f"prediction_{uuid.uuid4().hex[:12]}.{file_ext}"
        file_path = os.path.join(dir_path, filename)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        self.file_name = filename
        self.file_path = to_relative_content_path(file_path)
        return file_path

    def save_formula_image(self, image_data, file_ext='png'):
        if self.formula_path:
            real_old = resolve_content_path(self.formula_path)
            if real_old and os.path.exists(real_old):
                try:
                    os.remove(real_old)
                except Exception:
                    pass
        dir_path = self._get_storage_dir('formula_images')
        filename = f"formula_{uuid.uuid4().hex[:12]}.{file_ext}"
        file_path = os.path.join(dir_path, filename)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        self.formula_name = filename
        self.formula_path = to_relative_content_path(file_path)
        return file_path

    def delete_files(self):
        if self.file_path:
            real_path = resolve_content_path(self.file_path)
            if real_path and os.path.exists(real_path):
                try:
                    os.remove(real_path)
                except Exception:
                    pass
            self.file_path = None
            self.file_name = None
        if self.formula_path:
            real_path = resolve_content_path(self.formula_path)
            if real_path and os.path.exists(real_path):
                try:
                    os.remove(real_path)
                except Exception:
                    pass
            self.formula_path = None
            self.formula_name = None
