# 横店影视城·秦王宫微缩模型

四海归一殿保留深色双层屋顶、宽柱列和高台，前置长阶、石栏与两侧阙楼。瓦面和砖墙使用平铺贴图，木柱保留真实透空。

## 实景和定位

1997 年为影视拍摄兴建的秦王宫景区，取四海归一殿。高德「秦王宫-四海归一殿」主体 GCJ-02 120.313282,29.136251 迭代反算；公开 OSM 主殿轮廓 686076606 与该点相邻。 按 OSM 的宫殿和两侧配殿轮廓，主轴、入口朝东南约 150°。 [实景与景区资料](https://www.hengdianworld.com/Tourist/15/) · [高德主体 POI](https://ditu.amap.com/place/B0FFF05DMT)

模型原点对应 WGS84 经度 **120.30887168°**、纬度 **29.13897336°**。Blender 底面为 Z=0，正面朝 −Y；导出后 GLB 底面为 Y=0，+Z 对应地理方位约 **150°**（从正北顺时针）。用于贴地核查的主体周边范围约 145 米。[坐标与出行查询词](site.json)

按影视城现存建筑表现。门前广场和阙楼距主殿的距离经过压缩。

## 参考与实模

- [ImageGen 三视图](reference/三视图.png) · [完整生成提示词](reference/prompt.txt)
- 从最终 GLB 导回 Blender 拍摄的实模图：[正面](renders/正面.png)、[右侧](renders/右侧.png)、[侧前方](renders/侧前方.png)。
- [带材质的分组母版](source.blend) · [全国版 GLB](web/hengdian.glb) · [网页中的同一资源](../../../app/public/models/hengdian.glb)

**三视角对照记录**　正面可辨阙楼、大殿柱列和牌匾，右侧可读双层屋面与台基，斜面仍保留入口长阶。实际更深的前庭在模型上缩短。

## 重建

在仓库根目录运行，`blender` 为 Blender 5.2 的可执行文件。已保存的母版和 GLB 均嵌入贴图。修改脚本时可直接使用随项目保存的 [材质图](../workshop-a/textures/)；如需重制贴图，[绘制脚本](../workshop-a/textures.py) 使用 Python、Pillow 和系统中文字体。

```sh
# 从结构脚本重建母版、导出网页文件、回读成品拍摄三视图
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- hengdian

# 从已手动编辑并保存的母版交付同名模型
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- hengdian --from-master
```

[场景结构脚本](../workshop-a/models.py) · [几何与材质构件](../workshop-a/geometry.py) · [导出与实模拍摄](../workshop-a/build.py)

`national-v1` 最终文件含 **4,618 个三角面**、10 个材质、6 张嵌入贴图，大小 **375,292 字节**。校验值和局部边界见[导出统计](stats.json)。
