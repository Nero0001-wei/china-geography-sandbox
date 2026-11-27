# 上海迪士尼度假区微缩模型

八座不同高度的粉色、米白塔身逐层退台，渐收的蓝色塔帽与镀金尖顶构成城堡轮廓。门前的尖山花和真拱洞可从正面辨认。

## 实景和定位

2016 年开放的奇幻童话城堡，正面取面向奇想花园入口的一侧。 [实景与景区资料](https://www.shanghaidisneyresort.com/zh-cn/experience/attraction/enchanted-storybook-castle) · [OpenStreetMap 主体地物](https://www.openstreetmap.org/way/494348161)

模型原点对应 WGS84 经度 **121.65532471°**、纬度 **31.14574596°**。Blender 底面为 Z=0，正面朝 −Y；导出后 GLB 底面为 Y=0，+Z 对应地理方位约 **171°**（从正北顺时针）。用于贴地核查的主体周边范围约 98 米。[坐标与出行查询词](site.json)

取奇幻童话城堡面向奇想花园的立面。各塔层、连廊和翼部按沙盘视角简化。

## 参考与实模

- [ImageGen 三视图](reference/三视图.png) · [完整生成提示词](reference/prompt.txt)
- 从最终 GLB 导回 Blender 拍摄的实模图：[正面](renders/正面.png)、[右侧](renders/右侧.png)、[侧前方](renders/侧前方.png)。
- [带材质的分组母版](source.blend) · [全国版 GLB](web/shanghai-disney.glb) · [网页中的同一资源](../../../app/public/models/shanghai-disney.glb)

**三视角对照记录**　正面看得到拱门周围的两座前塔，右侧确认前后塔群错落，侧前方可分清蓝色塔帽与金色尖山花。中央主塔架在通道上方，首层留空。

## 重建

在仓库根目录运行，`blender` 为 Blender 5.2 的可执行文件。已保存的母版和 GLB 均嵌入贴图。修改脚本时可直接使用随项目保存的 [材质图](../workshop-a/textures/)；如需重制贴图，[绘制脚本](../workshop-a/textures.py) 使用 Python、Pillow 和系统中文字体。

```sh
# 从结构脚本重建母版、导出网页文件、回读成品拍摄三视图
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- shanghai-disney

# 从已手动编辑并保存的母版交付同名模型
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- shanghai-disney --from-master
```

[场景结构脚本](../workshop-a/models.py) · [几何与材质构件](../workshop-a/geometry.py) · [导出与实模拍摄](../workshop-a/build.py)

`national-v1` 最终文件含 **4,870 个三角面**、6 个材质、2 张嵌入贴图，大小 **340,700 字节**。校验值和局部边界见[导出统计](stats.json)。
