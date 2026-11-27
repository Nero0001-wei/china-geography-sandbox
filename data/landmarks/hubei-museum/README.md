# 湖北省博物馆

在东湖边的南馆，浅色外挑馆体像一口巨鼎。玻璃中庭之后是北馆深色的层叠楚式屋檐。

锚点取 OpenStreetMap 所标建筑轮廓的顶点平均位置。锚点对应 2021 年开放的文展大楼南主馆。由南侧入口广场向馆区取景，保留浅色倾斜外墙、玻璃凹口和后方北馆的主要屋檐。 152° 为模型正面方位，地形贴合跨度按约 160 米记录。

- [实景资料](https://wlt.hubei.gov.cn/bmdt/xydt/202111/t20211112_3859467.shtml)
- [坐标来源](https://www.openstreetmap.org/way/953408416)
- [三视设计参考](reference/design-triplet.jpg)和[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/hubei-museum.glb)和[实测统计](stats.json)
- 从全国版回读的[正面](renders/正面.png)、[右侧](renders/右侧.png)和[侧前方](renders/侧前方.png)

从项目根目录执行重建命令，使用 Blender 5.2.1 和项目内共用的城市模型导出工具。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-museum/build.py -- hubei-museum
```
