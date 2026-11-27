# 庐山·三叠泉

三道细长水帘沿五老峰下的岩坎和窄谷层层跌落。 [实景与景区资料](https://www.lushan.gov.cn/bmxzxxgk/bumeng/whgdxwcbj/fdzdgknr_195359/lvyou/202512/t20251231_7134056.html)

分层制作岩壁、水帘和小潭，正面能辨认三叠之间的纵深，不同宽度对应三个落水台阶。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取三叠泉主体，WGS84 **116.0275172°E、29.5660257°N**。OpenStreetMap “三叠泉主体”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/2766430360)
- 地形取样跨度约 245 米。模型正面朝 111°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [lushan.glb](../../../app/public/models/lushan.glb) | national-v1 | 6,978 | 805,304 字节 | 16 / 6 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- lushan
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/waters.py) · [共用建模与导出说明](../expansion-nature/README.md)
