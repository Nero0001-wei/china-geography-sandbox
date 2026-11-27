# 宏村

宏村中心的月沼弯如新月，驳岸外列着灰瓦、白墙和阶梯状马头墙。

取 OpenStreetMap 标绘的宏村月沼水面轮廓中心。模型取月沼和池畔徽派民居，按现状外观概括各栋楼体及马头墙。 179° 为正面方位记录，跨度约 85 米。

- [实景资料](https://whc.unesco.org/en/list/1002/)
- [坐标来源](https://www.openstreetmap.org/way/1356852361)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/hongcun.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- hongcun
```
