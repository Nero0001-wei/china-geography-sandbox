# 三星堆博物馆

三星堆博物馆新馆由几座倾斜堆体组成，覆土坡面与带铜色的折线立面相接。

主体附近的高德 POI（GCJ-02 104.218621, 31.001439）通过项目迭代转换为 WGS84。模型取 2023 年开放的新馆，保留连续堆体和青铜色细分立面。前庭纹样是缩尺识别标志。 215° 为正面方位记录，跨度约 280 米。

- [实景资料](https://www.mct.gov.cn/wlbphone/wlbydd/xxfb/qglb/sc/202308/t20230801_946332.html)
- [坐标来源](https://ditu.amap.com/place/B034600ZUS)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/sanxingdui.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- sanxingdui
```
