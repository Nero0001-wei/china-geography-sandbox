# 张掖七彩丹霞

从七彩虹霞台一带截取起伏山岭和横切坡面的斜向彩色沉积岩带。 [实景与景区资料](https://www.zhangye.gov.cn/chzy/zyly/ajjq/202303/t20230318_1007476_ghb.html)

地表颜色沿倾斜地层划分，使得同一色带连续跨过相邻坡面和低谷。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取七彩虹霞台一带，WGS84 **100.0597949°E、38.9596594°N**。高德“七彩虹霞台一带”POI，GCJ-02（100.06149，38.960327）按项目函数反算 WGS84，作为展示锚点。 [地理坐标来源](https://www.amap.com/place/B0FFL1PFKE)
- 地形取样跨度约 400 米。模型正面朝 207°，从正北起顺时针计算。筛选归入自然风光与区域代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [zhangye-danxia.glb](../../../app/public/models/zhangye-danxia.glb) | national-v1 | 7,090 | 756,472 字节 | 10 / 2 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- zhangye-danxia
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/terrain.py) · [共用建模与导出说明](../expansion-nature/README.md)
