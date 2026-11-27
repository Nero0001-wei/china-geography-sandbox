# 峨眉山·金顶

金顶的白石台基、金色殿宇和临崖向下的山体。 [实景与景区资料](https://www.emeishan.gov.cn/emss/efbf/2023022214035442128800000.html)

保留作为远观识别线索的金色殿宇与白石台基，下部是起伏山肩和裸岩。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取峨眉金顶，WGS84 **103.3371337°E、29.5227629°N**。OpenStreetMap “峨眉金顶”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/2902204708)
- 地形取样跨度约 215 米。模型正面朝 132°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [emei.glb](../../../app/public/models/emei.glb) | national-v1 | 6,212 | 767,128 字节 | 15 / 8 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- emei
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/summits.py) · [共用建模与导出说明](../expansion-nature/README.md)
