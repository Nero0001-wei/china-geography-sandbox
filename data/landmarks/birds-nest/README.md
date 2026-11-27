# 鸟巢

北京国家体育场的银灰钢桁架围绕椭圆形看台交织，屋面中央敞开，可以看到红色看台和场地。

锚点取 OpenStreetMap 所标建筑轮廓的顶点平均位置。取奥林匹克公园内的国家体育场现状。保持南北向长轴，从南侧广场看，椭圆屋口与外圈钢构均保留真实几何间隙。 178.5° 为模型正面方位，地形贴合跨度按约 333 米记录。

- [实景资料](https://www.n-s.cn/visitindex.html)
- [坐标来源](https://www.openstreetmap.org/way/152301551)
- [三视设计参考](reference/design-triplet.jpg)和[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/birds-nest.glb)和[实测统计](stats.json)
- 从全国版回读的[正面](renders/正面.png)、[右侧](renders/右侧.png)和[侧前方](renders/侧前方.png)

从项目根目录执行重建命令，使用 Blender 5.2.1 和项目内共用的城市模型导出工具。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-museum/build.py -- birds-nest
```
