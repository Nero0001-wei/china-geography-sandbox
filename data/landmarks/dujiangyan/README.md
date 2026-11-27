# 都江堰

鱼嘴分水堤像一段尖楔，伸入岷江并把河水分为内江和外江。

以 OpenStreetMap 鱼嘴节点定位分水堤尖端，并用相邻实景核对方位。表现现状鱼嘴、内外江和短段安澜索桥，分水尖端在正面。 320° 为正面方位记录，跨度约 220 米。

- [实景资料](https://whc.unesco.org/en/list/1001/)
- [坐标来源](https://www.openstreetmap.org/node/5845822640)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/dujiangyan.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- dujiangyan
```
