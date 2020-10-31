# Assignment 4: Lighting

<p align="right"> 18340040 冯大纬 </p>

## 实验要求

**Task 1、在Shader 类中的fragment 函数中实现漫反射光照的计算逻辑。**

**Task 2、在Shader 类中的fragment 函数中实现Phong的镜面光照计算逻辑。**

**Task 3、在Shader 类中的fragment 函数中实现Blinn-Phong的镜面光照计算逻辑。**

**Task 4、在main 函数中实现eye绕着y旋转的动画。**

**Task 5、（选做）在OpenGL中实现传统的光照模型。**

## 实验环境

OS：Windows 10 Ver 1903

运行时环境：VS2019

## 实验结果

### Task 1、在Shader 类中的fragment 函数中实现漫反射光照的计算逻辑。

**思路：**

由于忘记漫反射要怎么算了，所以我首先百度了一下phong模型中的漫反射定义：对于表面比较粗糙的物体，基本表面的明暗就是漫反射效果，比如裤子的材质。某一个象素的明暗系数只取决于该点与光源的相对位置，而与眼睛的位置无关。

由此，假设明暗系数为$diff$那么可以得出以下公式
$$
diff=max(0,normal\times light)
$$
其中，$normal$为该点的法线向量，$light$为该点到光源的单位向量，当该点的法线和光源叉积为负时，说明该点无法被光源照射到，所以其明暗系数应该为0，此时使用负值是没有意义的，所以要取叉积和0的最大值。

由此可以写出代码

```c++
diff = std::max(0.f, normal * lightDir);
```

结果如下图

![image-20201031103535986](https://maho.kyoka.cloud/images/2020/10/31/image-20201031103535986.png)

<p align="middle"> 图1 加入漫反射前后效果对比<br>
    左:无漫反射	右:有漫反射
</p>



### Task 2、在Shader 类中的fragment 函数中实现Phong的镜面光照计算逻辑。

**思路：**

原始的Phong模型的镜面反射计算公式有如下形式
$$
I_{spec}=(V*R)^{p}k_sI_l
$$
其中，$V$是从顶点到视点的观察方向，$R$代表反射光方向，$p$为高光指数，本次实验要求更换为4/16/64并对比，$k_s$和$I_l$均为反射系数，由于没有用到所以记为单位矩阵，在运算中可以忽略，即$I_{spec}=(V*R)^p$

反射光$R$的的方向和入射光$L$存在以下关系
$$
R+L=(2*N*L)N
$$
所以我们可以推导出$R$的计算方法，即
$$
R=N*(2*N*L)-L
$$
基于$(2)(4)$式，可以写出以下代码

```c++
int p = 4;
//使用(4)式计算反射光R
Vec3f R_reflect = (normal * 2 * (normal * lightDir) - lightDir).normalize();

//使用(2)式计算镜面反射系数
spec = pow(viewDir * R_reflect, p);
```

更换不同p值效果如下

![image-20201031111931631](https://maho.kyoka.cloud/images/2020/10/31/image-20201031111931631.png)

<p align="middle"> 图2 不同反射效果对比<br>
    第一行左起：漫反射、高光系数p=4<br>
    第二行左起：高光系数p=16、高光系数p=64
</p>



### Task 3、在Shader 类中的fragment 函数中实现Blinn-Phong的镜面光照计算逻辑。

**思路：**

和Phong光照对比，Blinn-Phong其实只是修改了$(2)$式中的$R$参数，原来的Phong模型计算$R$需要进行多次向量乘法，运算缓慢，而Blinn-Phone模型使用了半角向量$H$来代替$R$
$$
H=\frac{L+V}{|L+V|}\\
I=(V*H)^p
$$
相比于原来$(4)$式计算$R$的过程，很明显计算半角向量$H$要简洁很多，只需要让光线向量和视线向量相加并转换为单位向量即可，基于$(5)$式，可以写出以下代码

```c++
int p = 4;
//使用(5)式计算半角向量H和镜面反射系数
Vec3f H = (lightDir + viewDir).normalize();
spec = pow(normal * H, p);
```

更换不同p的渲染效果如下

![image-20201031115743463](https://maho.kyoka.cloud/images/2020/10/31/image-20201031115743463.png)

<p align="middle"> 图3 Blinn-Phong不同高光系数对比<br>
    左起：高光系数p=4、高光系数p=16、高光系数p=64<br>
</p>



![image-20201031120016130](https://maho.kyoka.cloud/images/2020/10/31/image-20201031120016130.png)

<p align="middle"> 图4 Phong和Blinn-Phong效果对比<br>
    第一行：高光系数p=4、16、64的Phong模型效果<br>
    第二行：高光系数p=4、16、64的Blinn-Phong模型效果
</p>



经过对比可以看出，Blinn-Phong做的这个改进一方面加快了渲染的速度，因为半角向量的计算比反射光线向量要方便很多，另一方面，使用Blinn-Phong方法渲染出的效果也更加真实

### Task 4、在main 函数中实现eye绕着y旋转的动画。

**原理：**

3维空间中的点$p$绕$y$轴旋转$\theta$角的旋转矩阵有如下表示形式
$$
\left[ \begin{matrix} cos(\theta) & 0 & sin(\theta) & 0\\ 0 & 1 & 0 & 0  \\ -sin(\theta) & 0 & cos(\theta) & 0 \\ 0& 0 & 0 & 1\end{matrix} \right]
$$
将旋转过程封装为函数`rotete_y`如下：

```c++
Vec3f rotate_y(Vec3f pre_eye, double angle) {
    //角度转弧度
    constexpr double INNER_PI = 3.1415926;
    double rotate = angle * INNER_PI / 180;

    //按照(6)式生成旋转矩阵
    mat<4, 4, float> rotateMatrix;
    rotateMatrix=rotateMatrix.identity();
    rotateMatrix[0][0] = cos(rotate);
    rotateMatrix[0][2] = sin(rotate);
    rotateMatrix[2][0] = -sin(rotate);
    rotateMatrix[2][2] = cos(rotate);

    //将原来3维的pre_eye向量增广为4维并旋转
    Vec4f rotated = rotateMatrix * embed<4>(pre_eye);
    
    //生成旋转后的向量
    Vec3f res(rotated[0], rotated[1], rotated[2]);
    return res;
}
```

在渲染的主循环中调用`rotete_y`来旋转视角

```c++
eye = rotate_y(eye, 30); //旋转角度30度便于观察差别
```

连续4帧结果如下

![image-20201031132651940](https://maho.kyoka.cloud/images/2020/10/31/image-20201031132651940.png)

<p align="middle"> 图5 连续4帧每帧旋转30度</p>

### Task 5、（选做）在OpenGL中实现传统的光照模型。

#### 环境光照

LearnOpenGL给出的片段着色器没有定义输入输出和中间变量，加上以后就可以运行了

```c++
#version 330 core
out vec4 FragColor;

in vec3 FragPos;  

uniform vec3 lightColor;
uniform vec3 objectColor;

void main()
{
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;
    vec3 result = ambient * objectColor;
    FragColor = vec4(result, 1.0);
} 
```



![image-20201031134809064](https://maho.kyoka.cloud/images/2020/10/31/image-20201031134809064.png)

<p align="middle"> 图6 只使用环境光照，物体非常暗</p>

#### 漫反射光照

![image-20201031135904848](https://maho.kyoka.cloud/images/2020/10/31/image-20201031135904848.png)

<p align="middle"> 图7 使用漫反射光照，物体变亮了一些，但没有高光显得不是很真实</p>

#### 镜面光照

![image-20201031140127990](https://maho.kyoka.cloud/images/2020/10/31/image-20201031140127990.png)

<p align="middle"> 图8 完整的Phong光照模型，环境光+漫反射+镜面反射</p>

## 感想

这次实验虽然主要的难点在数学运算上，也就是推导公式和查资料，但做完以后很有成就感，尤其是看到原本很破烂的模型在Blinn-Phong光照模型下能够获得很真实的效果时感觉很爽

实验所有工程文件均开源至

<a href="https://github.com/B1ACK917/2020_Course/tree/master/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%9B%BE%E5%BD%A2%E5%AD%A6">Github</a>

