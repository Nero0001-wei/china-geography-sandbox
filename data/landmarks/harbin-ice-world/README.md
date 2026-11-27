# 哈尔滨冰雪大世界

冰雪大世界的冬季冰塔用冰块逐层搭起，中央的尖塔周围排列多座低塔。

园区代表点。冰雕每季更新，具体主塔随届次变化。以 2025–2026 冬季第二十七届冰雪大世界的塔群为参照，概括冰晶材料和主从天际线。 167° 为正面方位记录，跨度约 240 米。

- [实景资料](https://wlt.hlj.gov.cn/wlt/c114165/202512/c00_31896256.shtml)
- [坐标来源](https://www.wikidata.org/wiki/Q10895490)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/harbin-ice-world.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- harbin-ice-world
```
