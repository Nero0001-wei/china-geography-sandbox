# 珠峰景区

取中国侧绒布寺一带所见的珠峰北壁和金字塔状雪峰轮廓。 [实景与景区资料](https://wlt.xizang.gov.cn/xwzx_69/jdxw/201812/t20181219_119925.html)

压缩绒布寺一带向南望去的远近距离，集中表现峰顶、北壁阴影与下方冰雪条带。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取绒布寺附近观景段，WGS84 **86.8281779°E、28.1951821°N**。OpenStreetMap “绒布寺附近观景段”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/13840969183)
- 地形取样跨度约 1400 米。模型正面朝 351°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [everest.glb](../../../app/public/models/everest.glb) | national-v1 | 7,778 | 803,564 字节 | 9 / 4 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- everest
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/summits.py) · [共用建模与导出说明](../expansion-nature/README.md)
