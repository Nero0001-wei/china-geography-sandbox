# 长沙橘子洲

橘子洲南端的青年毛泽东艺术雕塑由花岗岩砌筑，长发轮廓远看仍可辨识。

主体附近的高德 POI（GCJ-02 112.960324, 28.167602）通过项目迭代转换为 WGS84。表现 2009 年建成的洲头雕塑与湘江水岸，近似一段洲尖地形。 140° 为正面方位记录，跨度约 130 米。

- [实景资料](https://www.hunan.gov.cn/hnszf/jxxx/hslv/c101474/202108/t20210827_20403826.html)
- [坐标来源](https://ditu.amap.com/place/B02DB0W8QW)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/orange-isle.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- orange-isle
```
