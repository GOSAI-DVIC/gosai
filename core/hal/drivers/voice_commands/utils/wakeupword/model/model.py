import torch
import torch.nn as nn


class LSTM(nn.Module):

    def __init__(self, device, num_classes=1, feature_size=40, hidden_size=32,
                num_layers=1, dropout=0.1, bidirectional=False):
        super(LSTM, self).__init__()
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.device = device 
        self.directions = 2 if bidirectional else 1
        self.layernorm = nn.LayerNorm(feature_size)
        self.lstm = nn.LSTM(input_size=feature_size, hidden_size=hidden_size,
                            num_layers=num_layers, dropout=dropout,
                            bidirectional=bidirectional)
        self.classifier = nn.Linear(hidden_size*self.directions, num_classes)
    def _init_hidden(self, batch_size):
        n, d, hs = self.num_layers, self.directions, self.hidden_size
        return (torch.zeros(n*d, batch_size, hs).to(self.device),
                torch.zeros(n*d, batch_size, hs).to(self.device))

    def forward(self, x):
        # x.shape => seq_len, batch, feature
        x = self.layernorm(x)

        hidden = self._init_hidden(x.size()[1])

        out, (hn, cn) = self.lstm(x, hidden)

        out = self.classifier(hn)


        return torch.sigmoid(out)