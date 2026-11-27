# 鸣沙山月牙泉

低伏的新月形泉水夹在弧形沙脊与楼阁之间。 [实景与景区资料](https://www.forestry.gov.cn/c/www/lcdt/516966.jhtml)

将新月轮廓落在连绵沙脊的凹地中，沿泉边保留小楼与苇岸。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取月牙泉泉盆，WGS84 **94.6693085°E、40.0873683°N**。OpenStreetMap “月牙泉泉盆”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/way/1308452182)
- 地形取样跨度约 340 米。模型正面朝 174°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [crescent-lake.glb](../../../app/public/models/crescent-lake.glb) | national-v1 | 7,180 | 765,092 字节 | 15 / 5 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- crescent-lake
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/terrain.py) · [共用建模与导出说明](../expansion-nature/README.md)
