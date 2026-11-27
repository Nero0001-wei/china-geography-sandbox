# 昆明石林·阿诗玛

在小石林的灰色剑峰中突出阿诗玛石峰略向前倾的轮廓。 [实景与景区资料](https://zhuanti.mct.gov.cn/xcszbwg2022/yunnan/detail/1993.html)

取阿诗玛主峰的偏折轮廓和周围高低不同的岩刃，地表添加稀疏植被与碎石。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取小石林阿诗玛，WGS84 **103.3274966°E、24.8201062°N**。OpenStreetMap “小石林阿诗玛”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/12241708494)
- 地形取样跨度约 110 米。模型正面朝 182°，从正北起顺时针计算。筛选归入自然风光与区域代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [stone-forest.glb](../../../app/public/models/stone-forest.glb) | national-v1 | 6,144 | 778,324 字节 | 15 / 7 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- stone-forest
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/terrain.py) · [共用建模与导出说明](../expansion-nature/README.md)
