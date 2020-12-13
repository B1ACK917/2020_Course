# Assignment 7: 弹簧质点系统

<p align="right"> 18340040 冯大纬 </p>

## 实验要求

Task1：完善rope.cpp 中的 Rope::rope(...)。

Task2：完善rope.cpp 中的 Rope::simulateEuler(...)。

Task3：完善rope.cpp 中的 Rope::simulateVerlet(...)。

## 实验结果

### Task1：完善rope.cpp 中的 Rope::rope(...)

思路：

1. 根据`num_nodes`计算每两个点之间的距离
2. 根据间隔从`start`开始一次生成中间的点
3. 每两点之间设置一个`Spring`弹簧



![image-20201213121042194](https://i.loli.net/2020/12/13/fw7jHU4VJa3o9Q6.png)



### Task2：完善rope.cpp 中的 Rope::simulateEuler(...)

思路：

1. 遍历弹簧，对每个弹簧求出$a,b$
2. 利用$a,b$计算出$f_{b\to a}$和$f_{a\to b}$
3. 对弹簧两个端点分别施加$f_{b\to a}$和$f_{a\to b}$
4. 对每个节点使用物理定律计算$v$和$x$



![image-20201213130430360](https://i.loli.net/2020/12/13/y4cYMHmKz9fFbZG.png)

<p align="middle"> 步数分别为16、64、256、1024情况下的rope</p>



当设置阻尼系数为0时，绳子自由落下，没有弹起来。

可以观察到的现象是阻尼系数越大，绳子弹起来的越快。



### Task3：完善rope.cpp 中的 Rope::simulateVerlet(...)

思路：

1. 遍历弹簧，对每个弹簧求出$a,b$
2. 利用$a,b$计算出$f_{b\to a}$和$f_{a\to b}$
3. 对弹簧两个端点分别施加$f_{b\to a}$和$f_{a\to b}$
4. 使用$x(t+1)=x(t)+(1-d)[x(t)-x(t-1)]+a(t)*dt*dt$计算绳子下一刻的位置



当阻尼系数从0变化到0.005时，明显地变化是绳子摆动的次数减少了，阻尼系数越大，摆动次数越少，当系数为0.005时，绳子只摆动了一次就停下了。

![image-20201213133017890](https://i.loli.net/2020/12/13/cekE2rRmuoKy4Tx.png)

<p align="middle"> 阻尼系数分别为0,0.00005,0.0005,0.005情况下的rope</p>