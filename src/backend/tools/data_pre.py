import os
from tools.tool_for_pre import save_data_loaders, main, get_parameters

# model_factory.py
from models_lib.model_Autoformer import Autoformer_EncoderOnly
from models_lib.model_BiLSTM import BiLSTM
from models_lib.model_GRU import GRU
from models_lib.model_LSTM import LSTM, BPNetwork
from models_lib.model_TCN import TemporalConvNet
from models_lib.model_Trans_KAN import TimeSeriesTransformer_ekan
from models_lib.model_Transformer import TransformerModel

def get_model(args):
    model_name = getattr(args, "model_name", None)
    if model_name == 'GRU':
        return GRU(args)
    elif model_name == 'LSTM':
        return LSTM(args)
    elif model_name == 'BP':
        return BPNetwork(args)
    elif model_name == 'LSTM_my':
        return LSTM(args)
    elif model_name == 'BiLSTM':
        return BiLSTM(args)
    elif model_name == 'TCN':
        return TemporalConvNet(args)
    elif model_name == 'Transformer':
        return TransformerModel(args)
    elif model_name == 'Transformer_KAN':
        return TimeSeriesTransformer_ekan(args)
    elif model_name == 'TimeSeriesTransformer_ekan_large':
        return TimeSeriesTransformer_ekan(args)
    elif model_name in ('Autoformer', 'Autoformer_EncoderOnly'):
        return Autoformer_EncoderOnly(args)
    else:
        raise ValueError(f"未知模型名: {model_name}")

def data_pre_process(args):
    directory = args.input_directory  # 替换为你的目录路径
    target_column = args.predict_target  # 替换为你的目标列名称
    sequence_length = args.sequence_length  # 替换为你的时序数据长度
    batch_size = args.batch_size  # 替换为你的批次大小

    save_directory = os.path.join('../data_save', '本次数据读取的缓存', args.input_directory)
    train_loader, val_loader = main(directory, target_column, sequence_length, batch_size, save_directory, args=args)
    # 检查目录是否存在，不存在则创建
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    save_data_loaders(train_loader, val_loader, save_directory=save_directory)




if __name__ == "__main__":
    # 示例用法
    args = get_parameters(preset_path="../预设参数/预设参数.csv")
    data_pre_process(args)
