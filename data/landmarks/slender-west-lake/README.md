# 扬州瘦西湖

瘦西湖莲花埂上的五亭桥，五座黄琉璃瓦亭分列桥身，桥券跨水相连。

取 OpenStreetMap 五亭桥主体中心，方位按湖中步桥南北两端校正。表现清乾隆年间所建五亭桥的现状。正面取湖上观赏侧，保留主跨和侧跨的镂空。 258.5° 为正面方位记录，跨度约 70 米。

- [实景资料](https://www.jsrd.gov.cn/qwfb/d_sjfg/202512/t20251229_1191953.shtml)
- [坐标来源](https://www.openstreetmap.org/way/1058957656)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/slender-west-lake.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- slender-west-lake
```
