import os
import pickle as pickle
import numpy as np
import wget
import tarfile

URL = 'https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz'


def download_CIFAR10(_dir):
    os.mkdir(_dir)
    original_dir = os.getcwd()
    os.chdir(_dir)
    filename = wget.download(URL)
    _file = tarfile.open(filename)
    _file.extractall()
    os.chdir(original_dir)


def load_CIFAR_batch(filename):
    with open(filename, 'rb') as f:
        datadict = pickle.load(f, encoding='latin1')
        X = datadict['data']
        Y = datadict['labels']
        X = X.reshape(10000, 3, 32, 32).transpose(0, 2, 3, 1).astype("float")
        Y = np.array(Y)
        return X, Y


def load_CIFAR10(_dir):
    file = _dir + '/' + 'cifar-10-batches-py'
    if not os.path.isdir(file):
        print('No Cifar Dataset found, Begin to download cifar-10-python.tar.gz')
        download_CIFAR10(_dir)
        print('Download Completed')
    print('Detected Cifar-10 Dataset, loading from disk')
    data_dir = _dir + '/' + 'cifar-10-batches-py'
    xs = []
    ys = []
    for b in range(1, 6):
        f = os.path.join(data_dir, 'data_batch_%d' % (b,))
        X, Y = load_CIFAR_batch(f)
        xs.append(X)
        ys.append(Y)
    Xtr = np.concatenate(xs)
    Ytr = np.concatenate(ys)
    Xte, Yte = load_CIFAR_batch(os.path.join(data_dir, 'test_batch'))
    return Xtr, Ytr, Xte, Yte
