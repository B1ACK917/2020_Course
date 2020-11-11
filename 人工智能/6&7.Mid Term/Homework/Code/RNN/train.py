import argparse
import os
from utils import CRF, FocalLoss, F1Score
import dataloader

import torch
import numpy
import torch.optim as optim
import torch.nn.functional

parser = argparse.ArgumentParser()
parser.add_argument('--learningrate', '-lr', type=float, default=1e-5, help='Learning rate')
parser.add_argument('--iteration', '-i', type=int, default=100, help='Training Epoch')
parser.add_argument('--save_ite', '-s', type=int, default=10, help='How many epoch to save model')
parser.add_argument('--load', action='store_true', default=False, help='load model')

args = parser.parse_args()

input_dim = 300
cell_dim = 1024
output_dim = 2
lr = None
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model_save_path = 'model/'


class LSTM(torch.nn.Module):  # input_dim cell_dim
    global input_dim, cell_dim, output_dim

    def __init__(self):
        super(LSTM, self).__init__()
        self.f = torch.nn.Sequential(
            torch.nn.Linear(input_dim + cell_dim, cell_dim),
            torch.nn.Sigmoid()
        )
        self.ts = torch.nn.Sequential(
            torch.nn.Linear(input_dim + cell_dim, cell_dim),
            torch.nn.Sigmoid()
        )
        self.tt = torch.nn.Sequential(
            torch.nn.Linear(input_dim + cell_dim, cell_dim),
            torch.nn.Tanh()
        )
        self.os = torch.nn.Sequential(
            torch.nn.Linear(input_dim + cell_dim, cell_dim),
            torch.nn.Sigmoid()
        )
        self.ot = torch.nn.Sequential(
            torch.nn.Linear(cell_dim, cell_dim),
            torch.nn.Tanh()
        )

    def forward(self, X, h, c):
        a = []
        for x in X:
            tmp = torch.cat((x.float(), h), -1)
            c = torch.add(
                torch.mul(self.f(tmp), c),
                torch.mul(self.ts(tmp), self.tt(tmp))
            )
            h = torch.mul(self.os(tmp), self.ot(c))
            a.append(h.reshape((1, cell_dim)))
        return torch.cat(a)


class BILSTM(torch.nn.Module):  # input_dim cell_dim
    global input_dim, cell_dim, output_dim, trans

    def __init__(self):
        super(BILSTM, self).__init__()
        self.LSTM = torch.nn.LSTM(input_size=input_dim, hidden_size=output_dim, num_layers=1, bidirectional=True,
                                  batch_first=True)
        self.l = torch.nn.Linear(2 * output_dim, output_dim)
        self.o = torch.nn.Softmax()

    def forward(self, X):
        opt = self.LSTM(X.reshape(1, X.shape[0], X.shape[1]).float())
        return self.o(self.l(opt[0][0])).reshape(-1, output_dim)


net = BILSTM().to(device)


def train(Epoch, features, labels):
    loss_history = 0.0
    # features = features[:10]
    for i in range(len(features)):
        rfeature = numpy.flip(features[i], 0)
        feature = torch.from_numpy(features[i]).to(device)
        net.train()
        optimizer = optim.Adam(net.parameters(), lr=args.learningrate)
        optimizer.zero_grad()
        output = net(feature)
        label = torch.from_numpy(labels[i]).long().to(device).reshape((-1, 1))
        # loss_func = FocalLoss(2).to(device)
        # loss_train = loss_func(output, label)
        loss_func = CRF(output_dim).to(device)
        loss_train = -loss_func(output.reshape(output.shape[0], 1, -1), label.reshape(label.shape[0], -1))
        loss_train.backward()
        optimizer.step()
        loss_history += loss_train
    loss = loss_history / len(features)
    print('Epoch: {}, loss: {}'.format(Epoch, loss))
    return loss


def test(features, labels):
    accracy_history, f1_history = 0.0, 0.0
    # features = features[:10]
    for i in range(len(features)):
        feature = torch.from_numpy(features[i]).to(device)
        net.eval()
        output = net(feature)
        label = labels[i]
        f1, acc = F1Score(label, output)
        accracy_history += acc
        f1_history += f1
    accuracy = accracy_history / len(features)
    f1 = f1_history / len(features)
    print('Test accuracy: {},F1 Score: {}'.format(accuracy, f1))
    return f1, accuracy


def main(data_from_disk=False, model_from_disk=False):
    global net
    if not data_from_disk:
        a = dataloader.DataLoader()
        a.set(data_path='dataset/Laptops_Train.xml', vec_path='wordvec/glove.6B/glove.6B.300d.txt', fill_rule='random')
        x_train, y_train, x_test, y_test = a.load()
        numpy.save('dataset/x_train', x_train)
        numpy.save('dataset/y_train', y_train)
        numpy.save('dataset/x_test', x_test)
        numpy.save('dataset/y_test', y_test)
    else:
        x_train = numpy.load('dataset/x_train.npy', allow_pickle=True)
        y_train = numpy.load('dataset/y_train.npy', allow_pickle=True)
        x_test = numpy.load('dataset/x_test.npy', allow_pickle=True)
        y_test = numpy.load('dataset/y_test.npy', allow_pickle=True)
    print('Training start, using saved model: {}, max iteration: {}, save iteration: {}'.format(model_from_disk,
                                                                                                args.iteration,
                                                                                                args.save_ite))
    if not os.path.exists(model_save_path):
        os.mkdir(model_save_path)
    if model_from_disk:
        net = torch.load(model_save_path + 'BILSTM_2000').to(device)
        test(x_test, y_test)
    loss_train = []
    for i in range(1, args.iteration + 1):
        loss = train(i, x_train, y_train)
        loss_train.append(loss.tolist())
        if not i % args.save_ite:
            torch.save(net, model_save_path + 'BILSTM_{}'.format(i))
            with open(model_save_path + 'loss.txt', 'w')as file:
                file.write('{}'.format(loss_train))
    torch.save(net, model_save_path + 'BILSTM_Final')
    accuracy_test, f1_test = test(x_test, y_test)
    with open(model_save_path + 'loss.txt', 'w')as file:
        file.write('{}\nTest accuracy: {}\nF1 Score: {}'.format(loss_train, accuracy_test, f1_test))


if __name__ == '__main__':
    # main(data_from_disk=True, model_from_disk=args.load)
    main(data_from_disk=True, model_from_disk=True)
