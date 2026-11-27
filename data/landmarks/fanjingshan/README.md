# 梵净山·红云金顶

红云金顶的陡岩被深缝分开，桥连接两侧山顶殿宇。 [实景与景区资料](https://www.tongren.gov.cn/2025/0709/336936.shtml)

将红云金顶拆成两根岩柱，深缝贯穿山肩以上，两座小殿和山顶桥跨在岩柱顶部。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取红云金顶，WGS84 **108.6917029°E、27.9099965°N**。OpenStreetMap “红云金顶”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/7491142475)
- 地形取样跨度约 210 米。模型正面朝 195°，从正北起顺时针计算。筛选归入自然风光与区域代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [fanjingshan.glb](../../../app/public/models/fanjingshan.glb) | national-v1 | 6,681 | 786,336 字节 | 16 / 8 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- fanjingshan
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/summits.py) · [共用建模与导出说明](../expansion-nature/README.md)
