# 呼伦贝尔草原·莫尔格勒河

从阿吉奈观景台截取草甸中的连续河曲，明绿缓坡衬出蓝色回弯。 [实景与景区资料](https://sjfw.mct.gov.cn/site/dataservice/culdetails?curId=10&id=34822)

河水贯穿底座，用连续回转的窄水带呈现莫尔格勒河的曲流，缓坡以低矮地被与小牛马衬托。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取阿吉奈观景台，WGS84 **119.9343498°E、49.5788264°N**。高德“阿吉奈观景台”POI，GCJ-02（119.941342，49.580548）按项目函数反算 WGS84，作为展示锚点。 [地理坐标来源](https://www.amap.com/place/B0JUFUGA3E)
- 地形取样跨度约 1100 米。模型正面朝 128°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [hulunbuir.glb](../../../app/public/models/hulunbuir.glb) | national-v1 | 4,458 | 418,108 字节 | 11 / 2 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- hulunbuir
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/waters.py) · [共用建模与导出说明](../expansion-nature/README.md)
