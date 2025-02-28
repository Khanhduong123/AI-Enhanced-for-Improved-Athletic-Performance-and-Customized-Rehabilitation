import copy
import torch

import torch.nn as nn
from typing import Optional
from dataclasses import dataclass
from torch import Tensor
import torch_geometric.nn as gnn

def _get_clones(mod, n):
    return nn.ModuleList([copy.deepcopy(mod) for _ in range(n)])

# @dataclass
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
    def __init__(self, num_classes, hidden_dim):
        """
        Implementation of the SPOTER (Sign POse-based TransformER) architecture for sign language recognition from sequence
        of skeletal data.
        """
        super().__init__()

        self.input_projection = nn.Linear(100 * 33 * 3, hidden_dim)  # 9900 → 54

        self.row_embed = nn.Parameter(torch.rand(50, hidden_dim))
        self.pos = nn.Parameter(torch.cat([self.row_embed[0].unsqueeze(0).repeat(1, 1, 1)], dim=-1).flatten(0, 1).unsqueeze(0))
        self.class_query = nn.Parameter(torch.rand(1, hidden_dim))
        self.transformer = nn.Transformer(hidden_dim, 9, 6, 6) #hidden_dim, num_heads, layer_encoder, layer_decoder
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
    def __init__(self, in_channels=3, hidden_dim=64, num_classes=4):
        super(YogaGCN, self).__init__()
        self.conv1 = gnn.GCNConv(in_channels, hidden_dim)
        self.conv2 = gnn.GCNConv(hidden_dim, hidden_dim)
        self.conv3 = gnn.GCNConv(hidden_dim, hidden_dim)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x, edge_index, batch):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index).relu()
        x = self.conv3(x, edge_index).relu()

        # Pooling giữ đúng batch_size
        x = gnn.global_mean_pool(x, batch)  # (batch_size, hidden_dim)

        x = self.fc(x)  # (batch_size, num_classes)
        return x
   

def model(cf):
    if cf.model_name == 'spoter':
        return SPOTER(cf.num_classes, cf.hidden_dim)
    else:
        pass