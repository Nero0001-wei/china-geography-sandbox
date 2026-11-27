# 中国天眼

贵州平塘大窝凼公开科普景观，山地洼处嵌着球面反射盘，周边塔架托起中央馈源舱。 [景区与实景资料](https://www.mct.gov.cn/wlbphone/wlbydd/xxfb/qglb/gz/202205/t20220509_932857.html) · [中国科学院科普资料](https://www.cas.cn/zjs/202111/t20211124_4815660.shtml)

保护反射盘连贯的下凹轮廓。模型可看到公开科普视角内的六座支撑塔、牵索和悬空馈源舱，锚定大窝凼的主体。

[三视设计参考](reference/design-triplet.jpg) · [完整 ImageGen 提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点为贵州平塘大窝凼球面天线，WGS84 **106.8565670°E、25.6528526°N**。取 OpenStreetMap 五百米口径球面射电望远镜轮廓的代表点，用作地理展示。 [坐标来源](https://www.openstreetmap.org/way/384699313)
- 局部正面指向西北的公开观景方向。 地形取样跨度约 680 米，地图筛选归入城市与工程地标与全国代表。 [元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [fast-observatory.glb](../../../app/public/models/fast-observatory.glb) | national-v1 | 7,690 | 773,492 字节 | 16 / 3 |

母版分组可编辑，回读实模图均由最终网页 GLB 在空白场景重新导入后渲染。[母版](source.blend) · [实测统计](stats.json)

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 重建

在项目根目录运行下列命令。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-scenic/build.py -- fast-observatory
```

[场景源码](../expansion-scenic/structures.py) · [共用建模与导出说明](../expansion-scenic/README.md)
