import copy
import torch
import os
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
    Edited TransformerDecoderLayer implementation omitting the redundant self-attention operation.
    """
    def __init__(self, d_model, nhead, dim_feedforward, dropout, activation):
        super(SPOTERTransformerDecoderLayer, self).__init__(d_model, nhead, dim_feedforward, dropout, activation)
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
    """
    SPOTER architecture for sign recognition from skeletal data.
    """
    def __init__(self, num_classes, hidden_dim, max_frame, num_heads, encoder_layers, decoder_layers):
        super().__init__()
        self.input_projection = nn.Linear(max_frame * 33 * 3, hidden_dim)

        self.row_embed = nn.Parameter(torch.rand(50, hidden_dim))
        self.pos = nn.Parameter(torch.cat([self.row_embed[0].unsqueeze(0).repeat(1, 1, 1)], dim=-1).flatten(0, 1).unsqueeze(0))
        self.class_query = nn.Parameter(torch.rand(1, hidden_dim))
        self.transformer = nn.Transformer(
            d_model=hidden_dim,
            nhead=num_heads,
            num_encoder_layers=encoder_layers,
            num_decoder_layers=decoder_layers
        )
        self.linear_class = nn.Linear(hidden_dim, num_classes)

        custom_decoder_layer = SPOTERTransformerDecoderLayer(
            self.transformer.d_model, self.transformer.nhead, 2048, 0.1, "relu"
        )
        self.transformer.decoder.layers = _get_clones(custom_decoder_layer, self.transformer.decoder.num_layers)

    def forward(self, inputs):
        # Flatten to (batch_size, 9900)
        h = inputs.flatten(start_dim=1)
        # Project to hidden_dim
        h = self.input_projection(h)
        h = h.unsqueeze(1).float()  # (batch_size, 1, hidden_dim)
        h = h.permute(1, 0, 2)      # (1, batch_size, hidden_dim)

        # Prepare class query
        class_query = self.class_query.unsqueeze(1).repeat(1, h.shape[1], 1)
        h = self.transformer(h, class_query)
        h = h.squeeze(0)
        res = self.linear_class(h)
        return res

class YogaGCN(nn.Module):
    """
    Simple GCN-based model for yoga pose classification.
    """
    def __init__(self, in_channels=3, hidden_dim=128, num_classes=4):
        super(YogaGCN, self).__init__()
        self.conv1 = gnn.GCNConv(in_channels, hidden_dim)
        self.conv2 = gnn.GCNConv(hidden_dim, hidden_dim)
        self.conv3 = gnn.GCNConv(hidden_dim, hidden_dim)
        self.conv4 = gnn.GCNConv(hidden_dim, hidden_dim)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x, edge_index, batch):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index).relu()
        x = self.conv3(x, edge_index).relu()
        x = self.conv4(x, edge_index).relu()
        x = gnn.global_mean_pool(x, batch)
        x = self.fc(x)
        return x