# 喀什古城

喀什古城东口的黄褐砖墙与高拱城门，是游客观看开城仪式的一处入口。

取 OpenStreetMap 喀什古城东门实体节点，正面朝东。砂黄色砖墙和拱道按保护性改造后的外观制作。 88° 为正面方位记录，跨度约 74 米。

- [实景资料](https://www.neac.gov.cn/seac/xwzx/202607/1192630.shtml)
- [坐标来源](https://www.openstreetmap.org/node/5832030085)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/kashgar-old-city.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- kashgar-old-city
```
