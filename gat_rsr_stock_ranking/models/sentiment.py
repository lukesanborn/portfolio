from torch import nn


class SentimentEncoding(nn.Module):
    def __init__(self, n_features, n_hidden=64, n_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=n_hidden,
            batch_first=True,
            num_layers=n_layers,
            dropout=0.2
        )
        self.regress = nn.Linear(n_hidden, 1)

    def forward(self, x):
        self.lstm.flatten_parameters()
        _, (hidden, _) = self.lstm(x)
        out = hidden[-1]
        return self.regress(out)