# 东方明珠

浦东陆家嘴的东方明珠以三组斜撑托起红紫色球体，塔顶伸出细长天线。

以塔身的 Wikidata 坐标为锚点。取 1990 年代建成的电视塔主体。旋转对称的塔身从浦江岸一侧呈现。 240° 为正面方位记录，跨度约 128 米。

- [实景资料](https://www.otis.com/zh/cn/our-company/global-projects/project-showcase/oriental-pearl-tower)
- [坐标来源](https://www.wikidata.org/wiki/Q223207)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/oriental-pearl.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- oriental-pearl
```
