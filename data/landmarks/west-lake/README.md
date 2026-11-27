# 杭州西湖·三潭印月微缩模型

三塔按湖面上的三角形布置。每塔球腹有五个真圆形开口，塔腹、外挑石檐和葫芦尖分层建模，湖面保留塔周水纹。

## 实景和定位

三潭石塔群位于小瀛洲以南，用三座石塔群的 OSM 点作为模型原点。三足排列可用 OSM 地物 975360500、975360501、975360502 复核。正面取向按三塔在湖面上的相对位置。 [实景与景区资料](https://whc.unesco.org/en/list/1334/) · [OpenStreetMap 主体地物](https://www.openstreetmap.org/node/9025997767)

模型原点对应 WGS84 经度 **120.139741°**、纬度 **30.2394106°**。Blender 底面为 Z=0，正面朝 −Y；导出后 GLB 底面为 Y=0，+Z 对应地理方位约 **180°**（从正北顺时针）。用于贴地核查的主体周边范围约 65 米。[坐标与出行查询词](site.json)

塔间距等比缩短、单塔适当放大，以便全国图上识别。中心为三塔群标记，三座塔的真实相对方位保留。

## 参考与实模

- [ImageGen 三视图](reference/三视图.png) · [完整生成提示词](reference/prompt.txt)
- 从最终 GLB 导回 Blender 拍摄的实模图：[正面](renders/正面.png)、[右侧](renders/右侧.png)、[侧前方](renders/侧前方.png)。
- [带材质的分组母版](source.blend) · [全国版 GLB](web/west-lake.glb) · [网页中的同一资源](../../../app/public/models/west-lake.glb)

**三视角对照记录**　正面和右侧可从不同球腹开口看到暗面，侧前方可确认三座塔的三角排列。倒影和湖面面积按小比例沙盘简化。

## 重建

在仓库根目录运行，`blender` 为 Blender 5.2 的可执行文件。已保存的母版和 GLB 均嵌入贴图。修改脚本时可直接使用随项目保存的 [材质图](../workshop-a/textures/)；如需重制贴图，[绘制脚本](../workshop-a/textures.py) 使用 Python、Pillow 和系统中文字体。

```sh
# 从结构脚本重建母版、导出网页文件、回读成品拍摄三视图
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- west-lake

# 从已手动编辑并保存的母版交付同名模型
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- west-lake --from-master
```

[场景结构脚本](../workshop-a/models.py) · [几何与材质构件](../workshop-a/geometry.py) · [导出与实模拍摄](../workshop-a/build.py)

`national-v1` 最终文件含 **6,296 个三角面**、4 个材质、3 张嵌入贴图，大小 **457,468 字节**。校验值和局部边界见[导出统计](stats.json)。
