# 青海湖·二郎剑

二郎剑一段狭长沙嘴伸入青海湖开阔水面。 [实景与景区资料](https://www.gonghe.gov.cn/lnb/zjgh1/stgh1__zjgh/stgh/content_1013640474)

留出大片蓝水来衬托二郎剑沙嘴。截取窄堤、浅水岸和远处低山作尺度参照。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取二郎剑景区南岸陆侧，WGS84 **100.4949253°E、36.5799889°N**。OpenStreetMap “二郎剑景区南岸陆侧”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/7867081285)
- 地形取样跨度约 650 米。模型正面朝 130°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [qinghai-lake.glb](../../../app/public/models/qinghai-lake.glb) | national-v1 | 4,450 | 331,300 字节 | 11 / 3 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- qinghai-lake
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/waters.py) · [共用建模与导出说明](../expansion-nature/README.md)
