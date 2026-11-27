# 凤凰古城

沱江虹桥的石拱托起双层廊楼，与外侧沿江吊脚楼遥相呼应。

取 OpenStreetMap 虹桥线两端的中点。模型表现现状双层风雨楼和两岸吊脚楼。正面从沱江上游沿河观看。 281.4° 为正面方位记录，跨度约 98 米。

- [实景资料](https://www.hnrd.gov.cn/content/2006/07/22/7267206.html)
- [坐标来源](https://www.openstreetmap.org/way/286788519)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/fenghuang.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- fenghuang
```
