# 日月潭

从向山一带看环绕拉鲁岛的湖湾、林岸和近岸码头。 [实景与景区资料](https://www.sunmoonlake.gov.tw/zh-TW/)

模型重现开阔湖湾和独立拉鲁岛，背面植被山脊围起湖盆，岸边有短码头与小船。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取向山游客中心陆侧，WGS84 **120.9021197°E、23.8520452°N**。OpenStreetMap “向山游客中心陆侧”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/2341498877)
- 地形取样跨度约 600 米。模型正面朝 238°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [sun-moon-lake.glb](../../../app/public/models/sun-moon-lake.glb) | national-v1 | 6,816 | 797,228 字节 | 15 / 6 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- sun-moon-lake
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/waters.py) · [共用建模与导出说明](../expansion-nature/README.md)
