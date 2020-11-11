# Assignment 5: Ray tracing

<p align="right"> 18340040 冯大纬 </p>

## 实验要求

- **Task 1、跟着教程实现Chapter 2 ~ Chapter 6的内容。**
- **Task 2、跟着教程实现Chapter 7~ Chapter 12的内容。**
- **Task 3、跟着教程实现了一个精简的光线追踪渲染器，谈谈你的感想和收获。**

## 实验环境

OS：Windows 10 Ver 1903

运行时环境：VS2019

## 实验结果

### Task 1、跟着教程实现Chapter 2 ~ Chapter 6的内容。

#### Chapter 2 The vec3 class

![image-20201109192929650](https://maho.kyoka.cloud/images/2020/11/09/image-20201109192929650.png)

<p align="middle"> 图1 CH2运行结果</p>

![image-20201109203130968](https://maho.kyoka.cloud/images/2020/11/09/image-20201109203130968.png)

<p align="middle"> 图2 将CH2结果写入ppm文件用matlab预览</p>



#### Chapter 3: Rays, a simple camera, and background

![image-20201109200255028](https://maho.kyoka.cloud/images/2020/11/09/image-20201109200255028.png)

<p align="middle"> 图3 CH3运行结果</p>

![image-20201109203020401](https://maho.kyoka.cloud/images/2020/11/09/image-20201109203020401.png)

<p align="middle"> 图4 将CH3结果写入ppm文件用matlab预览</p>



#### Chapter 5: Surface normals and multiple objects.

![image-20201109202859714](https://maho.kyoka.cloud/images/2020/11/09/image-20201109202859714.png)

<p align="middle"> 图5 将CH5结果写入ppm文件用matlab预览</p>

#### Chapter 6: Antialiasing

![image-20201109204619503](https://maho.kyoka.cloud/images/2020/11/09/image-20201109204619503.png)

<p align="middle"> 图6 将CH6结果写入ppm文件用matlab预览</p>

### Task 2、跟着教程实现Chapter 7~ Chapter 12的内容。

#### Chapter 7: Diffuse Materials

![image-20201109205526761](https://maho.kyoka.cloud/images/2020/11/09/image-20201109205526761.png)

<p align="middle"> 图7 将CH7结果写入ppm文件用matlab预览</p>

#### Chapter 8: Metal

![image-20201109210923517](https://maho.kyoka.cloud/images/2020/11/09/image-20201109210923517.png)

<p align="middle"> 图8 将CH8结果写入ppm文件用matlab预览</p>

#### Chapter 9: Dielectrics

![image-20201109211422784](https://maho.kyoka.cloud/images/2020/11/09/image-20201109211422784.png)

<p align="middle"> 图9 将CH9结果写入ppm文件用matlab预览</p>

#### Chapter 10: Positionable camera

![image-20201109212200129](https://maho.kyoka.cloud/images/2020/11/09/image-20201109212200129.png)

<p align="middle"> 图10 将CH10-1结果写入ppm文件用matlab预览</p>

![image-20201109215455164](https://maho.kyoka.cloud/images/2020/11/09/image-20201109215455164.png)

<p align="middle"> 图11 将CH10-2结果写入ppm文件用matlab预览</p>

#### Chapter 11: Defocus Blur

![image-20201109221046032](https://maho.kyoka.cloud/images/2020/11/09/image-20201109221046032.png)

<p align="middle"> 图12 将CH11结果写入ppm文件用matlab预览</p>

#### Chapter 12: Where next?

![image-20201109230104235](https://maho.kyoka.cloud/images/2020/11/10/image-20201109230104235.png)

<p align="middle"> 图13 将CH12结果写入ppm文件用matlab预览</p>

#### Final

跟着教程做完12个章节以后，将光追算法迁移到PathTracer中，按照作业要求中给出的视角位置渲染最终图像

![image-20201110200038576](https://maho.kyoka.cloud/images/2020/11/10/image-20201110200038576.png)

<p align="middle"> 图14 最终生成的结果</p>

### Task 3、跟着教程实现了一个精简的光线追踪渲染器，谈谈你的感想和收获。

上课时候听光追算法感觉巨高端巨难，但跟着教程一步一步实现下来感觉好像也没有想象中那么复杂，看起来原理就是完全递归去模拟一束光，然后运用一些公式来追踪这束光在遇到各种不同表面时候的反射路径或者折射路径，最后获得每一个像素点的颜色就ok了。

感想就是用CPU渲染图像真的好慢，800x600的图片竟然要460s才能渲染完，再联想一下现在游戏可以在短时间内渲染出一个更大的场景，看起来是用了不少黑科技。

最后再上一张2k画质的渲染结果，花了将近一个小时，太难顶了

![image-20201110211455012](https://maho.kyoka.cloud/images/2020/11/10/image-20201110211455012.png)