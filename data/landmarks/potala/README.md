# 布达拉宫红宫与白宫

红山上红宫居中，白宫沿坡展开，金顶、窗带与折返台阶保留在全国版剪影中。以17世纪扩建后保留至今的红白宫群为参考。[景区或机构资料](https://whc.unesco.org/en/list/707/)

## 制作取舍

沿山叠放收分的白色墙体，中段压入较高的赭红宫体与小金顶。红山、侧翼、窗带和南侧折返上行的台阶按不同结构分组。

[ImageGen 正面、右侧和侧前方参考](reference/三视角.webp) · [提示词原文](reference/prompt.txt) · [原始三景九格图](../workshop-c/reference/A.png)

## 地理锚点

OpenStreetMap 布达拉宫主体建筑外沿封闭多边形的面积质心。 经纬度顺序为经度、纬度，WGS84 **91.1173514°、29.6579495°**。GLB 的局部 +Z 朝地理方位 180°，以正北为 0° 顺时针计。取面向布达拉宫广场的南立面。[主体定位来源](https://www.openstreetmap.org/way/31475419) · [地图接入元数据](site.json)

地理取样覆盖约 360 米。全国沙盘使用统一显示尺度。模型局部原点对齐主体锚点，底面高度为零。出行时可分别检索“布达拉宫西门停车场”与“布达拉宫广场公交站”。

## 模型与回读结果

| 网页资产 | 版本 | 三角面 | 字节数 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [potala.glb](../../../app/public/models/potala.glb) | national-v1 | 7,520 | 711,876 | 7 / 7 |

实模图来自空白场景重新导入网页 GLB 后的三角度正交渲染。材质均从 GLB 内部读取。原始分组和贴图保存在[可编辑 Blender 母版](source.blend)，导出与母版的 SHA-256 记录于[实测统计](stats.json)。

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 网页预览

[全国视图](../web/全国视图.png) · [手机全国视图](../web/手机全国视图.png) · [景点斜视近景](web/斜视近景.png)

## 重建

在项目根目录使用 Blender 5.2.1。修改母版后，以下命令从已保存的分组网格导出并更新网页文件、面数和实模图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/workshop-c/build.py -- potala --from-master
```

完整重建时移除 `--from-master`。几何位于[场景脚本](../workshop-c/sites.py)，重复构件使用[几何函数](../workshop-c/geometry.py)，[导出脚本](../workshop-c/build.py)读取已备好的[原创材质贴图](../workshop-c/textures/)。如需重新生成贴图，可用带 Pillow 的 Python 执行 `python3 data/landmarks/workshop-c/surfaces.py`。
