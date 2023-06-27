from torch import nn
from torch_geometric.nn import GATv2Conv
import torch.nn.functional as F


class GAT(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()

        # self.conv1 = GATv2Conv(in_channels, 8, heads=8, dropout=0.6)
        # self.conv2 = GATv2Conv(8 * 8, out_channels, heads=1, concat=False,
        #                        dropout=0.6)
        self.conv1 = GATv2Conv(in_channels, 4, heads=4, dropout=0.6, add_self_loops=False)
        self.conv2 = GATv2Conv(4 * 4, out_channels, heads=1, concat=False, add_self_loops=False,
                               dropout=0.6)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x, edge_index):
        x = F.dropout(x, p=0.6, training=self.training)
        out = self.conv1(x, edge_index)
        # print(f"\nconv1 0 : {out[0][:5]}")
        # print(f"conv1 1 : {out[1][:5]}")
        x = F.elu(out)
        # x = F.dropout(x, p=0.6, training=self.training)
        x = self.conv2(x, edge_index)
        # print(f"conv2 0 : {x[0][:5]}")
        # print(f"conv2 1 : {x[0][:5]}")
        return self.sigmoid(x)
        # return x
        # return F.log_softmax(x, dim=1)