import torch
from torch import nn

from models_lib.model_tools import get_activation_fn


class BiLSTM(nn.Module):
    def __init__(self, args):
        super(BiLSTM, self).__init__()
        self.hidden_dim = args.hidden_size
        self.num_layers = args.num_layers
        input_dim = args.input_size
        output_dim = args.output_size

        # BiLSTM -> 双向LSTM隐藏层维度为2倍
        self.lstm = nn.LSTM(input_dim, self.hidden_dim, self.num_layers,
                            batch_first=True, bidirectional=True)

        # 归一化方式（作用于输出层的拼接维度）
        if args.use_layer_norm:
            self.norm = nn.LayerNorm(self.hidden_dim * 2)
        else:
            self.norm = nn.Identity()

        self.dropout = nn.Dropout(args.dropout)
        self.activation = get_activation_fn(args.activation)
        self.fc = nn.Linear(self.hidden_dim * 2, output_dim)

    def forward(self, x):
        device = x.device
        h0 = torch.zeros(self.num_layers * 2, x.size(0), self.hidden_dim).to(device)
        c0 = torch.zeros(self.num_layers * 2, x.size(0), self.hidden_dim).to(device)

        out, _ = self.lstm(x, (h0, c0))  # out: [B, T, 2*H]
        out = out[:, -1, :]              # 取最后时间步的双向拼接输出 [B, 2*H]
        out = self.norm(out)
        out = self.dropout(out)
        out = self.fc(out)
        out = self.activation(out)
        return out.reshape(-1,)


