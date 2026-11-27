# 台北101办公塔楼

采用青绿色玻璃叠竹节的八组塔身、收窄基座，以及顶部细长的塔冠和天线。2004年启用的现状办公塔楼。[景区或机构资料](https://www.taipei-101.com.tw/en/corporate/story/content/b5eb46ce-8f1b-4f65-a0f4-11c3a54bb1ae)

## 制作取舍

按照建筑的八段外扩塔身逐段建立独立对象。青绿色格栅、外框、下段圆形装饰和收束到针尖的塔冠保留近景可见的层次。

[ImageGen 正面、右侧和侧前方参考](reference/三视角.webp) · [提示词原文](reference/prompt.txt) · [原始三景九格图](../workshop-c/reference/C.png)

## 地理锚点

OpenStreetMap 层数为101的塔楼独立轮廓的面积质心，未合并购物中心。 经纬度顺序为经度、纬度，WGS84 **121.5644968°、25.0339726°**。GLB 的局部 +Z 朝地理方位 181.2°，以正北为 0° 顺时针计。塔身四面近似对称，展示正面选择靠信义路的南面；OSM 长边的南向方位约 181.2°。[主体定位来源](https://www.openstreetmap.org/way/1159328965) · [地图接入元数据](site.json)

地理取样覆盖约 55 米。全国沙盘使用统一显示尺度。模型局部原点对齐主体锚点，底面高度为零。出行时可分别检索“台北101购物中心停车场”与“台北101/世贸站”。

## 模型与回读结果

| 网页资产 | 版本 | 三角面 | 字节数 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [taipei-101.glb](../../../app/public/models/taipei-101.glb) | national-v1 | 3,716 | 402,424 | 6 / 6 |

实模图来自空白场景重新导入网页 GLB 后的三角度正交渲染。材质均从 GLB 内部读取。原始分组和贴图保存在[可编辑 Blender 母版](source.blend)，导出与母版的 SHA-256 记录于[实测统计](stats.json)。

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 网页预览

[全国视图](../web/全国视图.png) · [手机全国视图](../web/手机全国视图.png) · [景点斜视近景](web/斜视近景.png)

## 重建

在项目根目录使用 Blender 5.2.1。修改母版后，以下命令从已保存的分组网格导出并更新网页文件、面数和实模图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/workshop-c/build.py -- taipei-101 --from-master
```

完整重建时移除 `--from-master`。几何位于[场景脚本](../workshop-c/sites.py)，重复构件使用[几何函数](../workshop-c/geometry.py)，[导出脚本](../workshop-c/build.py)读取已备好的[原创材质贴图](../workshop-c/textures/)。如需重新生成贴图，可用带 Pillow 的 Python 执行 `python3 data/landmarks/workshop-c/surfaces.py`。
