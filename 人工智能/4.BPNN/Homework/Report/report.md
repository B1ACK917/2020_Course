# BPNN实验报告

<p align="right"> 18340040 冯大纬</p>

## 算法原理

### 模型参数定义

BPNN是众多神经网络中最基础的一种模型，它的基本形式如下

![image-20201019193534145](https://maho.kyoka.cloud/images/2020/10/19/image-20201019193534145.png)

<p align="middle"> 图1 单层神经网络</p>

最简单的BPNN由三层构成，$L_1$为输入层，其中的每个节点接收来自输入的信息，$L_2$为隐含层，负责对$L_1$层的数据变换，$L_3$层为输出层，负责对$L_2$层节点再做一次变换后得到最后的输出结果。

一般在使用这种三层模型的时候还会在层与层之间加入激活函数以达到非线性变换的目的。

多层神经网络就是在输入层和输出层之间再多加几层隐含层，但针对全连接的隐含层来说，目前已经有理论证明了具有偏差和至少一个S型隐含层加上一个线性输出层的网络,能够逼近任何有理函数，所以大多数情况下对于全连接的神经网络，只需要一层隐含层就可以了。

对于这种单层的神经网络，我们可以用矩阵来表示参数以使用矩阵运算达到加速的目的

我们给每个来自输入节点$i$，指向隐含节点$j$的边编号为$w_{ij}$，输入向量增广一维，值为1，作为权重的偏置项，如下图

![image-20201019195345152](https://maho.kyoka.cloud/images/2020/10/19/image-20201019195345152.png)

<p align="middle"> 图2 单层神经网络参数</p>

假设我们的输入向量为$X$，那么输入层到隐含层之间的权重矩阵可以表示为如下形式
$$
\left[ \begin{matrix} w_{11} & w_{12} & w_{13}\\ w_{21} & w_{22} & w_{23} \\ w_{31} & w_{32} & w_{33} \\ w_{41} & w_{42} & w_{43} \end{matrix} \right]
$$
测试一下这个矩阵对输入向量$X$做一次矩阵乘法的效果
$$
\left[ \begin{matrix} x_1&x_2& x_3& 1.0\end{matrix} \right]\left[ \begin{matrix} w_{11} & w_{12} & w_{13}\\ w_{21} & w_{22} & w_{23} \\ w_{31} & w_{32} & w_{33} \\ w_{41} & w_{42} & w_{43} \end{matrix} \right]\\
=\left[ \begin{matrix} x_1w_{11}+x_2w_{21}+x_3w_{31}+w_{41}&x_1w_{12}+x_2w_{22}+x_3w_{32}+w_{42}& x_1w_{13}+x_2w_{23}+x_3w_{33}+w_{43}\end{matrix} \right]
=\left[ \begin{matrix} H_1&H_2& H_3\end{matrix} \right]
$$
完美符合我们对隐含层节点的定义，说明将其写成这样的矩阵形式是合理的。

使用矩阵还有一个好处就是在使用MBGD方法进行梯度下降时，可以一次读入`Batch_size`个向量拼接成矩阵，然后进行一次矩阵乘法得到所有样本在隐含层上的值，这比对每条边都进行定义要方便很多。

### 前向传播

假设每一个样本最后的特征向量为$v$维，隐含层神经元有$k$个，那么使用上面的方法，我们可以定义一个样本向量构成的矩阵$X$，一个从输入层到隐含层的权重矩阵，记为$W_{I2H}$，以及一个从隐含层到输出层的权重矩阵，记为$W_{H2O}$

其中
$$
X\in R^{n\times v}\\
W_{I2H}\in R^{v\times k}\\
W_{H2O}\in R^{k\times 1}
$$
那么前向传播的流程就是读入样本矩阵$X$，和$W_{I2H}$做矩阵乘法，得到隐含层的值$H_{in}\in R^{n\times k}$，使用激活函数$\pi (x)$对$H$激活得到$H_{out}=\pi(H)$，然后用$H_{out}$和$W_{H2O}$做矩阵乘法得到$n$个样本的输出$O\in R^{n\times 1}$，其中$O$的每一维是每个样本的预测值。

### 反向传播

对于这次实验，我们使用square error做为loss函数，隐含层输出使用sigmoid激活函数，为了让输出能够落在$[0,+\infty]$，输出层使用relu激活函数，即
$$
E=sum(\frac{1}{2}(Y-P)^2)\\
P=relu(H_{out}\times W_{H2O})\\
$$
其中Y为真实Label，P为模型的预测值

更新隐含层到输出层的权重使用如下规则
$$
\delta_1=(Y-P)relu'(H_{out}\times W_{H2O})\\
W_{H2O}=W_{H2O}+\eta \delta_1 H_{out}
$$
更新输入层到隐含层的权重使用如下规则
$$
\delta_2=(\delta_1\times W_{I2H}^T).sigmoid'(X\times W_{I2H})\\
W_{I2H}=W_{I2H}+\eta \delta_2X
$$
每次反向传播都使用$(5),(6)$式更新$W_{H2O}，W_{I2H}$

## 伪代码与流程图

### 流程图

![BPNN](https://maho.kyoka.cloud/images/2020/10/19/BPNN.png)

<p align="middle"> 图3 BPNN流程</p>

### 伪代码

```
初始化权重，ite=0
while(ite!=MAX_ITE):
	读入样本
	前向传播计算E
	根据E反向传播更新权重
	ite++
保存模型
```

## 关键代码

```python
def fit(self, train_data, train_label):
    self.trainData = np.array(train_data)
    self.trainData = Utils.ext_bias(self.trainData)  # 生成增广矩阵
    self.trainLabel = np.array(train_label)  # 制作真实值标签Label
    self.__init_weight()  # 初始化权重
    self.forward(self.trainData)  # 先进行一轮前向传播
    self.run_loss(self.trainLabel, self.superArgs['out'])  # 根据预测结果计算loss
    print('Initial Loss: {}'.format(self.superArgs['loss']))
    for i in range(1, self.maxIteration + 1):
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
        if not i % 10:  # 每十轮进行一次前向传播输出loss
            self.forward(self.trainData)
            self.run_loss(self.trainLabel, self.superArgs['out'])
            print('Epoch {}, Loss: {}'.format(i, self.superArgs['loss']))
```

## 优化点

### 数据预处理

对于这次的数据，我认为进行一些数据处理会让模型的训练结果更好

![image-20201019211033373](https://maho.kyoka.cloud/images/2020/10/19/image-20201019211033373.png)

`instant`列可以直接去掉，因为和样本特征没有关联性

`dteday`列也可以直接去掉，因为它的格式是`year-month-day`，而这三个信息在后面的`yr`，`mnth`，`weekday`列都有表现，而且特征更加明显，所以这一列其实可以用后面的`yr`，`mnth`，`weekday`列替换

对于`season`，`yr`，`mnth`，`hr`，`holiday`，`weekday`，`workingday`，`weathersit`这8列，应该对它们实行one-hot编码，因为这几列的数值本身的大小是没有意义的，比如`season`列，假设在实际情况中夏天人们的借车概率更高，但1,2,3,4只能表示不同的季节，而在大小上不能反映出这个事实，所以我们要对它进行one-hot编码，给予第2维一个更高的权重就可以表示出夏天有更高的概率了。

对于`temp`，`atemp`，`hum`，`windspeed`这四列，它们在数值大小上是具有实际意义的，比如温度的高低或者风速的大小，所以这几列转换为浮点数就可以了

最终对于训练集的编码为60维，增广后为61维

### 不同的激活函数

观察这次我们需要做出的预测，可以发现我们要做的是一个位于$[0,+\infty]$上的预测，而如果依旧使用`sigmoid`做输出层的激活函数，我们只能得到位于$[0,1]$上的输出，所以对于输出层的激活函数，我们应当选择使用`relu`函数

我是用了最原始版本的relu，即$x<0$时，$f(x)=0$，$x>0$时，$f(x)=x$，画出图像如下图所示

![image-20201019212244449](https://maho.kyoka.cloud/images/2020/10/19/image-20201019212244449.png)

<p align="middle"> 图4 relu函数图像</p>

### 多层神经网络

我使用了$(6)$式的通用形式进行多层隐含层之间的梯度计算，即
$$
\delta_h=(\delta_{h+1}\times W_{h2h+1}^T).sigmoid'(X\times W_{h2h+1})\\
W_{h2h+1}=W_{h2h+1}+\eta \delta_hX
$$
在编写代码时我已经写好了加深加宽的接口，定义为`def add(self, _type='FC', active_func='sigmoid', hide_width=3, loss_func=None)`

如果要构建一个包含2层隐含层的全连接BPNN，只需要使用如下代码即可构建一个分别具有256，128个神经元的两层隐含层BPNN

```python
model.add(_type='FC', hide_width=256)
model.add(_type='ACT', active_func='sigmoid')
model.add(_type='FC', hide_width=128)
model.add(_type='ACT', active_func='sigmoid')
model.add(_type='OUT', active_func='relu', loss_func='mse')
```

### Mini-batch

本次我使用的Batch_Size设置为64，即每次读入64个样本前向传播，然后使用梯度之和更新权重

MBGD部分的训练代码如下

```python
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
```

## 实验结果与分析

### 单层BPNN

#### 结果

使用单层神经网络，迭代10000轮，学习率1e-5，MBGD梯度下降策略，Batch_Size=64，不同隐藏层节点数目训练的结果如下：

|                  | 最低loss(均方误差) | 平均每轮训练时间 |
| ---------------- | ------------------ | ---------------- |
| Hidden_Nums=16   | 5455               | 0.021s           |
| Hidden_Nums=32   | 3935               | 0.027s           |
| Hidden_Nums=64   | 2765               | 0.034s           |
| Hidden_Nums=128  | 814.4              | 0.065s           |
| Hidden_Nums=256  | 550.5              | 0.126s           |
| Hidden_Nums=512  | 457.1              | 0.217s           |
| Hidden_Nums=1024 | 406.1              | 0.475s           |

可视化训练过程的loss下降如下

![1_h](https://maho.kyoka.cloud/images/2020/10/19/1_h.png)

<p align="middle"> 图5 单层神经网络训练过程</p>

#### 分析

由于这次的要预测的值域很大，有的值可以到好几百，而隐含层的激活函数为sigmoid，所以每个隐含层节点的输出上限为1，如果隐含层节点数目过少会导致最后的预测结果值域过小，导致无法覆盖所有可能结果，所以隐含层节点数目要尽可能多一些。

从图中可以看出，当隐含层节点少于128时，模型无法找到一个合适的参数来尽可能使loss最小，而会不停抖动。

当隐含层节点数目大于等于128时，模型loss可以正常下降，寻找最优参数，而且随隐含层节点数目增加会让loss最小值下降，如下图

![1_h_2](https://maho.kyoka.cloud/images/2020/10/19/1_h_2.png)

<p align="middle"> 图6 隐藏层节点数目大于等于128以后的loss下降</p>

### 多层BPNN

#### 结果

由于层数过多会导致训练速度急剧变慢，所以只测试了两层隐藏层的情况，迭代10000轮，学习率1e-5，MBGD梯度下降策略，Batch_Size=64，结果如下：

|                           | 最低loss(均方误差) | 平均每轮训练时间 |
| ------------------------- | ------------------ | ---------------- |
| 第一层：512，第二层：256  | 7122               | 0.583s           |
| 第一层：1024，第二层：512 | 4209               | 1.581s           |

可视化如下

![2_h](https://maho.kyoka.cloud/images/2020/10/19/2_h.png)

<p align="middle"> 图7 双层BPNN</p>

#### 分析

由图中可以看出，多层神经网络迭代时收敛的非常慢，往往需要抖动很多次才可以找到最佳的下降方向，而且由于多层隐藏层的参数变多了很多，每个参数都要更新导致10000轮迭代以后的效果并不理想，但可以从最后4000轮看出模型已经开始收敛，但收敛速度很慢，或许再多训练几万轮可以达到比单层1024节点更好的效果，但由于每轮训练实在太慢，所以没有继续尝试

对于更多层的神经网络，因为训练速度太慢所以没有训练完，但是拿到了每轮迭代花费的时间，列表如下

|                         | 平均每轮训练时间 |
| ----------------------- | ---------------- |
| 3层隐含层，每层512节点  | 1.677s           |
| 3层隐含层，每层1024节点 | 4.266s           |
| 3层隐含层，每层2048节点 | 16.0s            |
| 4层隐含层，每层512节点  | 2.357s           |
| 4层隐含层，每层1024节点 | 6.243s           |
| 4层隐含层，每层2048节点 | 24.378s          |
| 5层隐含层，每层512节点  | 2.686s           |
| 5层隐含层，每层1024节点 | 8.529s           |
| 5层隐含层，每层2048节点 | 31.566s          |

可以看出，随着深度和宽度的增加，训练速度急速下降，所以在训练的时候应当权衡好训练速度和模型精度之间的平衡。

## 思考题

### 尝试说明下其他激活函数的优缺点。

- Sigmoid函数

  优点：连续，且平滑便于求导

  缺点：由于Sigmoid的导数总是小于1，所以当层数多了之后，会使回传的梯度越来越小，导致梯度消失问题。

- Tanh函数

  优点：解决了Sigmoid函数输出恒大于0的缺点

  缺点：计算量大，需要计算两次e的指数；依然会出现梯度消失问题

- ReLU函数

  优点：x 大于0时，其导数恒为1，这样就不会存在梯度消失的问题；计算导数非常快，只需要判断 x 是大于0，还是小于0

  缺点：因为当x小于等于0时输出恒为0，如果某个神经元的输出总是满足小于等于0 的话，那么它将无法被更新

### 有什么方法可以实现传递过程中不激活所有节点？

使用Dropout方法，在每一层隐藏层后设置一个`Dropout`层，设置`Drop_rate`，当需要激活这个节点时，roll出一个随机数，如果随机数小于`Drop_rate`，则不激活这个节点，否则才激活这个节点。

### 梯度消失和梯度爆炸是什么？可以怎么解决？

梯度消失和梯度爆炸产生的原因是由于链式法则中乘法的存在，当梯度在多层神经网络中传播时，如果网络过深会导致梯度传播回去时经过多次乘法导致数值过小或过大。

比如对于一个十层的BPNN，每层都使用sigmoid激活函数，那么当进行一次反向传播时，每一层的梯度均在$(0,1)$之间，假设均为$0.1$，那么经过10层反向传播，到最接近输入层的隐藏层时，梯度已经变为了$1\times 10^{-9}$，乘以学习率以后近似对这个节点的权重没有更新，这就是梯度消失现象。

梯度爆炸现象也类似，如果每一层的梯度都过大，当连续很多层的梯度连乘以后就会得到一个非常大的梯度，导致最接近输入层的那层隐藏层出现梯度爆炸现象。