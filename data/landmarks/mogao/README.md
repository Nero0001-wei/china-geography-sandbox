# 莫高窟第96窟九层楼

九层楼贴在砾岩崖壁上，层层挑檐与两侧较小洞窟表现崖面尺度。第96窟外现状九层木构窟檐。[景区或机构资料](https://www.dha.ac.cn/info/1425/3648.htm)

## 制作取舍

按敦煌研究院资料保留贴崖的九道檐口。崖面根据洞口位置裁去网格，补上洞壁与内侧背墙。砾岩纵向起伏和横向层理在侧光下可看到，崖壁与正面的红色木构可以分别编辑。

[ImageGen 正面、右侧和侧前方参考](reference/三视角.webp) · [提示词原文](reference/prompt.txt) · [原始三景九格图](../workshop-c/reference/B.png)

## 地理锚点

OpenStreetMap 九层楼主体建筑轮廓的面积质心。 经纬度顺序为经度、纬度，WGS84 **94.8037828°、40.0372951°**。GLB 的局部 +Z 朝地理方位 86°，以正北为 0° 顺时针计。朝九层楼广场（约94.8044774,40.0373285），取向东略偏北。[主体定位来源](https://www.openstreetmap.org/way/1308425685) · [地图接入元数据](site.json)

地理取样覆盖约 38 米。全国沙盘使用统一显示尺度。模型局部原点对齐主体锚点，底面高度为零。出行时可分别检索“莫高窟数字展示中心停车场”与“莫高窟数字展示中心”。

## 模型与回读结果

| 网页资产 | 版本 | 三角面 | 字节数 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [mogao.glb](../../../app/public/models/mogao.glb) | national-v1 | 4,948 | 608,352 | 10 / 10 |

实模图来自空白场景重新导入网页 GLB 后的三角度正交渲染。材质均从 GLB 内部读取。原始分组和贴图保存在[可编辑 Blender 母版](source.blend)，导出与母版的 SHA-256 记录于[实测统计](stats.json)。

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 网页预览

[全国视图](../web/全国视图.png) · [手机全国视图](../web/手机全国视图.png) · [景点斜视近景](web/斜视近景.png)

## 重建

在项目根目录使用 Blender 5.2.1。修改母版后，以下命令从已保存的分组网格导出并更新网页文件、面数和实模图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/workshop-c/build.py -- mogao --from-master
```

完整重建时移除 `--from-master`。几何位于[场景脚本](../workshop-c/sites.py)，重复构件使用[几何函数](../workshop-c/geometry.py)，[导出脚本](../workshop-c/build.py)读取已备好的[原创材质贴图](../workshop-c/textures/)。如需重新生成贴图，可用带 Pillow 的 Python 执行 `python3 data/landmarks/workshop-c/surfaces.py`。
