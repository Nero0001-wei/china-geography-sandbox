# 德天跨国瀑布

归春河中国一侧密林台地上错落的三级瀑布和碧水。 [实景与景区资料](https://eco.gov.cn/news_info/40720.html)

将归春河中方一侧的瀑崖拆为不同宽度的三级，青绿水面和台地森林包住白色瀑帘。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取中国侧德天瀑布，WGS84 **106.7231618°E、22.8558796°N**。OpenStreetMap “中国侧德天瀑布”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/7712684163)
- 地形取样跨度约 270 米。模型正面朝 142°，从正北起顺时针计算。筛选归入自然风光与区域代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [detian.glb](../../../app/public/models/detian.glb) | national-v1 | 6,046 | 668,852 字节 | 17 / 6 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- detian
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/waters.py) · [共用建模与导出说明](../expansion-nature/README.md)
