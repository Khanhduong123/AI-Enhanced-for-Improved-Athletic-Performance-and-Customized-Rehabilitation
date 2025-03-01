import copy
import torch
import os
import sys
import torch.nn as nn
from typing import Optional
from dataclasses import dataclass
from torch import Tensor
import torch_geometric.nn as gnn

def _get_clones(mod, n):
    return nn.ModuleList([copy.deepcopy(mod) for _ in range(n)])

class SelfAttention(nn.Module):
    batch_first: bool = True

class SPOTERTransformerDecoderLayer(nn.TransformerDecoderLayer):
    """
    Edited TransformerDecoderLayer implementation omitting the redundant self-attention operation as opposed to the
    standard implementation.
    """

    def __init__(self, d_model, nhead, dim_feedforward, dropout, activation):
        super(SPOTERTransformerDecoderLayer, self).__init__(d_model, nhead, dim_feedforward, dropout, activation)

        # del self.self_attn
        self.self_attn =  SelfAttention()

    def forward(
        self,
        tgt: Tensor,
        memory: Tensor,
        tgt_mask: Optional[Tensor] = None,
        memory_mask: Optional[Tensor] = None,
        tgt_key_padding_mask: Optional[Tensor] = None,
        memory_key_padding_mask: Optional[Tensor] = None,
        tgt_is_causal: bool = False,
        memory_is_causal: bool = False,
    ) -> torch.Tensor:

        tgt = tgt + self.dropout1(tgt)
        tgt = self.norm1(tgt)
        tgt2 = self.multihead_attn(tgt, memory, memory, attn_mask=memory_mask,
                                   key_padding_mask=memory_key_padding_mask)[0]
        tgt = tgt + self.dropout2(tgt2)
        tgt = self.norm2(tgt)
        tgt2 = self.linear2(self.dropout(self.activation(self.linear1(tgt))))
        tgt = tgt + self.dropout3(tgt2)
        tgt = self.norm3(tgt)
        return tgt


class SPOTER(nn.Module):
    def __init__(self, num_classes, hidden_dim,max_frame ,num_heads, encoder_layers, decoder_layers):
        """
        Implementation of the SPOTER (Sign POse-based TransformER) architecture for sign language recognition from sequence
        of skeletal data.
        """
        super().__init__()
        self.input_projection = nn.Linear(max_frame * 33 * 3, hidden_dim)  # 9900 → 54

        self.row_embed = nn.Parameter(torch.rand(50, hidden_dim))
        self.pos = nn.Parameter(torch.cat([self.row_embed[0].unsqueeze(0).repeat(1, 1, 1)], dim=-1).flatten(0, 1).unsqueeze(0))
        self.class_query = nn.Parameter(torch.rand(1, hidden_dim))
        self.transformer = nn.Transformer(hidden_dim, num_heads, encoder_layers, decoder_layers) #hidden_dim, num_heads, layer_encoder, layer_decoder
        self.linear_class = nn.Linear(hidden_dim, num_classes)

        custom_decoder_layer = SPOTERTransformerDecoderLayer(self.transformer.d_model, self.transformer.nhead, 2048, 0.1, "relu")
        self.transformer.decoder.layers = _get_clones(custom_decoder_layer, self.transformer.decoder.num_layers)

    def forward(self, inputs):
        h = inputs.flatten(start_dim=1)  # (batch_size, 9900)
        h = self.input_projection(h)     # (batch_size, hidden_dim=72)
        h = h.unsqueeze(1).float()       # (batch_size, 1, hidden_dim)  [Thêm 1 chiều sequence length]
        
        # Transformer yêu cầu input có shape (seq_len, batch_size, hidden_dim), nên ta cần hoán vị
        h = h.permute(1, 0, 2)  # (1, batch_size, hidden_dim)
        # Đảm bảo class_query có batch_size giống h
        class_query = self.class_query.unsqueeze(1).repeat(1, h.shape[1], 1)  # (1, batch_size, hidden_dim)
        # Đưa vào Transformer
        h = self.transformer(h, class_query)  # (1, batch_size, hidden_dim)
        h = h.squeeze(0)  # Chuyển về (batch_size, hidden_dim) để phù hợp với linear_class
        res = self.linear_class(h)  # (batch_size, num_classes)
        return res  # Trả về đúng shape: (batch_size, num_classes)


class YogaGCN(nn.Module):
    def __init__(self, in_channels=3, hidden_dim=128, num_classes=4):
        super(YogaGCN, self).__init__()
        self.conv1 = gnn.GCNConv(in_channels, hidden_dim)
        self.conv2 = gnn.GCNConv(hidden_dim, hidden_dim)
        self.conv3 = gnn.GCNConv(hidden_dim, hidden_dim)
        self.conv4 = gnn.GCNConv(hidden_dim, hidden_dim)  # Thêm một lớp nữa
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x, edge_index, batch):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index).relu()
        x = self.conv3(x, edge_index).relu()
        x = self.conv4(x, edge_index).relu()
        x = gnn.global_mean_pool(x, batch)
        x = self.fc(x)
        return x
   
def modify_model_for_finetune(model, cf):
    """
    Chỉnh sửa model khi fine-tune (is_pretrain == False), giữ nguyên feature extractor
    và chỉ thay đổi classification layer.
    """
    model_name = cf.get('model.model_name')
    checkpoint_path = os.path.join(os.getcwd(), "checkpoints", model_name, "pretrain", "best_checkpoint.pt")

    # Nếu checkpoint không tồn tại, bỏ qua việc load
    if not os.path.exists(checkpoint_path):
        print(f"❌ Không tìm thấy checkpoint tại {checkpoint_path}. Bỏ qua việc load pretrain.")
        return model

    print(f"Đang load pretrain từ {checkpoint_path}...")
    checkpoint = torch.load(checkpoint_path, map_location="cuda" if torch.cuda.is_available() else "cpu")
    state_dict = checkpoint['model']

    if model_name == "spoter":
        new_num_classes = int(cf.get('model.finetune_config.spoter.num_classes'))
        hidden_dim = int(cf.get('model.finetune_config.spoter.hidden_dim'))
        old_num_classes = state_dict["linear_class.weight"].shape[0]

        # Xóa lớp classification cũ
        state_dict.pop("linear_class.weight", None)
        state_dict.pop("linear_class.bias", None)

        # Load trọng số vào model
        model.load_state_dict(state_dict, strict=False)

        # Thay đổi classification layer
        model.linear_class = nn.Linear(hidden_dim, new_num_classes)
        nn.init.xavier_uniform_(model.linear_class.weight)
        model.linear_class.bias.data.zero_()

        print(f"SPOTER fine-tune: num_classes thay đổi từ {old_num_classes} → {new_num_classes}")

    elif model_name == "gcn":
        
        new_num_classes = int(cf.get('model.finetune_config.gcn.num_classes'))
        hidden_dim = int(cf.get('model.finetune_config.gcn.hidden_dim'))
        old_num_classes = state_dict["fc.weight"].shape[0]

        # Xóa lớp classification cũ
        state_dict.pop("fc.weight", None)
        state_dict.pop("fc.bias", None)

        # Load trọng số vào model
        model.load_state_dict(state_dict, strict=False)

        # Thay đổi classification layer
        model.fc = nn.Linear(model.fc.in_features, new_num_classes)
        nn.init.xavier_uniform_(model.fc.weight)
        model.fc.bias.data.zero_()

        print(f"GCN fine-tune: num_classes thay đổi từ {old_num_classes} → {new_num_classes}")

    return model



def get_model(cf):
    """
    Khởi tạo model dựa trên `cf.model_name` và `cf.pretrained`.
    Nếu không pretrain, tự động gọi `modify_model_for_finetune()`.
    """
    model_name = cf.get('model.model_name')
    is_pretrain = cf.get('model.pretrained')

    # Khởi tạo model
    if model_name == "spoter":
        model = SPOTER(
            num_classes=int(cf.get('model.pretrain_config.spoter.num_classes')), 
            hidden_dim=int(cf.get('model.pretrain_config.spoter.hidden_dim')),
            max_frame = int(cf.get('data.max_frame')),
            num_heads=int(cf.get('model.pretrain_config.spoter.num_heads')), 
            encoder_layers=int(cf.get('model.pretrain_config.spoter.encoder_layers')), 
            decoder_layers=int(cf.get('model.pretrain_config.spoter.decoder_layers'))
        )
    elif model_name == "gcn":
        model = YogaGCN(
            in_channels=int(cf.get('model.pretrain_config.gcn.in_channels')), 
            hidden_dim=int(cf.get('model.pretrain_config.gcn.hidden_dim')), 
            num_classes=int(cf.get('model.pretrain_config.gcn.num_classes'))
        )
    else:
        raise ValueError(f"Không tìm thấy model phù hợp: {model_name}")

    # Nếu không pretrain, sửa model để fine-tune
    if not is_pretrain:
        model = modify_model_for_finetune(model, cf)

    return model 