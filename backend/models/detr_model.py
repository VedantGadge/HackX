import torch
from torch import nn
from torchvision.models import resnet50, ResNet50_Weights
import sys 
from colorama import Fore 
from utils.logger import get_logger
from utils.rich_handlers import ModelHandler
from torchinfo import summary
import sys 
import math


def _get_1d_sincos_pos_embed(length: int, dim: int, temperature: float = 10000.0, device=None):
    assert dim % 2 == 0
    position = torch.arange(length, device=device, dtype=torch.float32).unsqueeze(1)
    div_term = torch.exp(
        torch.arange(0, dim, 2, device=device, dtype=torch.float32) * (-math.log(temperature) / dim)
    )
    pe = torch.zeros(length, dim, device=device, dtype=torch.float32)
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    return pe


def build_2d_sincos_position_embedding(height: int, width: int, dim: int, device=None):
    """Create 2D sine-cos positional encoding of shape (1, H*W, dim)."""
    assert dim % 2 == 0, "positional dim must be even"
    dim_half = dim // 2
    pe_y = _get_1d_sincos_pos_embed(height, dim_half, device=device)
    pe_x = _get_1d_sincos_pos_embed(width, dim_half, device=device)
    pos = torch.zeros(height, width, dim, device=device, dtype=torch.float32)
    pos[:, :, :dim_half] = pe_y[:, None, :].expand(-1, width, -1)
    pos[:, :, dim_half:] = pe_x[None, :, :].expand(height, -1, -1)
    pos = pos.view(1, height * width, dim)
    return pos


class DETR(nn.Module):
    def __init__(self, num_classes, hidden_dim=256, nheads=8,
                 num_encoder_layers=1, num_decoder_layers=1, num_queries=25):
        super().__init__()
        
        try:
            self.logger = get_logger("model")
            self.model_handler = ModelHandler()
            
            model_config = {
                "Model Type": "DETR (Detection Transformer)",
                "Number of Classes": num_classes,
                "Hidden Dimension": hidden_dim,
                "Attention Heads": nheads,
                "Encoder Layers": num_encoder_layers,
                "Decoder Layers": num_decoder_layers,
                "Object Queries": num_queries,
                "Backbone": "ResNet-50 (ImageNet pretrained)"
            }
            self.model_handler.log_model_architecture(model_config)
        except:
            pass

        self.backbone = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        self.backbone.fc = nn.Identity()
        self.conv = nn.Conv2d(2048, hidden_dim, 1)
        
        self.transformer = nn.Transformer(
            hidden_dim, nheads, num_encoder_layers, num_decoder_layers, batch_first=True, dropout=0.1)

        self.linear_class = nn.Linear(hidden_dim, num_classes + 1)
        self.linear_bbox = nn.Linear(hidden_dim, 4)
        self.num_queries = num_queries
        self.query_pos = nn.Parameter(torch.randn(self.num_queries, hidden_dim))
        self.norm_src = nn.LayerNorm(hidden_dim)
        self.norm_tgt = nn.LayerNorm(hidden_dim)

    def forward(self, inputs):
        x = self.backbone.conv1(inputs)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        x = self.backbone.maxpool(x)
        x = self.backbone.layer1(x)
        x = self.backbone.layer2(x)
        x = self.backbone.layer3(x)
        x = self.backbone.layer4(x)
        
        h = self.conv(x)
        bs, C, H, W = h.shape
        h = h.flatten(2).permute(0, 2, 1)
        
        pos_embed = build_2d_sincos_position_embedding(H, W, C, device=h.device)
        pos_embed = pos_embed.expand(bs, -1, -1)
        
        src = self.norm_src(h + pos_embed)
        tgt = self.norm_tgt(self.query_pos.unsqueeze(0).expand(bs, -1, -1))
        
        h = self.transformer(src, tgt)
        
        return {'pred_logits': self.linear_class(h), 'pred_boxes': self.linear_bbox(h).sigmoid()}

    def load_pretrained(self, path):
        try:
            self.load_state_dict(torch.load(path, map_location='cpu'))
            print(f"✅ Loaded pretrained weights from {path}")
        except Exception as e:
            print(f"❌ Failed to load pretrained weights: {e}")
