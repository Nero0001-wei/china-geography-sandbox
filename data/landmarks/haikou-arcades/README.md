# 海口骑楼老街

中山路一段南洋骑楼，底层是相通的遮阴拱廊，上层各有彩色窗套与山花。

主体附近的高德 POI（GCJ-02 110.343619, 20.043533）通过项目迭代转换为 WGS84。取中山路 50 号附近的街段，局部排列概括保留骑楼的连续廊道。 172° 为正面方位记录，跨度约 90 米。

- [实景资料](https://ggzy.haikou.gov.cn/gonggao/89849)
- [坐标来源](https://ditu.amap.com/place/B0FFFPCNQB)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/haikou-arcades.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- haikou-arcades
```
