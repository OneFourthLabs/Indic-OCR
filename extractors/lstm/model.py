import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable

class Classifier(nn.Module):
  def __init__(self, embed_dim, hidden_dim, label_size, num_layers=3, dropout=0.2):
    super(Classifier, self).__init__()
    self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=num_layers,
                        dropout=dropout, bidirectional=True, batch_first=True)
    self.hidden2label = nn.Linear(hidden_dim*2, label_size)

    self.lstm_layers = num_layers
    self.hidden_dim = hidden_dim

  def forward(self, inputs, device):
    inputs = inputs.float()
    self.hidden = self.init_hidden(inputs.size()[0], device)
    lstm_out, self.hidden = self.lstm(inputs, self.hidden)
    y = self.hidden2label(lstm_out)
    return y

  def init_hidden(self, batch_size, device):
    h0 = Variable(torch.zeros(2*self.lstm_layers,
                              batch_size, self.hidden_dim).to(device))
    c0 = Variable(torch.zeros(2*self.lstm_layers,
                              batch_size, self.hidden_dim).to(device))
    return (h0, c0)
