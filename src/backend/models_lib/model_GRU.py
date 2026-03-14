import torch
import torch.nn as nn

from models_lib.model_tools import get_activation_fn


class GRU(nn.Module):
    def __init__(self, args):
        super(GRU, self).__init__()
        self.hidden_dim = args.hidden_size
        self.num_layers = args.num_layers

        # 动态归一化层
        if args.use_layer_norm:
            self.norm = nn.LayerNorm(self.hidden_dim)
        else:
            self.norm = nn.Identity()

        self.dropout = nn.Dropout(args.dropout)
        self.activation = get_activation_fn(args.activation)

        self.gru = nn.GRU(args.input_size, self.hidden_dim, self.num_layers, batch_first=True)
        self.fc = nn.Linear(self.hidden_dim, args.output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device).requires_grad_()
        out, _ = self.gru(x, h0)
        out = out[:, -1, :]  # 最后一个时间步
        out = self.norm(out)
        out = self.dropout(out)
        out = self.fc(out)
        out = self.activation(out)
        return out.reshape(-1,)
