# 泰山南天门微缩模型

十八盘末段以连续四十二级微缩石阶引向南天门。城台留有贯通拱洞，下方是南天门匾，上方是黄瓦门楼，石坡用花岗岩与松丛分层。

## 实景和定位

泰山官方记录南天门始建于 1260 年，坐北朝南；模型取现状城门及十八盘末段，陡升的阶梯朝南。 [实景与景区资料](https://tsgw.taian.gov.cn/art/2026/3/23/art_363608_10320983.html) · [OpenStreetMap 主体地物](https://www.openstreetmap.org/way/169049697)

模型原点对应 WGS84 经度 **117.09833928°**、纬度 **36.25547791°**。Blender 底面为 Z=0，正面朝 −Y；导出后 GLB 底面为 Y=0，+Z 对应地理方位约 **180°**（从正北顺时针）。用于贴地核查的主体周边范围约 65 米。[坐标与出行查询词](site.json)

保留台阶前低后高的走向。门前石阶截取末段，长度与级数经过压缩。

## 参考与实模

- [ImageGen 三视图](reference/三视图.png) · [完整生成提示词](reference/prompt.txt)
- 从最终 GLB 导回 Blender 拍摄的实模图：[正面](renders/正面.png)、[右侧](renders/右侧.png)、[侧前方](renders/侧前方.png)。
- [带材质的分组母版](source.blend) · [全国版 GLB](web/taishan.glb) · [网页中的同一资源](../../../app/public/models/taishan.glb)

**三视角对照记录**　正面看见十八盘末段直通门洞，右侧可辨门楼位于坡顶，斜面可见黄瓦楼阁和两侧岩石。山体在南天门后方收坡，保留门楼剪影。

## 重建

在仓库根目录运行，`blender` 为 Blender 5.2 的可执行文件。已保存的母版和 GLB 均嵌入贴图。修改脚本时可直接使用随项目保存的 [材质图](../workshop-a/textures/)；如需重制贴图，[绘制脚本](../workshop-a/textures.py) 使用 Python、Pillow 和系统中文字体。

```sh
# 从结构脚本重建母版、导出网页文件、回读成品拍摄三视图
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- taishan

# 从已手动编辑并保存的母版交付同名模型
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- taishan --from-master
```

[场景结构脚本](../workshop-a/models.py) · [几何与材质构件](../workshop-a/geometry.py) · [导出与实模拍摄](../workshop-a/build.py)

`national-v1` 最终文件含 **7,678 个三角面**、12 个材质、8 张嵌入贴图，大小 **633,436 字节**。校验值和局部边界见[导出统计](stats.json)。
