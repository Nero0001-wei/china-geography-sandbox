# 天津之眼

白色巨轮跨在海河永乐桥上，能从轮圈外辨认一圈悬挂式轿厢。

采用 Wikidata 的摩天轮主体坐标，永乐桥中段。按现状白色轮圈、三角支架和桥上轮体建模，轿厢做隔位简化。正面取海河下游方向。 149° 为正面方位记录，跨度约 165 米。

- [实景资料](https://www.tj.gov.cn/sq/yztj/jgtp/202005/t20200520_2468039.html)
- [坐标来源](https://www.wikidata.org/wiki/Q750548)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/tianjin-eye.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- tianjin-eye
```
