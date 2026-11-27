# 阿里山·沼平车站

沼平车站旁的弯曲窄轨、红色列车和高山杉林。 [实景与景区资料](https://www.ali-nsa.net/zh-tw/attractions/detail/176)

以沼平车站代表阿里山林业铁道，绘制沿坡地弯曲的窄轨、枕木、红色列车和针叶林。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取沼平车站站房，WGS84 **120.8138181°E、23.5145072°N**。OpenStreetMap “沼平车站站房”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/way/548338239)
- 地形取样跨度约 165 米。模型正面朝 161°，从正北起顺时针计算。筛选归入自然风光与区域代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [alishan.glb](../../../app/public/models/alishan.glb) | national-v1 | 7,688 | 806,020 字节 | 16 / 6 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- alishan
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/terrain.py) · [共用建模与导出说明](../expansion-nature/README.md)
