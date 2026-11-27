# 侵华日军南京大屠杀遇难同胞纪念馆

江东门馆区临水西门大街，灰色题名墙、石阶和低矮陈列厅围合出安静的悼念空间。

锚点取 OpenStreetMap 所标建筑轮廓的顶点平均位置。取江东门馆区入口的悼念广场与相邻史料陈列厅，保留灰石墙、馆名、台阶和窄绿篱。入口向南朝水西门大街。 174° 为模型正面方位，地形贴合跨度按约 125 米记录。

- [实景资料](https://www.19371213.com.cn/information/news/201807/t20180712_2232683.html)
- [坐标来源](https://www.openstreetmap.org/way/992979424)
- [馆区沿革和现状](https://www.19371213.com.cn/information/news/202509/t20250905_5643460.html)
- [三视设计参考](reference/design-triplet.jpg)和[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/nanjing-massacre-memorial.glb)和[实测统计](stats.json)
- 从全国版回读的[正面](renders/正面.png)、[右侧](renders/右侧.png)和[侧前方](renders/侧前方.png)

从项目根目录执行重建命令，使用 Blender 5.2.1 和项目内共用的城市模型导出工具。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-museum/build.py -- nanjing-massacre-memorial
```

石墙题名贴图已随母版内嵌，原图可使用 `python3 data/landmarks/expansion-museum/nameplate.py --font <中文字体路径>` 重建。
