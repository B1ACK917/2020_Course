import tensorflow as tf
from tensorflow.contrib.layers import xavier_initializer
from model_shape import *

FLOW_PATH = None
LAYER_NUMS = None
GLOBAL_DICT = None
CNT = 0


def wei_mat(shape):
    global CNT
    # ini = tf.random.truncated_normal(shape, stddev=0.001)
    ini = tf.get_variable(str(CNT), shape, tf.float32, xavier_initializer())
    CNT += 1
    return tf.Variable(ini)


def bias_mat(shape):
    ini = tf.constant(0.1, dtype=tf.float32, shape=shape)
    return tf.Variable(ini)


def conv_2d(x_, W):
    return tf.nn.conv2d(x_, W, [1, 1, 1, 1], padding='SAME')


def max_pool(x_):
    return tf.nn.max_pool2d(x_, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


def mean_pool(x_):
    return tf.nn.avg_pool2d(x_, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


def multi(x_, W):
    return tf.matmul(x_, W)


def layer(name, _x, drop_rate):
    global GLOBAL_DICT
    if name[:4] == 'conv':
        spname = name.split('_')
        conv_kernel_size = int(spname[0][4:])
        output_channel_num = int(spname[1])
        for num in range(LAYER_NUMS[name]):
            with tf.compat.v1.variable_scope(name + str(num)):
                W = wei_mat([conv_kernel_size, conv_kernel_size, GLOBAL_DICT['SHAPE'][2], output_channel_num])
                B = bias_mat([output_channel_num])
                _x = tf.nn.relu(conv_2d(_x, W) + B)
            GLOBAL_DICT['SHAPE'] = (GLOBAL_DICT['SHAPE'][0], GLOBAL_DICT['SHAPE'][1], output_channel_num)
        return _x
    elif name == 'maxpool':
        a, b = int(float(GLOBAL_DICT['SHAPE'][0]) / 2 + 0.5), int(float(GLOBAL_DICT['SHAPE'][1]) / 2 + 0.5)
        GLOBAL_DICT['SHAPE'] = (a, b, GLOBAL_DICT['SHAPE'][2])
        return max_pool(_x)
    elif name == 'meanpool':
        a, b = int(float(GLOBAL_DICT['SHAPE'][0]) / 2 + 0.5), int(float(GLOBAL_DICT['SHAPE'][1]) / 2 + 0.5)
        GLOBAL_DICT['SHAPE'] = (a, b, GLOBAL_DICT['SHAPE'][2])
        return mean_pool(_x)
    elif name[:2] == 'FC':
        if not GLOBAL_DICT['IS_FLATTENED']:
            GLOBAL_DICT['FLATTENED_SHAPE'] = GLOBAL_DICT['SHAPE'][0] * GLOBAL_DICT['SHAPE'][1] * GLOBAL_DICT['SHAPE'][2]
            _x = tf.reshape(_x, [-1, GLOBAL_DICT['FLATTENED_SHAPE']])
            GLOBAL_DICT['IS_FLATTENED'] = True
        with tf.compat.v1.variable_scope(name):
            bias_num = int(name[3:])
            W = wei_mat([GLOBAL_DICT['FLATTENED_SHAPE'], bias_num])
            B = bias_mat([bias_num])
            Out = tf.nn.relu(multi(_x, W) + B)
            Out_dropout = tf.nn.dropout(Out, rate=drop_rate)
            GLOBAL_DICT['FLATTENED_SHAPE'] = bias_num
            return Out_dropout
    elif name == 'softmax':
        with tf.compat.v1.variable_scope(name):
            W = wei_mat([GLOBAL_DICT['FLATTENED_SHAPE'], GLOBAL_DICT['CLASSES']])
            B = bias_mat([GLOBAL_DICT['CLASSES']])
            y = tf.nn.softmax(multi(_x, W) + B)
            # y =multi(_x, W) + B
            return y
    return None


def model(ynum, name='VGG16', show_flowshape=False):
    global FLOW_PATH, GLOBAL_DICT, LAYER_NUMS
    GLOBAL_DICT = {
        'IS_FLATTENED': False,
        'FLATTENED_SHAPE': 0,
        'SHAPE': (32, 32, 3),
        'CLASSES': ynum,
    }
    FLOW_PATH = getattr(getattr(ModelShape, name), 'FLOW_PATH')
    LAYER_NUMS = getattr(getattr(ModelShape, name), 'LAYER_NUMS')
    x = tf.compat.v1.placeholder(tf.float32,
                                 [None, GLOBAL_DICT['SHAPE'][0] * GLOBAL_DICT['SHAPE'][1] * GLOBAL_DICT['SHAPE'][2]])
    label = tf.compat.v1.placeholder(tf.float32, [None, ynum])
    var = tf.reshape(x, [-1, GLOBAL_DICT['SHAPE'][0], GLOBAL_DICT['SHAPE'][1], GLOBAL_DICT['SHAPE'][2]])
    drop_rate = tf.compat.v1.placeholder(tf.float32)
    if show_flowshape:
        print('Input tensor shape : ' + str(var.shape))
    for FLOW in FLOW_PATH:
        var = layer(FLOW, var, drop_rate)
        if show_flowshape:
            print('Operation is %s ,repeat %d times, tensor shape : ' % (FLOW, LAYER_NUMS[FLOW]) + str(var.shape))

    return x, label, var, drop_rate
