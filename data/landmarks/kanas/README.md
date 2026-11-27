# 喀纳斯·月亮湾

从湾边的陆侧看蓝绿河水在针叶林山坡之间弯成月牙。 [实景与景区资料](https://zrzyt.xinjiang.gov.cn/xjgtzy/kpjd/202010/22b9bef9e4fc47638e7eac92c2936e47.shtml)

用林坡夹住月亮湾的曲流，浓密针叶林从水岸向高处逐步抬升。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取月亮湾东岸游览点，WGS84 **87.0471844°E、48.6345452°N**。OpenStreetMap “月亮湾东岸游览点”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/5813997974)
- 地形取样跨度约 520 米。模型正面朝 80°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [kanas.glb](../../../app/public/models/kanas.glb) | national-v1 | 7,238 | 660,876 字节 | 12 / 3 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- kanas
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/waters.py) · [共用建模与导出说明](../expansion-nature/README.md)
