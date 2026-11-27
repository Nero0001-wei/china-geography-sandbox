# 中国科学技术馆

奥林匹克公园旁的现馆有相互咬合的浅色方盒体块和深色玻璃窗，造型取意于鲁班锁。

锚点取 OpenStreetMap 所标建筑轮廓的顶点平均位置。按 2009 年开放的北辰东路现馆取景。正面取西侧公共广场，白色围合体、层间凹槽和玻璃按现状概括。 268.5° 为模型正面方位，地形贴合跨度按约 205 米记录。

- [实景资料](https://www.cstm.org.cn/gy/bggk/index.html)
- [坐标来源](https://www.openstreetmap.org/way/161298694)
- [三视设计参考](reference/design-triplet.jpg)和[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/china-science-museum.glb)和[实测统计](stats.json)
- 从全国版回读的[正面](renders/正面.png)、[右侧](renders/右侧.png)和[侧前方](renders/侧前方.png)

从项目根目录执行重建命令，使用 Blender 5.2.1 和项目内共用的城市模型导出工具。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-museum/build.py -- china-science-museum
```
