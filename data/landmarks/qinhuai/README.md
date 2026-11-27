# 夫子庙秦淮风光带微缩模型

大照壁前用一幅原创双龙戏珠纹样表现浮雕，几何瓦垄形成檐部剪影；水面、画舫、栏板与两端岸柳单独分组。

## 实景和定位

照壁据现状，双龙照壁面向泮池和文庙；取高德「秦淮河-大成殿照壁」本体 location（GCJ-02 118.789974,32.019395），用项目的迭代函数反算 WGS84。 [实景与景区资料](https://www.kmbhxh.cn/txwm/zg/2017-03-06/147.html) · [高德主体 POI](https://ditu.amap.com/place/B00190BSEQ)

模型原点对应 WGS84 经度 **118.78477532°**、纬度 **32.02144539°**。Blender 底面为 Z=0，正面朝 −Y；导出后 GLB 底面为 Y=0，+Z 对应地理方位约 **326°**（从正北顺时针）。用于贴地核查的主体周边范围约 109 米。[坐标与出行查询词](site.json)

古画舫属于场景构图，锚点在固定的照壁本体。岸线和河宽为全国沙盘压缩。

## 参考与实模

- [ImageGen 三视图](reference/三视图.png) · [完整生成提示词](reference/prompt.txt)
- 从最终 GLB 导回 Blender 拍摄的实模图：[正面](renders/正面.png)、[右侧](renders/右侧.png)、[侧前方](renders/侧前方.png)。
- [带材质的分组母版](source.blend) · [全国版 GLB](web/qinhuai.glb) · [网页中的同一资源](../../../app/public/models/qinhuai.glb)

**三视角对照记录**　正面能同时读出双龙照壁和画舫，右侧分开墙身、河岸及船的位置，侧前方可看清画舫立柱和檐口。龙纹采用原创色图表现。

## 重建

在仓库根目录运行，`blender` 为 Blender 5.2 的可执行文件。已保存的母版和 GLB 均嵌入贴图。修改脚本时可直接使用随项目保存的 [材质图](../workshop-a/textures/)；如需重制贴图，[绘制脚本](../workshop-a/textures.py) 使用 Python、Pillow 和系统中文字体。

```sh
# 从结构脚本重建母版、导出网页文件、回读成品拍摄三视图
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- qinhuai

# 从已手动编辑并保存的母版交付同名模型
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- qinhuai --from-master
```

[场景结构脚本](../workshop-a/models.py) · [几何与材质构件](../workshop-a/geometry.py) · [导出与实模拍摄](../workshop-a/build.py)

`national-v1` 最终文件含 **6,274 个三角面**、11 个材质、6 张嵌入贴图，大小 **481,180 字节**。校验值和局部边界见[导出统计](stats.json)。
