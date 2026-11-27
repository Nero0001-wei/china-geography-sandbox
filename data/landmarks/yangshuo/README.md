# 阳朔漓江·黄布倒影

取兴坪黄布倒影一段开阔静水面和连续的两岸锥状峰丛。 [实景与景区资料](https://zhuanti.mct.gov.cn/xcss2024_shjlzzxc/guangxi/detail/6871.html)

保留兴坪段两侧分布的锥状喀斯特峰丛，水面用细波和一叶竹筏表达距离。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取果农道黄布倒影观景点，WGS84 **110.5166399°E、24.9251035°N**。OpenStreetMap “果农道黄布倒影观景点”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/4376696293)
- 地形取样跨度约 600 米。模型正面朝 140°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [yangshuo.glb](../../../app/public/models/yangshuo.glb) | national-v1 | 7,690 | 832,848 字节 | 14 / 5 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- yangshuo
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/waters.py) · [共用建模与导出说明](../expansion-nature/README.md)
