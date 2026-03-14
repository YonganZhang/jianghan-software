import torch.nn as nn
from models_lib.model_KAN import KAN
from models_lib.model_tools import get_activation_fn


# 归一化层选择器
def get_norm_layer(use_layer_norm, dim):
    return nn.LayerNorm(dim) if use_layer_norm else nn.Identity()

class TimeSeriesTransformer_ekan(nn.Module):
    def __init__(self, args):
        super(TimeSeriesTransformer_ekan, self).__init__()
        self.input_dim = args.input_size
        self.num_heads = args.num_heads
        self.num_layers = args.num_layers
        self.num_outputs = args.output_size
        self.hidden_space = args.hidden_space
        self.dropout_rate = args.dropout
        self.activation = get_activation_fn(args.activation)
        self.use_layer_norm = args.use_layer_norm

        # Transformer Encoder Layer
        transformer_layer = nn.TransformerEncoderLayer(
            d_model=self.hidden_space,
            nhead=self.num_heads,
            dim_feedforward=4 * self.hidden_space,
            dropout=self.dropout_rate,
            activation=args.activation  # 注意这里传字符串即可
        )
        self.transformer_encoder = nn.TransformerEncoder(transformer_layer, num_layers=self.num_layers)

        # 线性变换输入维度
        self.input_projection = nn.Linear(self.input_dim, self.hidden_space)
        self.norm = get_norm_layer(self.use_layer_norm, self.hidden_space)
        self.dropout = nn.Dropout(self.dropout_rate)

        # 输出层：EKAN 模块
        self.e_kan = KAN([self.hidden_space, 10, self.num_outputs])

    def forward(self, x):
        # x: [B, T, D]
        x = x.permute(1, 0, 2)  # -> [T, B, D]
        x = self.input_projection(x)  # -> [T, B, hidden_space]
        x = self.norm(x)
        x = self.dropout(x)

        # Transformer 编码器
        x = self.transformer_encoder(x)  # -> [T, B, hidden_space]
        x = x[-1]  # 取最后一个时间步 [B, hidden_space]

        out = self.e_kan(x)
        return out.reshape(-1,)


