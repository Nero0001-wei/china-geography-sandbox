# 台北故宫博物院

北部院区正馆立在白色平台上，中央重檐铺绿色琉璃瓦，两翼向侧面展开。

取北部院区主建筑坐标。取 1965 年开馆的北部院区正馆现状，保留中轴阶梯和绿色重檐。 188° 为正面方位记录，跨度约 150 米。

- [实景资料](https://south.npm.gov.tw/Uploads/files/%E6%95%85%E5%AE%AE%E5%A5%BD%E5%AE%A2%20%E4%B8%AD%E6%96%87%E6%89%8B%E5%86%8A0113.pdf)
- [坐标来源](https://www.wikidata.org/wiki/Q540668)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/taipei-palace.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- taipei-palace
```
