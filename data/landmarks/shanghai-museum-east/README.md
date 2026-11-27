# 上海博物馆东馆

浦东东馆的白色大理石幕墙在方形馆体上卷起，中部通透玻璃分出上下体量。

锚点取 OpenStreetMap 所标建筑轮廓的顶点平均位置。取 2024 年全面开放的世纪大道东馆，展示朝世纪大道一侧的波浪石材与玻璃开缝。馆体与上博人民广场馆各有独立地址。 34° 为模型正面方位，地形贴合跨度按约 198 米记录。

- [实景资料](https://www.shanghaimuseum.net/mu/frontend/pg/article/id/I00004702)
- [坐标来源](https://www.openstreetmap.org/way/1034667864)
- [三视设计参考](reference/design-triplet.jpg)和[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/shanghai-museum-east.glb)和[实测统计](stats.json)
- 从全国版回读的[正面](renders/正面.png)、[右侧](renders/右侧.png)和[侧前方](renders/侧前方.png)

从项目根目录执行重建命令，使用 Blender 5.2.1 和项目内共用的城市模型导出工具。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-museum/build.py -- shanghai-museum-east
```
