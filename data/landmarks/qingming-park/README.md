# 开封清明上河园

清明上河园的汴河上横跨一座大跨度木虹桥，两岸布置宋式街屋和小船。

以清明上河园 Wikidata 园区坐标为锚点。表现依《清明上河图》建造的景区现状。虹桥为真正镂空的单跨，木格与街屋按全国视角简化。 180° 为正面方位记录，跨度约 118 米。

- [实景资料](https://www.shunhequ.gov.cn/kfsshhzqwz/c00314/pc/content/content_1909548820819951616.html)
- [坐标来源](https://www.wikidata.org/wiki/Q15909131)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/qingming-park.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- qingming-park
```
