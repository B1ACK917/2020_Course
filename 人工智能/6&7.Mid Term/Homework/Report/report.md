# 人工智能期中Project实验报告

<p align="right"> 18340040 冯大纬<br>
	18340034 邓明昱<br></p>


## CNN+CIFAR-10

### 算法原理

​	卷积神经网络（Convolutional Neural Networks, CNN）是一类包含卷积计算且具有深度结构的前馈神经网络（Feedforward Neural Networks）。卷积神经网络仿造生物的视知觉（visual perception）机制构建，可以进行监督学习和非监督学习，其隐含层内的卷积核参数共享和层间连接的稀疏性使得卷积神经网络能够以较小的计算量对格点化（grid-like topology）特征，例如像素和音频进行学习、有稳定的效果且对数据没有额外的特征工程（feature engineering）要求。

​	卷积神经网络的结构通常为输入层+隐藏层+输出层。在输入层常对数据进行归一化操作，有利于提升卷积神经网络的学习效率和表现。卷积神经网络中输出层的上游通常是全连接层，因此其结构和工作原理与传统前馈神经网络中的输出层相同。卷积神经网络的隐含层包含卷积层、池化层和全连接层 3 类常见构筑，在一些更为现代的算法中可能有 Inception 模块、残差块（residual block）等复杂构筑。在常见构筑中，卷积层和池化层为卷积神经网络特有。卷积层中的卷积核包含权重系数，而池化层不包含权重系数，因此在文献中，池化层可能不被认为是独立的层。

![image-20201111162015032](https://maho.kyoka.cloud/images/2020/11/11/image-20201111162015032.png)

<p align="center">[图片来源：课件]</p>


​	相比于全连接层，卷积核的使用使得网络参数数量有非常显著的减少。卷积层的功能是对输入数据进行特征提取，其内部包含多个卷积核，组成卷积核的每个元素都对应一个权重系数和一个偏差量（bias vector），类似于一个前馈神经网络的神经元（neuron）。卷积层内每个神经元都与前一层中位置接近的区域的多个神经元相连，区域的大小取决于卷积核的大小，在文献中被称为“感受野（receptive field）”，其含义可类比视觉皮层细胞的感受野。卷积核在工作时，会有规律地扫过输入特征，在感受野内对输入特征做矩阵元素乘法求和并叠加偏差量（以二维卷积核为例）：

![img](https://bkimg.cdn.bcebos.com/formula/eb0088f908d955e0e452d3b05ae309b4.svg)

![img](https://bkimg.cdn.bcebos.com/formula/1375ccf3da0c734269f31499744ad0e9.svg)

​	式中的求和部分等价于求解一次交叉相关（cross-correlation）。$b$ 为偏差量，$Z^l$ 和 $Z^{l+1}$ 表示第 $l+1$ 层的卷积输入和输出，也被称为特征图（feature map），$L^{l+1}$ 为 $Z^{l+1}$ 的尺寸，这里假设特征图长宽相同。$Z(i,j)$ 对应特征图的像素，$K$ 为特征图的通道数，$f$ 、$s_0$ 和 $p$ 是卷积层参数，对应卷积核大小、卷积步长（stride）和填充（padding）层数。[1]

​	卷积层参数包括卷积核大小、步长和填充，三者共同决定了卷积层输出特征图的尺寸，是卷积神经网络的超参数。其中卷积核大小可以指定为小于输入图像尺寸的任意值，卷积核越大，可提取的输入特征越复杂。

### 伪代码与流程图

#### 	流程图

![CNN (2)](https://maho.kyoka.cloud/images/2020/11/11/CNN-2.png)

#### 	伪代码

```c++
开始
    读入训练集
    读入测试集
    设置参数 max_epoch,learning_rate
    for i:=0 to max_epoch:
        使用Adam优化器
        优化器梯度清零
        CNN_Output=Model(数据)
        Loss=CrossEntropy(Output,Label)
        Loss反向传播
        优化器更新参数
    测试集测试准确率
    保存模型
    输出日志
结束
```



### 关键代码

```python
def layer(name, _x, drop_rate):
    global GLOBAL_DICT
    if name[:4] == 'conv':  # 卷积层连接
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
    elif name == 'maxpool':  # 最大池化层连接
        a, b = int(float(GLOBAL_DICT['SHAPE'][0]) / 2 + 0.5), int(float(GLOBAL_DICT['SHAPE'][1]) / 2 + 0.5)
        GLOBAL_DICT['SHAPE'] = (a, b, GLOBAL_DICT['SHAPE'][2])
        return max_pool(_x)
    elif name == 'meanpool':  # 平均池化层连接
        a, b = int(float(GLOBAL_DICT['SHAPE'][0]) / 2 + 0.5), int(float(GLOBAL_DICT['SHAPE'][1]) / 2 + 0.5)
        GLOBAL_DICT['SHAPE'] = (a, b, GLOBAL_DICT['SHAPE'][2])
        return mean_pool(_x)
    elif name[:2] == 'FC':  # 全连接层
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
    elif name == 'softmax':  # softmax层
        with tf.compat.v1.variable_scope(name):
            W = wei_mat([GLOBAL_DICT['FLATTENED_SHAPE'], GLOBAL_DICT['CLASSES']])
            B = bias_mat([GLOBAL_DICT['CLASSES']])
            y = tf.nn.softmax(multi(_x, W) + B)
            # y =multi(_x, W) + B
            return y
    return None
```



### 优化点

#### 	归一化(Normalization)

​	由于直接读入的数据集使用了RGB格式存储，所以每一个维度上的值位于 (0,255) 内，所以我们队输入数据进行了归一化，把数据变成 (0,1) 或者 (1,1) 之间的小数。主要是为了数据处理方便，把数据映射到 0～1 范围之内处理，更加便捷快速。

​	而且在使用梯度下降的方法求解最优化问题时， 归一化后可以加快梯度下降的求解速度，即提升模型的收敛速度。如下图所示，未归一化/标准化时形成的等高线偏椭圆，迭代时很有可能走“之”字型路线（垂直长轴），从而导致迭代很多次才能收敛。而对两个特征进行了归一化，对应的等高线就会变圆，在梯度下降进行求解时能较快的收敛。

![img](https://upload-images.jianshu.io/upload_images/2880006-762f0ef1c74dcd75.png?imageMogr2/auto-orient/strip|imageView2/2/w/809/format/webp)

<p align="center">[图片来源：简书]</p>

#### 	自动化模型构建(AutoGenerator)

​	在反复修改模型的过程中，我们感觉到了手动一层层堆叠卷积层和池化层过于麻烦，而且其实连接过程中可以通过上一层的输出来即时获得下一层的输入形状，所以我们设计了 `layer` 函数，这个函数可以根据我们需要的网络结构自动连接其中的每一层，并给出每一层连接后通过的 Tensor 形状，比如我们定义 TestNet 时就是在 `modelshape.py` 中定义如下结构：

```python
class TestNet:
    FLOW_PATH = ['conv3_64', 'maxpool', 'conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'conv3_512', 'maxpool',
                 'FC_256', 'FC_128',
                 'softmax']
    LAYER_NUMS = {
        'conv3_64': 1,
        'conv3_128': 1,
        'conv3_256': 1,
        'conv3_512': 1,
        'maxpool': 1,
        'FC_256': 1,
        'FC_128': 1,
        'softmax': 1
    }
```

​	在运行时使用

```shell
python cf10.py --model TestNet
```

​	模型会采用反射机制从 modelshape 中获取对应模型名称中给出的 `FLOW_PATH` 以及 `LAYER_NUMS` 并依据 `FLOW_PATH` 构建模型，并给出张量路径如下：

![image-20201111133747577](https://maho.kyoka.cloud/images/2020/11/11/image-20201111133747577.png)

​	基于该 `AutoGenerator` ，我们可以随意定义不同模型结构，把连接过程交给电脑去推定，省去手动连接网络结构的麻烦。

​	以下是我们最后写出的模型结构：

```python
class ModelShape:
    class AlexNet:
        FLOW_PATH = ['conv11_96', 'maxpool', 'conv5_256', 'maxpool', 'conv3_384', 'conv5_256', 'maxpool', 'FC_1024',
                     'FC_1024', 'softmax']
        LAYER_NUMS = {
            'conv11_96': 1,
            'conv5_256': 1,
            'conv3_384': 2,
            'FC_1024': 1,
            'maxpool': 1,
            'softmax': 1
        }

    class VGG16:
        FLOW_PATH = ['conv3_64', 'maxpool', 'conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'conv3_512', 'maxpool',
                     'conv3_512', 'maxpool', 'FC_4096', 'FC_4096', 'softmax']
        LAYER_NUMS = {
            'conv3_64': 2,
            'conv3_128': 2,
            'conv3_256': 3,
            'conv3_512': 3,
            'maxpool': 1,
            'FC_4096': 1,
            'softmax': 1
        }

    class VGG19:
        FLOW_PATH = ['conv3_64', 'maxpool', 'conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'conv3_512', 'maxpool',
                     'conv3_512', 'maxpool', 'FC_4096', 'FC_4096', 'softmax']
        LAYER_NUMS = {
            'conv3_64': 2,
            'conv3_128': 2,
            'conv3_256': 4,
            'conv3_512': 4,
            'maxpool': 1,
            'FC_4096': 1,
            'softmax': 1
        }

    class VGG11:
        FLOW_PATH = ['conv3_64', 'maxpool', 'conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'conv3_512', 'maxpool',
                     'conv3_512', 'maxpool', 'FC_4096', 'FC_4096', 'softmax']
        LAYER_NUMS = {
            'conv3_64': 1,
            'conv3_128': 1,
            'conv3_256': 2,
            'conv3_512': 2,
            'maxpool': 1,
            'FC_4096': 1,
            'softmax': 1
        }

    class SimpleNet:
        FLOW_PATH = ['conv3_64', 'maxpool', 'conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'FC_1024', 'FC_1024',
                     'softmax']
        LAYER_NUMS = {
            'conv3_64': 1,
            'conv3_128': 1,
            'conv3_256': 1,
            'maxpool': 1,
            'FC_1024': 1,
            'softmax': 1
        }

    class TestNet:
        FLOW_PATH = ['conv3_64', 'maxpool', 'conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'conv3_512', 'maxpool',
                     'FC_256', 'FC_128',
                     'softmax']
        LAYER_NUMS = {
            'conv3_64': 1,
            'conv3_128': 1,
            'conv3_256': 1,
            'conv3_512': 1,
            'maxpool': 1,
            'FC_256': 1,
            'FC_128': 1,
            'softmax': 1
        }

```



### 实验结果与分析

#### 	预挑选

​	经过精挑细选以及对我们算力的权衡以后，我们筛选出了 4 种模型：AlexNet，VGG11，SimpleNet，以及我们自己定义了一个网络，暂且称为 TestNet 。

 TestNet 的结构如下：

![SimpleNet (2)](https://maho.kyoka.cloud/images/2020/11/11/SimpleNet-2.png)

​	为了挑出在我们设备上能够获得最好效果的模型，我们首先对这四个模型以 1e-5 的学习率，运行 120 轮检测效果，结果如下：

![acc](https://maho.kyoka.cloud/images/2020/11/11/acc.png)

<p align="center"> 120迭代准确率变化图</p>

![loss](https://maho.kyoka.cloud/images/2020/11/11/loss1e71f3ff062fc088.png)

<p align="center"> 120迭代Loss变化图</p>

​	经过一番思考，我们认为虽然理论上 AlexNet 或者 VGG 有更高的上限，但鉴于我们羸弱的 GPU，我们最后选择了经过少量迭代就能获得不错效果的 TestNet 来作为最终模型进行训练。

#### Dataset & Train

- **训练集**：$45000\times32\times32\times3$

- **验证集**：$5000\times32\times32\times3$

- **测试集**：$10000\times32\times32\times3$

  训练过程可视化如下

  ![final](https://maho.kyoka.cloud/images/2020/11/11/final.png)

  |         | Learning Rate | Epoch | Test Accuracy | Time   |
  | ------- | ------------- | ----- | ------------- | ------ |
  | TestNet | 1e-5          | 500   | 0.74638671875 | 4811 s |

  ​	在训练过程中，我们的模型一度在验证集上取得了 0.9935555458068848 的准确率，但测试集的效果却只有 0.746，应该是发生了过拟合现象，由于时间关系，再加上我们认为这个模型上限也就这么高了，所以没有继续改下去。
  
  

## RNN+SEMEVAL2014-TASK4

### 算法原理

​	循环神经网络（Recurrent Neural Network, RNN）是一类以序列数据为输入的神经网络。相比于 CNN，它不需要对输入数据的长度做出限制。因此它在自然语言处理以及时序序列数据处理方面有着广泛的运用。

​	以下图为例，RNN 网络中有一个循环单元（RNN-cell，图中 A）。其从前往后依次以输入序列 $X$ 的单个数据单元 $x$ 和当前 RNN-cell 的隐信息 $s$ 作为输入，新的隐信息 $s'$ 和输出结果 $o$（图中 $h$）为输出。 

![](https://upload-images.jianshu.io/upload_images/6983308-42172a6dae3d3388.png?imageMogr2/auto-orient/strip|imageView2/2/w/1198/format/webp)

<p align="center">[图片来源：https://www.jianshu.com/p/95d5c461924c]


​	形式化表示为 $o_{t},s_t=f(s_{t-1},\ x_t,\ \theta)$ ，$\theta$ 是 RNN-cell 的内部参数，$f$ 是由 RNN-cell 的结构决定的函数。

​	RNN-cell 的结构、参数权重等对于每个输入的数据单元 $x$ 都是相同的，不同的只是隐状态 $s$ 。隐状态 $s$ 取决于 $x$ 之前的输入序列，会编码之前的输入序列运算得到的信息。

​	最基础的 RNN 网络具有非常明显的长依赖问题，体现为梯度爆炸和梯度消失等。RNN 只要输入序列长度足够，就可能因为权重参数的连续卷积导致指数级增长，从而引发这些问题。从信息的角度来说，隐状态 $s$ 的编码能力是有限的，在长距离上必然导致信息的损失。

### 优化点

​	因为计算资源的极度匮乏，所以在经过分析后，我们直接实现了 BiLSTM+CRF 的组合并进行训练。这其中蕴含了若干优化点。

#### 			双向循环神经网络（bidirectional recurrent neural network, BRNN）

​	BRNN 中至少包含两个 RNN 网络结构，分别将输入序列按照相反的方向处理。得到的结果进行拼接。这样的结果就同时具有前后文的信息关联。而普通的 RNN 结构只能提前到前文的信息以及前文中可能蕴含的少量后文信息。在处理有两个方向关联的问题时，BRNN  往往会比 RNN 有更好的表现。

#### 		长短期记忆网络（long short-term memory networks, LSTM）

![](https://upload-images.jianshu.io/upload_images/6983308-169c41fa64ff202f.png?imageMogr2/auto-orient/strip|imageView2/2/w/1200/format/webp)

<p align="center">[图片来源：https://www.jianshu.com/p/95d5c461924c]

​	LSTM 是最早被提出的 RNN 门控算法，其对应的循环单元，LSTM 单元包含 3 个门控：输入门、遗忘门和输出门。相对于 RNN 对系统状态建立的递归计算， 3 个门控对 LSTM 单元的内部状态建立了自循环（self-loop）。具体地，输入门决定当前时间步的输入和前一个时间步的系统状态对内部状态的更新；遗忘门决定前一个时间步内部状态对当前时间步内部状态的更新；输出门决定内部状态对系统状态的更新。LSTM 单元的更新方式如下：

![img](https://bkimg.cdn.bcebos.com/formula/bc414a02d88532aa94ace41f72de8e98.svg)

式中 ![img](https://bkimg.cdn.bcebos.com/formula/fe915c129ddf2c3cbd0fc0cfa91e4afd.svg) 为系统状态和内部状态的激励函数，通常为双曲正切函数， ![img](https://bkimg.cdn.bcebos.com/formula/e9ded7e59993ccb9e18d8c80478a6048.svg) 为随时间步更新的门控，本质上是以 Sigmoid​ 函数为激励函数的前馈神经网络，使用 Sigmoid 函数的原因是其输出在 ![img](https://bkimg.cdn.bcebos.com/formula/b70d9b7f862c65b650d5152b1c0bb800.svg) 区间，等效于一组权重。式中脚标 ![img](https://bkimg.cdn.bcebos.com/formula/eb37d821c8ad58d9ec561ffc972b65f0.svg) 表示输入门、遗忘门和输出门。[1]

#### 	Focal Loss

​	Focal loss 主要是为了解决 one-stage 目标检测中正负样本比例严重失衡的问题。该损失函数降低了大量简单负样本在训练中所占的权重，也可理解为一种困难样本挖掘。负样本数量太大，占总的 loss 的大部分，而且多是容易分类的，因此使得模型的优化方向并不是我们所希望的那样。

![img](https://maho.kyoka.cloud/images/2020/11/10/1055519-20180818174822290-765890427.png)

#### 		条件随机场（conditional random field, CRF）

​	设 $X$ 与 $Y$ 是随机变量，$P(Y|X)$ 是在给定 $X$ 的条件下 $Y$ 的条件概率分布。若随机变量 $Y$ 构成一个由无向图 $G = (V,E)$ 表示的马尔可夫随机场，即：$P(Y_v|X,Y_w,w≠v)=P(Y_v|X,Y_w,w∼v)$ 对任意结点 $v$ 成立，则称条件概率分布 $P(Y|X)$ 为条件随机场。

​	在序列标注问题中，常采用的是线性链条件随机场。每个状态只通过上一个状态计算得到。线性链条件随机场的形式化定义为：设 $X=\{X_i\}^n_{i=1},\ Y=\{Y_i\}^n_{i=1}$ 均为线性链表示的随机变量序列，若在给定随机变量序列 $X$ 的条件下，随机变量序列 $Y$ 的条件概率分布 $P(Y|X)$ 构成条件随机场，即满足马尔可夫性 $P(Y_i|X,Y_1,…,Y_{i−1},Y_{i+1},…,Y_n)=P(Y_i|X,Y_{i−1},Y_{i+1})$ 则称 $P(Y|X)$ 为线性链条件随机场。

​	在序列标注问题中引入 CRF 是非常自然的想法。LSTM 的输出没有显式地对标签之间的关系进行考虑，而 CRF 可以通过转移矩阵进行限制。CRF 有两类特征函数，一是观测序列与状态的对应关系，二是状态间关系。在 LSTM+CRF 模型中，前一类特征函数为 LSTM 的输出，后一类特征函数为标签转移矩阵。

​	那么在这个模型下，一个句子 $y$ 的总得分就是其标签得分 $label$ 与转移得分 $T$ 之和：（$s$ 为句中词的标签）
$$
score(y)=\sum_i label_i+T_{s_{i-1},s_i}
$$
​	在计算得到单个句子得分后，用 softmax 进行归一化，计算 $y$ 的概率（的以 $e$ 为底的对数）：
$$
p(y|x)=\frac{e^{score(y)}}{\sum_ye^{score(y)}} \\
\log p(y|x)=score(y)-\log \sum_ye^{score(y)}
$$
​	$score(y)$ 可以直接按照上文的公式计算，接下来考虑 $\log \sum_ye^{score(y)}$ 的计算。因为这是一个线性链条件随机场，所以可以使用动态规划的思想进行求解。记 $Score[i][j]$ 表示考虑长度为 $i$ 的前缀，第 $i$ 个标签为 $j$ 的贡献（$\log\sum e^{score}$）。那么有转移方程：
$$
Score[i][j]=\log\sum_k e^{Score[i-1][k]+T[k][j]+label[i][j]} \\
=\log\sum_k e^{Score[i-1][k]}+\sum_kT[k][j]+label[i][j]
$$
​	采用上式递推即可在可以接受的时间复杂度内完成 $\log \sum_ye^{score(y)}$ 的计算。（转移方程可以表示为矩阵形式）

​	在训练模型时，使用负对数似然作为损失函数 $loss=-\log p(y|x)$ 。

​	那么还剩下最后一个问题，就是如何对一个测试的句子给出最大概率的预测标签。这一步依然可以使用动态规划的思想解决，也称为维特比（Viterbi）算法。还是基于线性链条件随机场的特性设计状态，$ver[i][j]$ 表示考虑长度为 $i$ 的前缀，第 $i$ 个标签为 $j$ 的得分中最大值。那么就有计算式：
$$
ver[i][j]=\max_k(ver[i-1][k]+T[k][j]+label[i][j])
$$
​	只要维护每个状态的最大值由谁转移得到，那么从最后一个标签的最大概率状态沿着转移关系往回跳就可以知道最大得分的序列了。

### 伪代码与流程图

- **流程图**

  ![RNN (1)](https://maho.kyoka.cloud/images/2020/11/11/RNN-1.png)

- **伪代码**

  ```c++
  开始
      读入数据
      清洗数据
      设置参数 max_epoch,learning_rate
      for i:=0 to max_epoch:
          使用Adam优化器
          优化器梯度清零
          RNN_Output=RNN(数据)
          Pre_Output=Linear(RNN_Output)
          Output=Softmax(Pre_Output)
          Loss=Some_Loss_Func(Output,Label)
          Loss反向传播
          优化器更新参数
      测试集测试准确率，F1 Score
      保存模型
      输出日志
  结束
  ```

  

### 关键代码

```python
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
```



```python
def train(Epoch, features, labels):
    loss_history = 0.0
    for i in range(len(features)):
        feature = torch.from_numpy(features[i]).to(device)  # 转换到Tensor
        net.train()
        optimizer = optim.Adam(net.parameters(), lr=args.learningrate)  # Adam优化器
        optimizer.zero_grad()  # 梯度清零
        output = net(feature)
        label = torch.from_numpy(labels[i]).long().to(device).reshape((-1, 1)) 
        loss_func = CRF(output_dim).to(device)
        loss_train = -loss_func(output.reshape(output.shape[0], 1, -1), label.reshape(label.shape[0], -1))  # 计算loss
        loss_train.backward()  # 反向传播
        optimizer.step()  # 优化器更新参数
        loss_history += loss_train
    loss = loss_history / len(features)
    print('Epoch: {}, loss: {}'.format(Epoch, loss))
    return loss
```



### 实验结果与分析

​	由于算力十分匮乏，在对众多RNN模型性能和准确率的评估时只能采用小样本训练测试的方法，在对 12 种 RNN 模型进行测试以后，我们最终选择了  BiLSTM+CRF 模型，下面是我们对不同网络架构及损失函数进行的测试。

测试环境: 

- OS: Windows 10
- Frame: Pytorch==1.7.0
- GPU: Geforce GTX 1060

 

|                                           | Loss Function                          | Test Accuracy                                         | Test F1 Score                                         |
| ----------------------------------------- | -------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------- |
| RNN                                       | CrossEntropy                           | 0.6654066996147242                                    | 0.7693158547815103                                    |
| RNN                                       | FocalLoss                              | 0.855441676036169                                     | 0.9163426219430729                                    |
| RNN                                       | CRF                                    | 0.7542451398080774                                    | 0.8464741933500994                                    |
| BRNN                                      | CrossEntropy                           | 0.8364031545612287                                    | 0.9034853843825944                                    |
| BRNN                                      | FocalLoss                              | 0.8650943475137247                                    | 0.9247849044237034                                    |
| BRNN                                      | CRF                                    | 0.8317918145017136                                    | 0.9020786980637671                                    |
| LSTM                                      | CrossEntropy                           | 0.8648677960734374                                    | 0.9245148838653231                                    |
| LSTM                                      | FocalLoss                              | 0.8580561567952676                                    | 0.9197293760085405                                    |
| <span style="color:#FF0000">LSTM</span>   | <span style="color:#FF0000">CRF</span> | <span style="color:#FF0000">0.8666332165478992</span> | <span style="color:#FF0000">0.9256662659413841</span> |
| BiLSTM                                    | CrossEntropy                           | 0.8449110450487229                                    | 0.9096760516466343                                    |
| BiLSTM                                    | FocalLoss                              | 0.8653871358078269                                    | 0.9247237096767079                                    |
| <span style="color:#FF0000">BiLSTM</span> | <span style="color:#FF0000">CRF</span> | <span style="color:#FF0000">0.8659369202516027</span> | <span style="color:#FF0000">0.9253097542452986</span> |



​	由于不同 loss 种类之间的对比是没有意义的，所以我们在选择使用哪一种神经元以及是否使用双向神经网络时仅进行了同种 loss 间的对比，对比可视化如下：

![cross](https://maho.kyoka.cloud/images/2020/11/10/cross3a7cc9a60204ba49.png)

![focal](https://maho.kyoka.cloud/images/2020/11/10/focal.png)

![crf](https://maho.kyoka.cloud/images/2020/11/10/crf.png)

​	经过对三种 loss 和不同种神经网络架构的对比，我们选择了 <span style="color:#FF0000">BiLSTM+CRF</span> 来作为最终模型进行训练。



​	训练过程 loss 可视化如下：

![loss](https://maho.kyoka.cloud/images/2020/11/11/loss.png)



​	在测试集上的测试结果非常好，我们有理由相信此次RNN实验圆满成功。

|            | Learning Rate | Epoch | Test Accuracy     | Test F1 Score      |
| ---------- | ------------- | ----- | ----------------- | ------------------ |
| BiLSTM+CRF | 1e-4          | 2100  | 0.945211545461047 | 0.9668265805017919 |

### 一些失败的尝试

​	在标注的训练过程中，我们一直在与 “把所有词都标为非关键词“ 战斗。构建出的模型非常容易收敛到那种情况。在数日的修改中我们有许多的失败，但是我们认为应该把它们记下来。于是就开了这一个小节。

​	有些尝试可能不是因为它有问题而失败。在这个过程中我们同时在做出很多修改。它们只是没有被应用于最终版本的代码中。

#### 		手写 LSTM

​	在 RNN 的实现过程中，我们尝试了自己构建的 LSTM 。

```python
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
```

​	按照最基础的 LSTM 结构实现的网络在收敛的效果上表现不好。loss 相比于 pytorch 提供的 LSTM 高出很多。并且训练也很艰难。在代码修改的过程中放弃了这一部分。

#### 		更精细的标注

​	我们先采用了 BIOES 标注方法。经过后期的分析，我们认为这个是导致出现 “把所有词都标为非关键词” 问题的最主要原因。标注过细，但是样本不足，导致网络标注错误。

​	通过对数据本身分析，认为关键词不会连续出现。于是转而使用二分类标注，相连的关键词认为是同一个词。相比于 BIO 标注方法，二分类更容易摆脱我们当前所处的困境。而它也没有让我们失望，在抽样的小数据上训练了上千个 epoch 后，网络的 loss 达到了新低，结果显示它完美地预测了训练样本的标签。于是我们将二分类应用于大数据集进行测试后，采用了这种方案。

### 参考资料

[1] 百度百科：循环神经网络

[2] https://www.cnblogs.com/ooon/p/5818227.html

[3] https://zhuanlan.zhihu.com/p/97829287

[4] CRF 的实现参考了 https://github.com/SkyAndCloud/bilstm_crf_sequence_labeling_pytorch



### 组员分工

​	冯大纬主导 CNN 部分的实验内容，撰写了大部分代码。邓明昱主导 RNN 部分的实验内容。