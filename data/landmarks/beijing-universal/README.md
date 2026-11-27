# 北京环球度假区微缩模型

将金色大陆轮廓以经纬 UV 贴在蓝色球体上，绕球的浮字具有真实厚度。可单独编辑环形喷泉、支座、水柱、球体和环绕字。

## 实景和定位

2021 年开园的北京环球度假区；选择城市大道地球雕塑，正侧取景按城市大道游人一侧，旋转地球无固定正面。 [实景与景区资料](https://www.universalbeijingresort.com/zh_CN) · [OpenStreetMap 主体地物](https://www.openstreetmap.org/node/8568400246)

模型原点对应 WGS84 经度 **116.6709294°**、纬度 **39.8511332°**。Blender 底面为 Z=0，正面朝 −Y；导出后 GLB 底面为 Y=0，+Z 对应地理方位约 **165°**（从正北顺时针）。用于贴地核查的主体周边范围约 35 米。[坐标与出行查询词](site.json)

球体取静态瞬间。局部正面朝向喷泉前的城市大道视点。大陆图形来自公版 [Natural Earth 1:110m Land](https://www.naturalearthdata.com/downloads/110m-physical-vectors/110m-land/)。

## 参考与实模

- [ImageGen 三视图](reference/三视图.png) · [完整生成提示词](reference/prompt.txt)
- 从最终 GLB 导回 Blender 拍摄的实模图：[正面](renders/正面.png)、[右侧](renders/右侧.png)、[侧前方](renders/侧前方.png)。
- [带材质的分组母版](source.blend) · [全国版 GLB](web/beijing-universal.glb) · [网页中的同一资源](../../../app/public/models/beijing-universal.glb)

**三视角对照记录**　正面可读金属环带字，侧面可见地球图和环带的倾角，侧前方能辨认环形喷水池。全国版把喷泉水雾归纳为一圈弧形水柱。

## 重建

在仓库根目录运行，`blender` 为 Blender 5.2 的可执行文件。已保存的母版和 GLB 均嵌入贴图。修改脚本时可直接使用随项目保存的 [材质图](../workshop-a/textures/)；如需重制贴图，[绘制脚本](../workshop-a/textures.py) 使用 Python、Pillow 和系统中文字体。

```sh
# 从结构脚本重建母版、导出网页文件、回读成品拍摄三视图
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- beijing-universal

# 从已手动编辑并保存的母版交付同名模型
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- beijing-universal --from-master
```

[场景结构脚本](../workshop-a/models.py) · [几何与材质构件](../workshop-a/geometry.py) · [导出与实模拍摄](../workshop-a/build.py)

`national-v1` 最终文件含 **7,268 个三角面**、8 个材质、3 张嵌入贴图，大小 **624,132 字节**。校验值和局部边界见[导出统计](stats.json)。
