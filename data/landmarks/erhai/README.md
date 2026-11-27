# 大理洱海·小普陀

取洱海东侧海印村一带，湖水环绕小普陀岩屿，白墙灰瓦观音阁与远处苍山轮廓相对。 [景区与实景资料](https://www.yndali.gov.cn/dlsrmzf/c106753/2018963738441322496/wUplLX2u.pdf) · [小普陀岩岛实景](https://www.ourchinastory.com/zh/3685)

选洱海东岸的海印村，在湖面中保留独立岩岛与观音阁两重灰瓦檐。压缩远处苍山低脊，展出近岸白族民居和开阔水域。

[三视设计参考](reference/design-triplet.jpg) · [完整 ImageGen 提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点为挖色镇海印村“遥望小普陀”陆侧观景点，WGS84 **100.2225336°E、25.8096357°N**。取 OpenStreetMap 的水岸陆上观景点。小普陀岩屿距锚点约 128 米，岛屿独立留在模型湖面中。 [坐标来源](https://www.openstreetmap.org/node/6935389272)
- 主体位置另记为 **100.2219074°E、25.8106403°N**。 [主体地物来源](https://www.openstreetmap.org/way/310515894)
- 以湖岸朝向小普陀的 340° 观景方位取反，模型正面面向海印村岸侧。 地形取样跨度约 380 米，地图筛选归入自然风光与全国代表。 [元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [erhai.glb](../../../app/public/models/erhai.glb) | national-v1 | 7,690 | 834,680 字节 | 24 / 6 |

母版分组可编辑，回读实模图均由最终网页 GLB 在空白场景重新导入后渲染。[母版](source.blend) · [实测统计](stats.json)

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 重建

在项目根目录运行下列命令。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-scenic/build.py -- erhai
```

[场景源码](../expansion-scenic/natural.py) · [共用建模与导出说明](../expansion-scenic/README.md)
