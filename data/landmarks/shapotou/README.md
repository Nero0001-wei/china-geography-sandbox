# 沙坡头

腾格里沙坡在黄河弯道前陡然收住，水面保留羊皮筏。 [实景与景区资料](https://www.forestry.gov.cn/c/www/hmgzdt/524437.jhtml)

用腾格里沙丘陡坡和黄河转弯的狭长水面区分于响沙湾，岸边保留窄绿带与小羊皮筏。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取沙坡头黄河旅游区，WGS84 **104.9954087°E、37.4659276°N**。OpenStreetMap “沙坡头黄河旅游区”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/relation/9075585)
- 地形取样跨度约 480 米。模型正面朝 180°，从正北起顺时针计算。筛选归入自然风光与区域代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [shapotou.glb](../../../app/public/models/shapotou.glb) | national-v1 | 7,192 | 769,804 字节 | 13 / 3 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- shapotou
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/terrain.py) · [共用建模与导出说明](../expansion-nature/README.md)
