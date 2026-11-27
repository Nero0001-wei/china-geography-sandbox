# 武隆天生三桥

天龙桥的天然穿洞可透出峡谷，桥下保留天福官驿的一段院落。 [实景与景区资料](https://cqwl.gov.cn/bmjz_sites/bm/wlw/zwxx_98939/jqjd/jdjd_1/202007/t20200702_7634529.html)

天龙桥拱部用封闭内壁建模，保留可透背景的真正洞口。桥下有天福官驿的一段院落。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取天龙桥天然拱，WGS84 **107.7913965°E、29.4380716°N**。OpenStreetMap “天龙桥天然拱”地物，采用 WGS84 标注点；面要素采用检索API返回的代表点。 [地理坐标来源](https://www.openstreetmap.org/node/13276103456)
- 地形取样跨度约 255 米。模型正面朝 209°，从正北起顺时针计算。筛选归入自然风光与区域代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [wulong.glb](../../../app/public/models/wulong.glb) | national-v1 | 7,452 | 723,572 字节 | 13 / 5 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- wulong
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/terrain.py) · [共用建模与导出说明](../expansion-nature/README.md)
