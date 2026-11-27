# 南京博物院

历史馆的仿辽屋面很宽，金色琉璃瓦下排列朱柱，门前有宽阶和石台基。

取 OpenStreetMap 标绘的历史馆建筑轮廓中心。取中山东路院区历史馆现状。保留梁思成等参与设计的仿辽轮廓，正面朝向中山东路。 185° 为正面方位记录，跨度约 112 米。

- [实景资料](https://www.njmuseum.org.cn/)
- [坐标来源](https://www.openstreetmap.org/way/1517447675)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/nanjing-museum.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- nanjing-museum
```
