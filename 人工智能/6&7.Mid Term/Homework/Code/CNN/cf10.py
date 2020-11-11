import tensorflow as tf
import numpy as np
import time
import model, loader
import os
import argparse

from keras.utils import np_utils, to_categorical
from keras.metrics import categorical_accuracy, categorical_crossentropy

parser = argparse.ArgumentParser()

parser.add_argument('--model', '-m', type=str, default='SimpleNet', help='Training model, default as SimpleNet')
parser.add_argument('--load', '-l', type=bool, default=False, choices=[True, False],
                    help='Whether to use saved model from disk')
parser.add_argument('--learningrate', '-lr', type=float, default=0.001, help='Learning rate')
parser.add_argument('--iteration', '-i', type=int, default=100, help='Training Epoch')
parser.add_argument('--save_ite', '-s', type=int, default=10, help='How many epoch to save model')
parser.add_argument('--normalization', '-n', action='store_true', default=False,
                    help='Whether to use Normalization')


class _run:
    def __init__(self, name, lr, ite, s_ite, from_disk):
        self.g = tf.Graph()
        self.accList = []
        self.lossList = []
        self.model_save_path = './{}_{}_{}/'.format(name, lr, ite)
        self.model_name = 'model'
        self.sess = None
        self.fromDisk = from_disk
        self.learningRate = lr
        self.iteration = ite
        self.saveIte = s_ite
        with self.g.as_default():
            self.x, self.label, self.y, self.drop_rate = model.model(ynum=10, name=name, show_flowshape=True)
            self.cross_entropy = -tf.reduce_sum(self.label * tf.math.log(self.y), axis=1)
            self.accuracy = categorical_accuracy(self.label, self.y)
            self.train_step = tf.compat.v1.train.AdamOptimizer(self.learningRate).minimize(self.cross_entropy)
            self.init = tf.compat.v1.global_variables_initializer()
            self.saver = tf.compat.v1.train.Saver()

    @staticmethod
    def split(x, n):
        a, b = x.shape[0] // n, x.shape[0] % n
        splitted = []
        for i in range(a):
            splitted.append(np.array(x[i * n:(i + 1) * n]))
        splitted.append(np.array(x[a * n:]))
        return splitted

    def fbward(self, x_in, y_in, x_va, y_va, batch_size=256):
        x_in = x_in.astype('float32')
        y_in = y_in.astype('float32')
        x_va = x_va.astype('float32')
        y_va = y_va.astype('float32')
        x_in = self.split(x_in, batch_size)
        y_in = self.split(y_in, batch_size)
        with self.g.as_default():
            self.sess = tf.compat.v1.Session()
            self.sess.run(self.init)
            if self.fromDisk:
                print('Load Model from Disk Path {}'.format(self.model_save_path))
                self.saver.restore(self.sess, os.path.join(self.model_save_path, self.model_name))
            for i in range(1, self.iteration + 1):
                for j in range(len(x_in)):
                    self.sess.run(self.train_step,
                                  feed_dict={self.x: x_in[j], self.label: y_in[j], self.drop_rate: 0.5})

                if i:
                    loss = self.sess.run(self.cross_entropy,
                                         feed_dict={self.x: x_va, self.label: y_va, self.drop_rate: 0})
                    loss = np.average(loss)
                    acc = self.sess.run(self.accuracy,
                                        feed_dict={self.x: x_va, self.label: y_va, self.drop_rate: 0})
                    acc = np.average(acc)
                    print('epoch: {},loss: {}, accuracy: {}'.format(i, loss, acc))
                    self.accList.append(acc)
                    self.lossList.append(loss)
                if not i % self.saveIte:
                    self.saver.save(self.sess, os.path.join(self.model_save_path, self.model_name))
                    print('Model saved')

    def fward(self, x_in, y_in):
        x_in = self.split(x_in, 256)
        y_in = self.split(y_in, 256)
        acc = 0.0
        with self.g.as_default():
            for i in range(len(x_in)):
                _ = self.sess.run(self.accuracy, feed_dict={self.x: x_in[i], self.label: y_in[i], self.drop_rate: 0})
                acc += np.average(_)
            acc = acc / len(x_in)
            print('Test Accuracy: {}'.format(acc))
        return acc


def normalization(x):
    _range = np.max(x) - np.min(x)
    return (x - np.min(x)) / _range


if __name__ == '__main__':
    args = parser.parse_args()
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    x_train, y_train, x_test, y_test = loader.load_CIFAR10('data')
    if args.normalization:
        x_train = normalization(x_train)
        x_test = normalization(x_test)
    x_train = np.reshape(x_train, (x_train.shape[0], -1))
    y_train = np_utils.to_categorical(y_train, 10)
    x_test = np.reshape(x_test, (x_test.shape[0], -1))
    y_test = np_utils.to_categorical(y_test, 10)
    x_train = x_train[:x_train.shape[0] // 10 * 9]
    x_valid = x_train[x_train.shape[0] // 10 * 9:]
    y_train = y_train[:y_train.shape[0] // 10 * 9]
    y_valid = y_train[y_train.shape[0] // 10 * 9:]
    name = args.model
    print(
        'Training With Model {}, learning rate as {}, iteration as {}, save iteration as {}, use normalization: {}'.format(
            name,
            args.learningrate,
            args.iteration,
            args.save_ite,
            args.normalization))
    with tf.device("/gpu:0"):
        mod = _run(name=name, lr=args.learningrate, ite=args.iteration, s_ite=args.save_ite, from_disk=args.load)
        begin = time.perf_counter()
        mod.fbward(x_train, y_train, x_valid, y_valid)
        print('Training Time: {} s'.format(int(time.perf_counter() - begin)))
        acc = mod.fward(x_test, y_test)
        if not os.path.exists('result'):
            os.mkdir('result')
        with open('result/{}_lr{}_ite:{}_Norm{}_acc.txt'.format(name, args.learningrate, args.iteration,
                                                                  args.normalization),
                  'w')as file:
            file.write(str(mod.accList))
            file.write('\n\nTest Accuracy: {}'.format(acc))
        with open(
                'result/{}_lr{}_ite{}_Norm{}_loss.txt'.format(name, args.learningrate, args.iteration,
                                                                 args.normalization),
                'w')as file:
            file.write(str(mod.lossList))
