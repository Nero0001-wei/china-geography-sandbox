# 广州长隆野生动物世界

入口的雨林风格门楼和长颈鹿活动场组成微缩场景，反映园内可见的观赏体验。

主体附近的高德 POI（GCJ-02 113.320946, 22.998894）通过项目迭代转换为 WGS84。模型以南入口定位，旁置园中代表性的长颈鹿展区意象，动物展区距离与方位作缩尺重组。 173° 为正面方位记录，跨度约 112 米。

- [实景资料](https://www.chimelong.com/gz/safaripark/exhibition/)
- [坐标来源](https://ditu.amap.com/place/B0FFHYNZMU)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/chimelong-safari.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- chimelong-safari
```
