# 玉龙雪山

保留扇子陡黑灰峭壁、浅蓝冰川和成带的白雪。 [实景与景区资料](https://lcj.yn.gov.cn/special/2025/0507/6576.html)

用不对称的主峰和侧峰表现扇子陡的高处岩脊，冰川带在裸露灰岩之间向下延伸。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取主峰扇子陡，WGS84 **100.1767026°E、27.0984141°N**。OpenStreetMap “主峰扇子陡”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/298460509)
- 地形取样跨度约 850 米。模型正面朝 132°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [yulong.glb](../../../app/public/models/yulong.glb) | national-v1 | 7,368 | 861,224 字节 | 13 / 6 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- yulong
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/summits.py) · [共用建模与导出说明](../expansion-nature/README.md)
