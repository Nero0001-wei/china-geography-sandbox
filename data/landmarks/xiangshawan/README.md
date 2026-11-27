# 响沙湾

库布齐沙漠边连续弯曲的陡沙脊，近处以小驼队表现坡度。 [实景与景区资料](https://www.xiangsw.com/xsw/about/about-2.html)

沙脊用闭合的非对称坡面建模，迎风面较长，背风面陡急，前缘留小驼队作比例参照。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取达拉特旗响沙湾景区，WGS84 **109.9309886°E、40.2539701°N**。高德“达拉特旗响沙湾景区”POI，GCJ-02（109.936583，40.254903）按项目函数反算 WGS84，作为展示锚点。 [地理坐标来源](https://www.amap.com/place/B01DD008IM)
- 地形取样跨度约 540 米。模型正面朝 42°，从正北起顺时针计算。筛选归入自然风光与区域代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [xiangshawan.glb](../../../app/public/models/xiangshawan.glb) | national-v1 | 7,468 | 733,368 字节 | 7 / 1 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- xiangshawan
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/terrain.py) · [共用建模与导出说明](../expansion-nature/README.md)
