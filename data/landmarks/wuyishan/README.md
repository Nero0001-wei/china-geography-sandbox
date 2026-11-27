# 武夷山·九曲溪

取九曲溪畔的玉女峰，保留丰厚的红砂岩体、林顶和近水竹筏。 [实景与景区资料](https://wysgjgy.fujian.gov.cn/yxgy/gyjg/201710/t20171025_5511573.htm)

把玉女峰的红砂岩层与顶端植被留在九曲溪边，平水面上放置短竹筏。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取玉女峰，WGS84 **117.9514525°E、27.6438844°N**。OpenStreetMap “玉女峰”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/2659004065)
- 地形取样跨度约 320 米。模型正面朝 133°，从正北起顺时针计算。筛选归入自然风光与区域代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [wuyishan.glb](../../../app/public/models/wuyishan.glb) | national-v1 | 5,432 | 545,520 字节 | 14 / 3 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- wuyishan
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/waters.py) · [共用建模与导出说明](../expansion-nature/README.md)
