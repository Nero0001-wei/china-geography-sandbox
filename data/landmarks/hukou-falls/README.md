# 黄河壶口瀑布

横跨陕西宜川与山西吉县的黄河壶口，宽阔黄褐急流在砂岩台地前收进狭长石槽。 [景区与实景资料](https://www.mct.gov.cn/wlbphone/wlbydd/xxfb/qglb/sx/202208/t20220809_935221.html) · [陕晋黄河景观资料](https://www.mct.gov.cn/whzx/qgwhxxlb/sx_7740/202207/t20220725_934888.htm)

宽黄褐水面在岸岩之间收束为瀑帘，落入纵向的窄槽。河槽两侧留出地层的水平断口，瀑脚用浅黄色涌浪突出。

[三视设计参考](reference/design-triplet.jpg) · [完整 ImageGen 提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点为陕西宜川侧靠主瀑的基岩台沿，WGS84 **110.4437736°E、36.1486169°N**。取 OpenStreetMap 黄河西岸崖壁线 way/461534452 上的陆岸标注点。主瀑节点位于黄河水中，模型陆侧锚与主瀑节点相距约 16 米。 [坐标来源](https://www.openstreetmap.org/node/13136496680)
- 主体位置另记为 **110.4439195°E、36.1487029°N**。 [主体地物来源](https://www.openstreetmap.org/node/313159165)
- 正面朝黄河下游，表现宜川与吉县之间的同一处瀑布。 地形取样跨度约 340 米，地图筛选归入自然风光与全国代表。 [元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [hukou-falls.glb](../../../app/public/models/hukou-falls.glb) | national-v1 | 7,690 | 752,844 字节 | 13 / 0 |

母版分组可编辑，回读实模图均由最终网页 GLB 在空白场景重新导入后渲染。[母版](source.blend) · [实测统计](stats.json)

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 重建

在项目根目录运行下列命令。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-scenic/build.py -- hukou-falls
```

[场景源码](../expansion-scenic/natural.py) · [共用建模与导出说明](../expansion-scenic/README.md)
