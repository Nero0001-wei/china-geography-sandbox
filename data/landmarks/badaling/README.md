# 八达岭长城微缩模型

沿山脊连续布置雉堞、女墙和步道，在中央北四楼与西侧次楼各保留双拱窗。山体用分面山脊、岩块和松丛表现。

## 实景和定位

明代八达岭长城现存北段；取北四楼及其相邻一段城墙，东北上行坡用微缩起伏概括。 [实景与景区资料](https://www.visitbeijing.com.cn/article/47QqxoCnUj8) · [OpenStreetMap 主体地物](https://www.openstreetmap.org/way/1250479562)

模型原点对应 WGS84 经度 **116.0117463°**、纬度 **40.3564787°**。Blender 底面为 Z=0，正面朝 −Y；导出后 GLB 底面为 Y=0，+Z 对应地理方位约 **159°**（从正北顺时针）。用于贴地核查的主体周边范围约 145 米。[坐标与出行查询词](site.json)

走墙和相邻敌楼间距按展示比例压缩。东北侧为上行方向，东南侧可看见敌楼正立面。

## 参考与实模

- [ImageGen 三视图](reference/三视图.png) · [完整生成提示词](reference/prompt.txt)
- 从最终 GLB 导回 Blender 拍摄的实模图：[正面](renders/正面.png)、[右侧](renders/右侧.png)、[侧前方](renders/侧前方.png)。
- [带材质的分组母版](source.blend) · [全国版 GLB](web/badaling.glb) · [网页中的同一资源](../../../app/public/models/badaling.glb)

**三视角对照记录**　正面能辨认两座双拱敌楼，右侧看到通行的城墙顶面，斜面保留起伏的山脊和两侧石坡。墙脚埋入山坡，裸露端头有封墙。

## 重建

在仓库根目录运行，`blender` 为 Blender 5.2 的可执行文件。已保存的母版和 GLB 均嵌入贴图。修改脚本时可直接使用随项目保存的 [材质图](../workshop-a/textures/)；如需重制贴图，[绘制脚本](../workshop-a/textures.py) 使用 Python、Pillow 和系统中文字体。

```sh
# 从结构脚本重建母版、导出网页文件、回读成品拍摄三视图
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- badaling

# 从已手动编辑并保存的母版交付同名模型
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- badaling --from-master
```

[场景结构脚本](../workshop-a/models.py) · [几何与材质构件](../workshop-a/geometry.py) · [导出与实模拍摄](../workshop-a/build.py)

`national-v1` 最终文件含 **7,333 个三角面**、7 个材质、5 张嵌入贴图，大小 **575,376 字节**。校验值和局部边界见[导出统计](stats.json)。
