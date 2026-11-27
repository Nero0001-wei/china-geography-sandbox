# 华山·西峰

西峰的陡直花岗岩岩壁、相连的窄脊和脊顶石道。 [实景与景区资料](https://weinan.qinfeng.gov.cn/info/1095/36343.htm)

让西峰连向后侧次峰的窄石脊留在侧前方视角。突出浅色花岗岩、窄步道和岩顶建筑。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取华山西峰，WGS84 **110.0767764°E、34.4816348°N**。OpenStreetMap “华山西峰”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/2260053392)
- 地形取样跨度约 340 米。模型正面朝 194°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [huashan.glb](../../../app/public/models/huashan.glb) | national-v1 | 6,018 | 747,208 字节 | 15 / 8 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- huashan
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/summits.py) · [共用建模与导出说明](../expansion-nature/README.md)
