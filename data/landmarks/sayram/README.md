# 赛里木湖克勒涌珠

选择湖西南岸克勒涌珠，从岸石、草坡、蓝色湖面和远山截取一段典型岸线。现状湖岸景观的压缩表达。[景区或机构资料](https://www.xjboz.gov.cn/xjboz/c126221/202202/6c11b0230bb14c3aa22e87110b9ce152.shtml)

## 制作取舍

选择湖岸近景，压缩水体、石滩、地被、针叶林和远山的距离。山体用一片连续的带状网格构造，雪线随坡面变化。全国版的远景山脊是景观意象。

[ImageGen 正面、右侧和侧前方参考](reference/三视角.webp) · [提示词原文](reference/prompt.txt) · [原始三景九格图](../workshop-c/reference/B.png)

## 地理锚点

高德「赛里木湖-克勒涌珠」POI，GCJ-02（81.021960,44.561239）按项目迭代逆算为 WGS84；非测绘成果。 经纬度顺序为经度、纬度，WGS84 **81.0191847°、44.5603504°**。GLB 的局部 +Z 朝地理方位 70°，以正北为 0° 顺时针计。自然景观没有建筑正面；近侧水面朝向湖心方向，取东北偏东的示意方位。[主体定位来源](https://www.amap.com/place/B0FFG6HMNB) · [地图接入元数据](site.json)

地理取样覆盖约 350 米。全国沙盘使用统一显示尺度。模型局部原点对齐主体锚点，底面高度为零。出行时可分别检索“克勒涌珠停车场”与“克勒涌珠观光车停靠站”。

## 模型与回读结果

| 网页资产 | 版本 | 三角面 | 字节数 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [sayram.glb](../../../app/public/models/sayram.glb) | national-v1 | 7,449 | 850,780 | 9 / 9 |

实模图来自空白场景重新导入网页 GLB 后的三角度正交渲染。材质均从 GLB 内部读取。原始分组和贴图保存在[可编辑 Blender 母版](source.blend)，导出与母版的 SHA-256 记录于[实测统计](stats.json)。

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 网页预览

[全国视图](../web/全国视图.png) · [手机全国视图](../web/手机全国视图.png) · [景点斜视近景](web/斜视近景.png)

## 重建

在项目根目录使用 Blender 5.2.1。修改母版后，以下命令从已保存的分组网格导出并更新网页文件、面数和实模图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/workshop-c/build.py -- sayram --from-master
```

完整重建时移除 `--from-master`。几何位于[场景脚本](../workshop-c/sites.py)，重复构件使用[几何函数](../workshop-c/geometry.py)，[导出脚本](../workshop-c/build.py)读取已备好的[原创材质贴图](../workshop-c/textures/)。如需重新生成贴图，可用带 Pillow 的 Python 执行 `python3 data/landmarks/workshop-c/surfaces.py`。
