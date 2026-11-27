# 圣索菲亚教堂微缩模型

中央洋葱形铜绿穹顶保留轮廓分段、肋条和十字架。十字形红砖主体、侧面拱窗、阶梯与前厅钟楼分开建模。

## 实景和定位

1932 年落成的现存拜占庭式教堂；取教堂主体及入口钟楼。朝向为正立面在地图上的概略方位。 依据 OSM 教堂多边形，前部直线山墙与东侧半圆祭坛相对，前方约为西南偏西。 [实景与景区资料](https://fao.hlj.gov.cn/fao/c111834/202206/30672974/files/206c9110bd75c8a2e771b5434ffd70e9.pdf) · [OpenStreetMap 主体地物](https://www.openstreetmap.org/way/338425563)

模型原点对应 WGS84 经度 **126.62128754°**、纬度 **45.7681908°**。Blender 底面为 Z=0，正面朝 −Y；导出后 GLB 底面为 Y=0，+Z 对应地理方位约 **253°**（从正北顺时针）。用于贴地核查的主体周边范围约 54 米。[坐标与出行查询词](site.json)

在立面采用真拱廊、退开的窗芯与浅浮雕窗框。入口在半圆形祭坛对侧，大门和台阶位于模型正面。

## 参考与实模

- [ImageGen 三视图](reference/三视图.png) · [完整生成提示词](reference/prompt.txt)
- 从最终 GLB 导回 Blender 拍摄的实模图：[正面](renders/正面.png)、[右侧](renders/右侧.png)、[侧前方](renders/侧前方.png)。
- [带材质的分组母版](source.blend) · [全国版 GLB](web/saint-sophia.glb) · [网页中的同一资源](../../../app/public/models/saint-sophia.glb)

**三视角对照记录**　正面可辨门厅钟楼、两翼尖顶和中央大穹顶，右侧看见十字形向外伸出的侧堂，侧前方能区分红砖和铜绿屋面。窗列按可见尺寸合并。

## 重建

在仓库根目录运行，`blender` 为 Blender 5.2 的可执行文件。已保存的母版和 GLB 均嵌入贴图。修改脚本时可直接使用随项目保存的 [材质图](../workshop-a/textures/)；如需重制贴图，[绘制脚本](../workshop-a/textures.py) 使用 Python、Pillow 和系统中文字体。

```sh
# 从结构脚本重建母版、导出网页文件、回读成品拍摄三视图
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- saint-sophia

# 从已手动编辑并保存的母版交付同名模型
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- saint-sophia --from-master
```

[场景结构脚本](../workshop-a/models.py) · [几何与材质构件](../workshop-a/geometry.py) · [导出与实模拍摄](../workshop-a/build.py)

`national-v1` 最终文件含 **6,144 个三角面**、8 个材质、4 张嵌入贴图，大小 **459,240 字节**。校验值和局部边界见[导出统计](stats.json)。
