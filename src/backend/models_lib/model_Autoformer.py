import torch
import torch.nn as nn
from models_lib.AutoCorrelation import AutoCorrelation, AutoCorrelationLayer
from models_lib.Autoformer_EncDec import EncoderLayer
from models_lib.model_tools import get_activation_fn


class Autoformer_EncoderOnly(nn.Module):
    def __init__(self, args):
        super(Autoformer_EncoderOnly, self).__init__()
        self.seq_len = args.seq_len
        self.output_dim = args.output_size
        self.d_model = args.hidden_size

        activation = get_activation_fn(args.activation)
        use_ln = args.use_layer_norm

        # === Embedding ===
        self.enc_embedding = nn.Sequential(
            nn.Linear(args.input_size, self.d_model),
            nn.LayerNorm(self.d_model) if use_ln else nn.Identity(),
            nn.Dropout(args.dropout)
        )

        # === 输入特征残差投影 ===
        self.input_proj = nn.Sequential(
            nn.Linear(args.input_size * args.seq_len, args.hidden_space),
            activation,
            nn.LayerNorm(args.hidden_space) if use_ln else nn.Identity()
        )

        # === Encoder 层堆叠 ===
        self.encoder_layers = nn.ModuleList([
            EncoderLayer(
                AutoCorrelationLayer(
                    AutoCorrelation(False, args.factor, attention_dropout=args.dropout, output_attention=False),
                    self.d_model, args.num_heads
                ),
                self.d_model,
                args.d_ff,
                moving_avg=args.moving_avg,
                dropout=args.dropout,
                activation=args.activation  # 注意：这里传的是字符串，由 EncoderLayer 自行处理
            )
            for _ in range(args.e_layers)
        ])

        # === 拼接输出 + 残差 MLP 投影 ===
        self.total_d_model = args.e_layers * self.d_model + args.hidden_space
        self.residual_projector = nn.Sequential(
            nn.Linear(self.total_d_model, args.hidden_space),
            activation,
            nn.LayerNorm(args.hidden_space) if use_ln else nn.Identity(),
            nn.Linear(args.hidden_space, self.output_dim)
        )

    def forward(self, x_enc):
        B, L, C = x_enc.shape

        # 轻量嵌入
        enc_out = self.enc_embedding(x_enc)

        # Encoder 层堆叠
        layer_outputs = []
        for layer in self.encoder_layers:
            enc_out, _ = layer(enc_out, attn_mask=None)
            layer_outputs.append(enc_out)

        # 拼接所有 Encoder 输出
        concat_out = torch.cat(layer_outputs, dim=-1)  # [B, L, d_model * N]
        pooled_out = concat_out[:, -1, :]              # 可替换为 mean(dim=1)

        # 残差输入投影
        input_flat = x_enc.reshape(B, -1)
        input_embed = self.input_proj(input_flat)

        # 拼接 & 投影
        final_rep = torch.cat([pooled_out, input_embed], dim=-1)
        out = self.residual_projector(final_rep)
        return out.squeeze(-1)
