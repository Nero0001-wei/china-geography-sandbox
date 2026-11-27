# 天涯海角

南海岸线上的花岗岩题刻石组和浅色沙滩。 [实景与景区资料](https://ty.sanya.gov.cn/tyqsite/jrty/202509/dd81add782f34a9d90524794f94f543e.shtml)

用海蚀花岗岩、沙滩、浅浪和椰树表现海角。两个石面的朱红题刻投影到实际石面上。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取天涯海角岸边题刻石组，WGS84 **109.3450447°E、18.2926242°N**。OpenStreetMap “天涯海角岸边题刻石组”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/2272220538)
- 地形取样跨度约 130 米。模型正面朝 161°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [tianyahaijiao.glb](../../../app/public/models/tianyahaijiao.glb) | national-v1 | 6,106 | 744,568 字节 | 16 / 7 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- tianyahaijiao
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/waters.py) · [共用建模与导出说明](../expansion-nature/README.md)
