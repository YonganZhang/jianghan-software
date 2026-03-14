def get_activation_fn(name):
    import torch.nn as nn
    name = name.lower()
    if name == 'relu':
        return nn.ReLU()
    elif name == 'leaky_relu':
        return nn.LeakyReLU()
    elif name == 'elu':
        return nn.ELU()
    elif name == 'gelu':
        return nn.GELU()
    elif name == 'sigmoid':
        return nn.Sigmoid()
    elif name == 'tanh':
        return nn.Tanh()
    elif name == 'softplus':
        return nn.Softplus()
    elif name == 'silu':
        return nn.SiLU()
    elif name == 'none':
        return nn.Identity()
    else:
        raise ValueError(f"不支持的激活函数: {name}")
