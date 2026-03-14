import torch
import torch.nn as nn

from models_lib.model_tools import get_activation_fn


class LSTM(nn.Module):
    def __init__(self, args):
        super(LSTM, self).__init__()
        self.args = args
        self.hidden_size = args.hidden_size
        self.num_layers = args.num_layers

        self.lstm = nn.LSTM(args.input_size, args.hidden_size, args.num_layers, batch_first=True)
        self.fc = nn.Linear(args.hidden_size, args.output_size)

        # 动态构建模块
        self.activation = get_activation_fn(args.activation)

        if args.use_layer_norm:
            self.norm = nn.LayerNorm(args.hidden_size)
        else:
            self.norm = nn.Identity()

        self.dropout = nn.Dropout(args.dropout) if args.dropout > 0 else nn.Identity()

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = out[:, -1, :]  # 取最后一个时间步
        out = self.norm(out)
        out = self.dropout(out)
        out = self.fc(out)
        out = self.activation(out)
        return out.reshape(-1,)



import torch
import torch.nn as nn

class BPNetwork(nn.Module):
    def __init__(self, args):
        super(BPNetwork, self).__init__()
        hidden_size = args.hidden_size
        input_size = args.input_size
        output_size = args.output_size

        # 层定义
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc_out = nn.Linear(hidden_size, output_size)

        # 归一化方式选择：LayerNorm 或 BatchNorm 或 Identity
        if args.use_layer_norm:
            self.norm1 = nn.LayerNorm(hidden_size)
            self.norm2 = nn.LayerNorm(hidden_size)
            self.norm3 = nn.LayerNorm(hidden_size)
        else:
            self.norm1 = nn.Identity()
            self.norm2 = nn.Identity()
            self.norm3 = nn.Identity()

        # 激活函数与 dropout
        self.activation = get_activation_fn(args.activation)
        self.dropout = nn.Dropout(args.dropout) if args.dropout > 0 else nn.Identity()

    def forward(self, x):
        x = x[:, -1, :]  # 只取最后时间步，shape: (B, input_size)

        # 第一层
        x = self.fc1(x)
        x = self.norm1(x)
        x = self.activation(x)
        x = self.dropout(x)

        # 第二层
        x = self.fc2(x)
        x = self.norm2(x)
        x = self.activation(x)
        x = self.dropout(x)

        # 第三层（带残差）
        residual = x
        x = self.fc3(x)
        x = self.norm3(x)
        x = self.activation(x)
        x = x + residual
        x = self.dropout(x)

        # 输出层
        x = self.fc_out(x)
        return x.reshape(-1,)
