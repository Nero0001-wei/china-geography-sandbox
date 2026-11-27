# 神农架·神农顶

最高处的石碑、起伏山脊和分布在草甸下缘的针叶林。 [实景与景区资料](https://www.fohb.gov.cn/info/2022-08/20220810160800_196.html)

以长山脊和高山草甸为主，林线向低处过渡，顶碑和沿脊步道提供定位线索。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取神农顶主峰，WGS84 **110.3072111°E、31.4399826°N**。OpenStreetMap “神农顶主峰”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/5333328928)
- 地形取样跨度约 470 米。模型正面朝 168°，从正北起顺时针计算。筛选归入自然风光与区域代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [shennongjia.glb](../../../app/public/models/shennongjia.glb) | national-v1 | 6,518 | 716,964 字节 | 14 / 5 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- shennongjia
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/summits.py) · [共用建模与导出说明](../expansion-nature/README.md)
