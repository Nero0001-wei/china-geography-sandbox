# 湖南省博物馆

长沙主馆以宽阔悬挑为中央门厅遮覆，两翼石墙夹着玻璃立面，前方木栈接到浅水池。

锚点取 OpenStreetMap 所标建筑轮廓的顶点平均位置。取东风路主馆现状，以东风路一侧为正面。2025 年 10 月由「湖南博物院」更名为「湖南省博物馆」。 266° 为模型正面方位，地形贴合跨度按约 180 米记录。

- [实景资料](https://www.hunan.gov.cn/hnszf/jxxx/hslv/c101474/202108/t20210827_20401957.html)
- [坐标来源](https://www.openstreetmap.org/way/269856520)
- [2025 年更名公告](https://whhlyt.hunan.gov.cn/whhlyt/news/gzdt/202510/t20251013_33823787.html)
- [三视设计参考](reference/design-triplet.jpg)和[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/hunan-museum.glb)和[实测统计](stats.json)
- 从全国版回读的[正面](renders/正面.png)、[右侧](renders/右侧.png)和[侧前方](renders/侧前方.png)

从项目根目录执行重建命令，使用 Blender 5.2.1 和项目内共用的城市模型导出工具。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-museum/build.py -- hunan-museum
```
