import torch
import torch.nn as nn
from models_lib.model_tools import get_activation_fn


def get_norm_layer(use_layer_norm, dim):
    return nn.LayerNorm(dim) if use_layer_norm else nn.Identity()

class TransformerModel(nn.Module):
    def __init__(self, args):
        super(TransformerModel, self).__init__()
        self.input_dim = args.input_size
        self.hidden_space = args.hidden_space
        self.num_layers = args.num_layers
        self.num_outputs = args.output_size
        self.num_heads = args.num_heads
        self.dropout_rate = args.dropout
        self.activation_fn = get_activation_fn(args.activation)
        self.norm = get_norm_layer(args.use_layer_norm, self.hidden_space)

        # Transformer 编码层
        transformer_layer = nn.TransformerEncoderLayer(
            d_model=self.hidden_space,
            nhead=self.num_heads,
            dropout=self.dropout_rate,
            dim_feedforward=4 * self.hidden_space,
            activation=torch.nn.functional.gelu,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(transformer_layer, num_layers=self.num_layers)

        # 线性输入投影
        self.input_projection = nn.Linear(self.input_dim, self.hidden_space)

        # 输出投影
        self.output_layer = nn.Linear(self.hidden_space, self.num_outputs)
        self.dropout = nn.Dropout(self.dropout_rate)

    def forward(self, x):
        # 输入形状 x: [B, T, D]（batch_first=True，无需 permute）
        x = self.input_projection(x)     # [B, T, hidden_space]
        x = self.norm(x)
        x = self.dropout(x)

        # Transformer 编码器
        x = self.encoder(x)              # [B, T, hidden_space]

        # 取最后一个时间步
        x = x[:, -1, :]                  # [B, hidden_space]
        x = self.output_layer(x)        # [B, output_size]

        out = x.reshape(-1, )
        if torch.isnan(out).any():
            print("⚠️ 输出中包含 NaN")
        return out



