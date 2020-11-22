# Assignment 6: Bézier曲线

<p align="right"> 18340040 冯大纬 </p>

## 实验要求

Task 1、实现de Casteljau算法，并用它来绘制Beizer曲线。

Task 2、在Task 1的基础上，调整一下代码以支持更多的控制点。

Task 3、谈谈你对Beizer曲线的理解。

## 实验环境

OS：Windows 10 Ver 1903

运行时环境：VS2019

## 实验结果

### Task 1、实现de Casteljau算法，并用它来绘制Beizer曲线。

流程图：

![DC](https://maho.kyoka.cloud/images/2020/11/22/DC.png)

根据该流程图实现代码

```c++
cv::Point2f de_Casteljau(const std::vector<cv::Point2f> &control_points, float t) 
{
    // TODO: Implement de Casteljau's algorithm

    auto sz = control_points.size();

    if (sz == 1) // 只有一个控制点，返回该点
        return control_points[0];

    std::vector<cv::Point2f> new_control_points;

    for (auto i = 0;i < sz - 1;++i) {
        auto p = control_points[i];
        auto q = control_points[i + 1];
        new_control_points.push_back((q - p) * t + p); // 按比例t切割新控制点，加入控制点集合
    }

    return de_Casteljau(new_control_points, t); // 递归

}
```

在`bezier`中调用`de_Casteljau`方法

```c++
void bezier(const std::vector<cv::Point2f> &control_points, cv::Mat &window) 
{
    // TODO: Iterate through all t = 0 to t = 1 with small steps, and call de Casteljau's 
    // recursive Bezier algorithm.

    for (auto i = 0.0;i <= 1.0;i += 0.001) {
        auto point = de_Casteljau(control_points, i);
        window.at<cv::Vec3b>(point.y, point.x)[1] = 255;
    }
}
```



绘制Bezier曲线

![image-20201122121905649](https://maho.kyoka.cloud/images/2020/11/22/image-20201122121905649.png)



### Task 2、在Task 1的基础上，调整一下代码以支持更多的控制点。

需要修改的地方有两处

(1)main中的调用，判断条件改为`if (control_points.size() == 10) `

(2)鼠标动作回调事件，判断条件改为`if (event == cv::EVENT_LBUTTONDOWN && control_points.size() < 10) `



绘制Bezier曲线

![image-20201122122024993](https://maho.kyoka.cloud/images/2020/11/22/image-20201122122024993.png)

### Task 3、谈谈你对Bezier曲线的理解。

- **k**阶Bezier曲线由**k+1**个控制点绘制而成

- **de_Casteljau**方法是通过在k个控制点之间递归采样达到降阶的效果，最后绘制出Bezier曲线的

- 高阶的Bezier曲线可以通过不停的**递归**直到一阶
- 由于系数是二项式的展开，所以**各项系数之和为1**
- **第i项**系数和**倒数第i项**系数相同（对称性）
- Bezier曲线始终会在**包含了所有控制点的最小凸多边形**中（凸包性）
- Bezier曲线一定通过**两个端点**（端点性）
- Bezier曲线是**连续**的（连续性）