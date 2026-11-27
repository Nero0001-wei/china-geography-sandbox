# 武陵源·张家界国家森林公园

以袁家界乾坤柱（南天一柱）为中心，保留狭长直立的石英砂岩峰柱和绿顶。 [实景与景区资料](https://whhlyt.hunan.gov.cn/whhlyt/zxta/202511/t20251113_33847812.html)

以乾坤柱为高点，建一组彼此独立的柱形岩体。每座石柱的偏移、层理和顶部绿冠都有差异。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取袁家界乾坤柱，WGS84 **110.4372172°E、29.3451921°N**。OpenStreetMap “袁家界乾坤柱”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/4331753591)
- 地形取样跨度约 460 米。模型正面朝 146°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [wulingyuan.glb](../../../app/public/models/wulingyuan.glb) | national-v1 | 7,526 | 817,340 字节 | 11 / 5 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- wulingyuan
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/summits.py) · [共用建模与导出说明](../expansion-nature/README.md)
