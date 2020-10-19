from dataLoader import dataLoader
from dataCutter import dataCutter
import numpy as np
import time


class MathFunc:
    class origin:
        @staticmethod
        def f(x: np.ndarray):
            return x

        @staticmethod
        def df(x: np.ndarray):
            return 1

    class sigmoid:
        @staticmethod
        def f(x: np.ndarray):
            return 1 / (1 + np.exp(-x))

        @staticmethod
        def df(x: np.ndarray):
            return MathFunc.sigmoid.f(x) * (1 - MathFunc.sigmoid.f(x))

    class tanh:
        @staticmethod
        def f(x: np.ndarray):
            return np.tanh(x)

        @staticmethod
        def df(x: np.ndarray):
            return 1 - np.tanh(x) ** 2

    class relu:
        @staticmethod
        def f(x: np.ndarray):
            for i in range(x.shape[0]):
                for j in range(x.shape[1]):
                    if x[i, j] <= 0:
                        x[i, j] = 0
            return x

        @staticmethod
        def df(x: np.ndarray):
            for i in range(x.shape[0]):
                for j in range(x.shape[1]):
                    if x[i, j] <= 0:
                        x[i, j] = 0
                    else:
                        x[i, j] = 1
            return x

    class mse:
        @staticmethod
        def f(y, p):
            return np.sum((y - p) ** 2) / y.shape[0]

        @staticmethod
        def df(y, p):
            return y - p


class Utils:
    @staticmethod
    def ext_bias(mat: np.ndarray):
        mat = np.concatenate([mat, np.ones((mat.shape[0], 1))], axis=-1)
        return mat

    @staticmethod
    def zero_fill(mat: np.ndarray):
        m = np.zeros_like(mat)
        return m

    @staticmethod
    def xavier(mat: np.ndarray):
        m = np.random.standard_normal(mat.shape)
        return m


class BPNN:
    def __init__(self, data_rank, batch_size=64, max_iter=600, init_func='Xavier', learning_rate=1e-5,
                 opt_mode='BGD'):
        self.trainData = np.zeros((64, data_rank))
        self.trainLabel = np.zeros((64, 1))
        self.batchSize = batch_size
        self.maxIteration = max_iter
        self.superArgs = {}
        self.grad = {}
        self.prevLayer = self.trainData
        self.hiddenNums = 0
        self.weightInitializeFunc = init_func
        self.learningRate = learning_rate
        self.mode = opt_mode
        self.lossHistory = []

    def __init_weight(self):
        for key in self.superArgs:
            if key[-6:] == 'weight':
                if self.weightInitializeFunc == '0':
                    self.superArgs[key] = Utils.zero_fill(self.superArgs[key])
                elif self.weightInitializeFunc == 'Xavier':
                    self.superArgs[key] = Utils.xavier(self.superArgs[key])
                else:
                    pass

    def add(self, _type='FC', active_func='sigmoid', hide_width=3, loss_func=None):
        if _type == 'FC':
            weight = np.zeros((self.prevLayer.shape[1], hide_width))
            self.superArgs.update({'hide_{}_weight'.format(self.hiddenNums): weight})
            self.grad.update({'hide_{}_grad'.format(self.hiddenNums): None})
            self.grad.update({'hide_{}_delta'.format(self.hiddenNums): None})
            self.superArgs.update(
                {'hide_{}_out'.format(self.hiddenNums): np.zeros((self.prevLayer.shape[0], hide_width))})
            self.prevLayer = weight
            self.hiddenNums += 1
        elif _type == 'CONV':
            pass
        elif _type == 'ACT':
            self.superArgs.update({'hide_{}_func'.format(self.hiddenNums - 1): getattr(MathFunc, active_func)})
        elif _type == 'OUT':
            weight = np.zeros((self.prevLayer.shape[1], 1))
            self.superArgs.update({'out_weight': weight})
            self.superArgs.update({'out'.format(self.hiddenNums): np.zeros((self.prevLayer.shape[0], 1))})
            self.superArgs.update({'out_func': getattr(MathFunc, active_func)})
            self.superArgs.update({'loss_func': getattr(MathFunc, loss_func)})
            self.superArgs.update({'loss': None})
            self.grad.update({'out_grad': None})
            self.grad.update({'out_delta': None})
        else:
            raise TypeError('Unsupported type as {}'.format(_type))

    def forward(self, feature):
        for i in range(self.hiddenNums):
            if not i:
                self.superArgs['hide_{}_out'.format(i)] = np.matmul(feature,
                                                                    self.superArgs['hide_{}_weight'.format(i)])
            else:
                self.superArgs['hide_{}_out'.format(i)] = np.matmul(self.superArgs['hide_{}_out'.format(i - 1)],
                                                                    self.superArgs['hide_{}_weight'.format(i)])
            self.superArgs['hide_{}_out'.format(i)] = self.superArgs['hide_{}_func'.format(i)].f(
                self.superArgs['hide_{}_out'.format(i)])
        self.superArgs['out'] = np.matmul(self.superArgs['hide_{}_out'.format(self.hiddenNums - 1)],
                                          self.superArgs['out_weight'])
        self.superArgs['out'] = self.superArgs['out_func'].f(self.superArgs['out'])

    def run_loss(self, y, p):
        self.superArgs['loss'] = self.superArgs['loss_func'].f(y, p)
        self.lossHistory.append(self.superArgs['loss'])

    def backward(self, feature, y, p):
        self.grad['out_delta'] = self.superArgs['loss_func'].df(y, p) * self.superArgs['out_func'].df(p)
        self.grad['out_grad'] = np.matmul(np.transpose(self.superArgs['hide_{}_out'.format(self.hiddenNums - 1)]),
                                          self.grad['out_delta'])
        if self.hiddenNums == 1:
            self.grad['hide_0_delta'] = np.matmul(self.grad['out_delta'],
                                                  np.transpose(self.superArgs['out_weight'])) \
                                        * self.superArgs['hide_0_func'].df(self.superArgs['hide_0_out'])
            self.grad['hide_0_grad'] = np.matmul(np.transpose(feature), self.grad['hide_0_delta'])
            return
        for i in range(self.hiddenNums - 1, -1, -1):
            if i == self.hiddenNums - 1:
                self.grad['hide_{}_delta'.format(i)] = np.matmul(self.grad['out_delta'],
                                                                 np.transpose(self.superArgs['out_weight'])) * \
                                                       self.superArgs['hide_{}_func'.format(i)].df(
                                                           self.superArgs['hide_{}_out'.format(i)])
                self.grad['hide_{}_grad'.format(i)] = np.matmul(
                    np.transpose(self.superArgs['hide_{}_out'.format(i - 1)]), self.grad['hide_{}_delta'.format(i)])
            elif i == 0:
                self.grad['hide_0_delta'] = np.matmul(self.grad['hide_1_delta'],
                                                      np.transpose(self.superArgs['hide_1_weight'])) * \
                                            self.superArgs[
                                                'hide_0_func'].df(self.superArgs['hide_0_out'])
                self.grad['hide_0_grad'] = np.matmul(np.transpose(feature), self.grad['hide_0_delta'])
            else:
                self.grad['hide_{}_delta'.format(i)] = np.matmul(self.grad['hide_{}_delta'.format(i + 1)],
                                                                 np.transpose(
                                                                     self.superArgs[
                                                                         'hide_{}_weight'.format(i + 1)])) * \
                                                       self.superArgs['hide_{}_func'.format(i)].df(
                                                           self.superArgs['hide_{}_out'.format(i)])
                self.grad['hide_{}_grad'.format(i)] = np.matmul(
                    np.transpose(self.superArgs['hide_{}_out'.format(i - 1)]), self.grad['hide_{}_delta'.format(i)])

    def adapt(self):
        for key in self.superArgs:
            if key[-6:] == 'weight':
                self.superArgs[key] += self.learningRate * self.grad['{}grad'.format(key[:-6])]

    def fit(self, train_data, train_label):
        self.trainData = np.array(train_data)
        self.trainData = Utils.ext_bias(self.trainData)  # 生成增广矩阵
        self.trainLabel = np.array(train_label)  # 制作真实值标签Label
        self.__init_weight()  # 初始化权重
        self.forward(self.trainData)  # 先进行一轮前向传播
        self.run_loss(self.trainLabel, self.superArgs['out'])  # 根据预测结果计算loss
        print('Initial Loss: {}'.format(self.superArgs['loss']))
        time_total = 0.0
        for i in range(1, self.maxIteration + 1):
            begin_time = time.perf_counter()
            if self.mode == 'BGD':  # BGD模式
                self.forward(self.trainData)  # 所有训练样本进行前向传播
                self.backward(self.trainData, self.trainLabel, self.superArgs['out'])  # 反向传播计算梯度
                self.adapt()  # 根据梯度和学习率更新权重
            elif self.mode == 'SGD':  # SGD模式
                d = np.random.randint(0, self.trainData.shape[0])  # 随机获取一个样本
                self.forward(self.trainData[d:d + 1])  # 前向传播该样本
                self.backward(self.trainData[d:d + 1], self.trainLabel[d:d + 1], self.superArgs['out'])  # 反向传播计算梯度
                self.adapt()  # 根据梯度和学习率更新权重
            elif self.mode == 'MBGD':  # MBGD模式
                m, n = self.trainData.shape[0] // self.batchSize, self.trainData.shape[0] % self.batchSize  # 计算轮数
                for a in range(m):
                    self.forward(self.trainData[a * self.batchSize:(a + 1) * self.batchSize])  # 读入batch_size个样本前向传播
                    self.backward(self.trainData[a * self.batchSize:(a + 1) * self.batchSize],
                                  self.trainLabel[a * self.batchSize:(a + 1) * self.batchSize],
                                  self.superArgs['out'])  # 反向传播计算梯度
                    self.adapt()  # 根据梯度更新权重
                if n:  # 如果无法batch_size无法整除样本数，将剩余的样本再进行一次前后向传播
                    self.forward(self.trainData[m * self.batchSize:m * self.batchSize + n])
                    self.backward(self.trainData[m * self.batchSize:m * self.batchSize + n],
                                  self.trainLabel[m * self.batchSize:m * self.batchSize + n],
                                  self.superArgs['out'])
                    self.adapt()
            else:
                pass
            time_total += time.perf_counter() - begin_time
            if not i % 10:  # 每十轮进行一次前向传播输出loss
                self.forward(self.trainData)
                self.run_loss(self.trainLabel, self.superArgs['out'])
                print('Epoch {}, Loss: {}, Average Epoch Time: {}s'.format(i, self.superArgs['loss'],
                                                                           round(time_total / i, 3)))

    def run(self, dataset):
        dataset = np.array(dataset)
        dataset = Utils.ext_bias(dataset)
        self.forward(dataset)
        return self.superArgs['out']

    def get_loss_history(self):
        return self.lossHistory


def run_10_cross_validation(from_disk=False):
    if not from_disk:
        data = dataLoader('data/train.csv').load()
        c = dataCutter(data, mode='10 cross')
        data = c.run()
        np.save('testdata', data, allow_pickle=True)
    else:
        data = np.load('testdata.npy', allow_pickle=True)
    mse_history = []
    model = set_model()
    for d in data:
        tr, va = d[0], d[1]
        train_data = [i[:-1] for i in tr]
        train_label = [[i[-1]] for i in tr]
        valid_data = [i[:-1] for i in va]
        valid_label = [[i[-1]] for i in va]
        model.fit(train_data, train_label)
        valid_mse = MathFunc.mse.f(np.array(valid_label), model.run(valid_data))
        mse_history.append(valid_mse)
        print('Valid MSE: {}'.format(valid_mse))
    print('Average MSE: {}'.format(np.average(mse_history)))


def set_model():
    model = BPNN(61, opt_mode='MBGD', max_iter=10000, init_func='Xavier', learning_rate=1e-5)
    model.add(_type='FC', hide_width=2048)
    model.add(_type='ACT', active_func='sigmoid')
    model.add(_type='FC', hide_width=2048)
    model.add(_type='ACT', active_func='sigmoid')
    model.add(_type='FC', hide_width=2048)
    model.add(_type='ACT', active_func='sigmoid')
    model.add(_type='OUT', active_func='relu', loss_func='mse')
    return model


if __name__ == '__main__':
    # run_10_cross_validation(from_disk=True)
    data = dataLoader('data/train.csv').load()
    valid_data = [i[:-1] for i in data]
    valid_label = [[i[-1]] for i in data]
    model = set_model()
    model.fit(valid_data, valid_label)
    c = model.run(valid_data)
    np.save('predict', c)
    with open('1.txt', 'w') as file:
        file.write(str(model.get_loss_history()))

# 5556
