import torch
import torch.nn as nn

from models_lib.model_tools import get_activation_fn


class Chomp1d(nn.Module):
    def __init__(self, padding):
        super(Chomp1d, self).__init__()
        self.padding = padding

    def forward(self, x):
        return x[:, :, :-self.padding]

class TemporalBlock(nn.Module):
    def __init__(self, n_inputs, n_outputs, kernel_size, stride, dilation, padding, args):
        super(TemporalBlock, self).__init__()
        activation = get_activation_fn(args.activation)
        norm_layer = nn.LayerNorm if args.use_layer_norm else nn.BatchNorm1d

        self.conv1 = nn.Conv1d(n_inputs, n_outputs, kernel_size,
                               stride=stride, padding=padding, dilation=dilation)
        self.chomp1 = Chomp1d(padding)
        self.norm1 = norm_layer(n_outputs)
        self.activation1 = activation
        self.dropout1 = nn.Dropout(args.dropout)

        self.conv2 = nn.Conv1d(n_outputs, n_outputs, kernel_size,
                               stride=stride, padding=padding, dilation=dilation)
        self.chomp2 = Chomp1d(padding)
        self.norm2 = norm_layer(n_outputs)
        self.activation2 = activation
        self.dropout2 = nn.Dropout(args.dropout)

        self.net = nn.Sequential(
            self.conv1, self.chomp1,
            self.norm1,
            self.activation1,
            self.dropout1,
            self.conv2, self.chomp2,
            self.norm2,
            self.activation2,
            self.dropout2
        )
        self.downsample = nn.Conv1d(n_inputs, n_outputs, 1) if n_inputs != n_outputs else nn.Identity()
        self.final_act = activation

    def forward(self, x):
        out = self.net(x)
        res = self.downsample(x)
        return self.final_act(out + res)

class TemporalConvNet(nn.Module):
    def __init__(self, args):
        super(TemporalConvNet, self).__init__()
        num_inputs = args.input_size
        num_outputs = args.output_size
        num_channels = args.num_channels
        kernel_size = args.kernel_size

        layers = []
        num_levels = len(num_channels)
        for i in range(num_levels):
            dilation_size = 2 ** i
            in_channels = num_inputs if i == 0 else num_channels[i - 1]
            out_channels = num_channels[i]
            padding = (kernel_size - 1) * dilation_size
            layers += [TemporalBlock(in_channels, out_channels, kernel_size,
                                     stride=1, dilation=dilation_size, padding=padding, args=args)]

        self.network = nn.Sequential(*layers)
        self.fc = nn.Linear(num_channels[-1], num_outputs)

    def forward(self, x):
        x = x.transpose(1, 2)  # [B, D, T]
        x = self.network(x)
        x = x[:, :, -1]  # 取最后一个时间步
        x = self.fc(x)
        return x.reshape(-1,)