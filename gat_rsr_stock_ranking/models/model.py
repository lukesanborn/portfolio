from typing import Optional, Dict

import torch
from torch import nn, optim
from torchmetrics import MetricCollection, Accuracy, F1Score, MatthewsCorrCoef, Precision

import pytorch_lightning as pl

from src.models.components.gat import GAT
from src.models.components.sentiment import SentimentEncoding
from src.models.components.technical import TechnicalEncoding


class RSR(pl.LightningModule):
    def __init__(self, conf: Optional[Dict] = None):
        super().__init__()
        self.save_hyperparameters(conf)

        self.TechnicalEncoding = TechnicalEncoding(n_features=self.hparams["TechnicalEncodingIn"], n_hidden=128,
                                                   n_layers=2)
        self.SentimentEncoding = SentimentEncoding(n_features=self.hparams["SentimentEncodingIn"], n_hidden=128,
                                                   n_layers=2)
        # self.BilinearTransformer = BilinearTransformer()
        self.GAT = GAT(in_channels=self.hparams["GATIn"], out_channels=self.hparams["GATOut"])

        metrics = MetricCollection([
            Accuracy(num_classes=self.hparams['Classes']),
            F1Score(num_classes=self.hparams['Classes']),
            MatthewsCorrCoef(num_classes=2),
            Precision(num_classes=self.hparams['Classes']),
        ])
        self.train_metrics = metrics.clone(prefix='train_')
        self.val_metrics = metrics.clone(prefix='val_')
        self.test_metrics = metrics.clone(prefix='test_')
        # self.test_backtest = Backtesting(hold_time=self.hparams["Hold"], percent_portfolio=self.hparams["Percent"],top_n=self.hparams["Buy_Top_N"],
        #                                  report=False)
        self.criterion = nn.BCELoss()

    def forward(self, batch):
        technical = self.TechnicalEncoding(batch.technical)
        sentiment = self.SentimentEncoding(batch.sentiment)
        features = torch.cat([technical, sentiment], dim=-1)
        out = self.GAT(features, batch.edge_index).squeeze()
        return out

    def shared_step(self, batch):
        # print(batch.num_nodes)
        technical = self.TechnicalEncoding(batch.technical)
        sentiment = self.SentimentEncoding(batch.sentiment)
        # print(f"{sentiment[0]=}")
        # print(f"{sentiment.shape=}")
        # features = self.BilinearTransformer(technical, sentiment)
        features = torch.cat([technical, sentiment], dim=-1)
        out = self.GAT(features, batch.edge_index).squeeze()
        # print(f"{out[:5]=}")
        # print(f"{out.shape=}")
        loss = self.criterion(out, batch.y)
        return loss, out
        # return loss, F.log_softmax(out, dim=-1)

    def training_step(self, batch, batch_idx):
        loss, out = self.shared_step(batch)
        target = batch.y.type(torch.LongTensor).to(self.device)
        self.log_dict(self.train_metrics(out, target))
        self.log("train_loss", loss)
        return loss

    def training_epoch_end(self, outputs) -> None:
        self.log_dict(self.train_metrics.compute())

    def validation_step(self, batch, batch_idx):
        loss, out = self.shared_step(batch)
        target = batch.y.type(torch.LongTensor).to(self.device)
        self.log_dict(self.val_metrics(out, target))
        self.log("val_loss", loss)
        return loss

    def validation_epoch_end(self, outputs) -> None:
        self.log_dict(self.val_metrics.compute())

        # scores = self._stack(outputs)
        # returns, _, _ = _calc_all_results(scores.cpu(), self.hparams["Hold"], self.hparams["Percent"])
        # self.logger.experiment['backtest/val_epoch/returns'].log(returns)

    def test_step(self, batch, batch_idx):
        loss, out = self.shared_step(batch)
        target = batch.y.type(torch.LongTensor).to(self.device)
        self.test_metrics(out, target)
        # self.test_backtest(out, batch.ticker, batch.date)
        self.log("test_loss", loss)
        # return {"loss": loss, "predictions": out.detach(), "batch_size": batch.num_graphs}
        return loss

    # @staticmethod
    # def _stack(outputs):
    #     list_tensor = []
    #     for x in outputs:
    #         if x['predictions'].shape[0] == 1:
    #             list_tensor.append(x['predictions'])
    #         else:
    #             correct_sized = torch.tensor_split(x['predictions'], x['batch_size'])
    #             for t in correct_sized:
    #                 list_tensor.append(t)
    #     return torch.stack(list_tensor)

    #
    def test_epoch_end(self, outputs):
        self.log_dict(self.test_metrics.compute())
        # self.log_dict(self.test_backtest.compute())
        # scores = self._stack(outputs)
        # print(scores)
        # returns, volatility = _calc_all_results(scores.cpu(), self.hparams["Hold"], self.hparams["Percent"])
        # self.logger.experiment['accuracy/test_epoch'].log(self.test_acc.compute())
        # self.logger.experiment['F1/test_epoch'].log(self.test_f1.compute())
        #
        # # self.logger.experiment['MCC/test_epoch'].log(self.test_mcc.compute())
        # self.logger.experiment['precision/test_epoch'].log(self.test_precision.compute())
        # # self.logger.experiment['backtest_img'].upload(File.as_image(fig))
        # self.logger.experiment['backtest/returns'].log(returns)
        # self.logger.experiment['backtest/sharpe'].log(volatility)

    def configure_optimizers(self):
        return optim.Adam(self.parameters(), lr=self.hparams.lr)