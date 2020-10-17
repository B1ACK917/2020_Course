# Assignment 3: Rasterization与Zbuffering

<p align="right"> 18340040 冯大纬</p>

## 实验要求

- **Task 1、在`rasterize_triangle`函数中实现计算二维三角形的轴向包围盒。**
- **Task 2、在`insideTriangle `函数中实现判断给定的二维点是否在三角形内部。**
- **Task 3、在`rasterize_triangle `函数中实现Z-buffering算法。**
- **Task 4、回顾光栅化所处的阶段，思考并回答：光栅化的输入和输出分别是什么，光栅化主要负责做什么工作。**
- **Task 5、仔细观察光栅化的结果，你可以看到如下的锯齿走样现象，思考并回答：走样现象产生的原因是？列举几个抗锯齿的方法。**
- **Task 6、（选做）实现反走样算法——超采样抗锯齿方法。**

## 实验结果

### Task 1、在`rasterize_triangle`函数中实现计算二维三角形的轴向包围盒。

**思路：**

由于轴向包围盒需要把整个三角形包含进去，所以x的最小值就是三个顶点x坐标的最小值，最大值就是三个顶点x坐标的最大值，y也是如此

**代码：**

```c++
float x0 = t.v[0][0], x1 = t.v[1][0], x2 = t.v[2][0];
float y0 = t.v[0][1], y1 = t.v[1][1], y2 = t.v[2][1];
xmin = min(min(x0, x1), x2);
ymin = min(min(y0, y1), y2);
xmax = max(max(x0, x1), x2);
ymax = max(max(x0, x1), x2);
```

**运行截图：**

![image-20201017212318042](https://maho.kyoka.cloud/images/2020/10/17/image-20201017212318042.png)

<p align="middle"> 图1 绘制出的轴向包围盒</p>

### Task 2、在`insideTriangle `函数中实现判断给定的二维点是否在三角形内部。

**思路：**

假设存在点P，三角形ABC

连接PA，将PA和AB做叉积，将CA和AB做叉积，如果两个叉积的结果方向一致，那么点P和点C在AB的同侧

连接PB，将PA和AC做叉积，将BA和AC做叉积，如果两个叉积的结果方向一致，那么点P和点B在AC的同侧

连接PC，将PC和CB做叉积，将AC和CB做叉积，如果两个叉积的结果方向一致，那么点P和点A在CB的同侧

如果以上三点都满足，那么P在三角形内部

**代码：**

```c++
bool isSameSide(Vector3f A, Vector3f B, Vector3f C, Vector3f P) {
    // 判断两点是否在同一边
    Vector3f AB = B - A;
    Vector3f AC = C - A;
    Vector3f AP = P - A;
	
    // 两次叉乘取垂线
    Vector3f v1 = AB.cross(AC);
    Vector3f v2 = AB.cross(AP);

    // 判断两个叉积是否同方向
    return v1.dot(v2) >= 0;
}
```

```c++
static bool insideTriangle(int x, int y, const Vector3f* _v)
{   
    Vector3f P;
    P << x, y, 0;
    return isSameSide(_v[0], _v[1], _v[2], P) && isSameSide(_v[1], _v[2], _v[0], P) && isSameSide(_v[2], _v[0], _v[1], P);
}
```

**运行截图：**

![image-20201017214242537](https://maho.kyoka.cloud/images/2020/10/17/image-20201017214242537.png)

<p align="middle"> 图2 绘制出的两个三角形</p>

### Task 3、在`rasterize_triangle `函数中实现Z-buffering算法。

**思路：**

对于一个点(x,y)，先使用`get_index`来获取它在buffer中的位置，将目前buffer中存放的深度值和三角形这个位置的深度值作比较，如果buffer中的深度值比当前位置深度值大，说明当前点离屏幕更近，那么将buffer这个点的深度值更新为当前深度值，并且把这个点渲染为该三角形的颜色。

**代码：**

```c++
int index = get_index(x, y);
if (depth_buf[index] > z_interpolated) { // 如果buffer深度值大于当前深度，说明三角形该点离屏幕更近，应该渲染为该颜色
    depth_buf[index] = z_interpolated;  // 更新buffer
    frame_buf[get_index(x, y)] = 255.0f * t.color[0];  //渲染为三角形t的颜色
}
```

**运行截图：**

![image-20201017221221123](https://maho.kyoka.cloud/images/2020/10/17/image-20201017221221123.png)

<p align="middle"> 图3 使用Z-Buffer对正确的遮挡关系上色</p>

### Task 4、回顾光栅化所处的阶段，思考并回答：光栅化的输入和输出分别是什么，光栅化主要负责做什么工作。

光栅化的输入是一个多边形的各顶点坐标，输出是二维图像上的一个点，这个点包含颜色，深度，纹理等数据。

比如说光栅化一个三角形，就是将三角形的三个顶点坐标输入，然后获得这个三角形覆盖了哪些像素以及这些像素的颜色、深度、纹理等数据。

所以其实光栅化负责的工作就是将连续的三角形离散化为一个个像素点，让我们能够把这些像素点输出到屏幕上。

### Task 5、仔细观察光栅化的结果，你可以看到如下的锯齿走样现象，思考并回答：走样现象产生的原因是？列举几个抗锯齿的方法。

由于我们对三角形进行光栅化后获得的是一个一个离散的单元，由于像素本质上的离散性，导致其在屏幕上显示的时候具有锯齿形的外观，这种由于低频取样导致的情况就是走样

目前比较常见的抗锯齿方法有：

SSAA：超采样抗锯齿，即先渲染一张尺寸为目标图像2倍长宽的图像，然后对每个2x2像素进行一次采样

MSAA：多重采样抗锯齿，类似SSAA，不过为了提高效率，只对边缘部分进行SSAA

FXAA：快速近似抗锯齿，主要工作在流水管线后端

### Task 6、（选做）实现反走样算法——超采样抗锯齿方法。

由于最后我们使用均值滤波进行下采样，所以可以计算每个点的上下左右四个点有几个在三角形内，也就是放大4倍后的四个像素点会有几个被上色

比如经过计算发现只有两个点最后会落在三角形内被上色，那么这个点经过中值滤波的下采样以后的颜色值就是$0.5\times color$

关键代码：

```c++
if (depth_buf[index] > z_interpolated) {
    depth_buf[index] = z_interpolated; // 更新Z-Buffer
    int count = 0;

    auto steps = std::array{-1,1};  // 遍历上下左右4个点
    for (auto delta_x : steps) {
        for (auto delta_y : steps) {
            int xn = x + delta_x;
            int yn = y + delta_y;
            if (insideTriangle(xn, yn, t.v)) {  // 判断在不在三角形内
                count++;
            }
        }
    }
    float percent = min(1.0f, 1.0f * count / (steps.size() * steps.size()));  // 计算中值滤波后的像素值百分比
    frame_buf[get_index(x, y)] = percent * 255.0f * t.color[0];  // 根据百分比上色
}
```



最后实现的效果如下：

![image-20201017231036246](https://maho.kyoka.cloud/images/2020/10/18/image-20201017231036246.png)

<p align="middle"> 使用SSAA后渲染的三角形</p>

将经过SSAA后的三角形边缘部分放大和之前作对比

![image-20201017232218335](https://maho.kyoka.cloud/images/2020/10/18/image-20201017232218335.png)

<p align="middle"> 图5 左：未使用SSAA  右：使用SSAA</p>