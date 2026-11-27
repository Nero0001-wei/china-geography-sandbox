# 黄果树瀑布

截取弧面的宽主瀑、崖下犀牛潭与台地上的林缘。 [实景与景区资料](https://www.eco.gov.cn/news_info/40420.html)

表达黔中植被包围的钙华台地，以及从弧形崖檐落向犀牛潭的宽瀑。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取黄果树主瀑，WGS84 **105.6661996°E、25.9924212°N**。OpenStreetMap “黄果树主瀑”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/2932278086)
- 地形取样跨度约 240 米。模型正面朝 133°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [huangguoshu.glb](../../../app/public/models/huangguoshu.glb) | national-v1 | 5,834 | 667,372 字节 | 15 / 5 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- huangguoshu
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/waters.py) · [共用建模与导出说明](../expansion-nature/README.md)
