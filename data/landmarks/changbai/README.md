# 长白山天池

从长白山北坡一侧看深蓝色火山口湖、雪线和环形陡壁。 [实景与景区资料](https://www.changbaishan.gov.cn/zbsly/lyzn/bpgl/202108/t20210816_210159.html)

地形沿北坡视点围合深蓝湖盆。火山口山脊留出错落高差，积雪集中于陡壁高处。 [造型参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点取北坡天文峰观景点，WGS84 **128.0663091°E、42.0257994°N**。OpenStreetMap 北坡天文峰观景点，WGS84。与去哪儿路线对同一观景点给出的经纬度相差约 8 米。 [地理坐标来源](https://www.openstreetmap.org/node/5258261080)
- 地形取样跨度约 1000 米。模型正面朝 5°，从正北起顺时针计算。筛选归入自然风光与全国代表。 [地图元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [changbai.glb](../../../app/public/models/changbai.glb) | national-v1 | 3,236 | 395,240 字节 | 11 / 6 |

可编辑母版按结构分组。实模图由空白场景重新导入网页 GLB，以柔和日光进行正交渲染。 [Blender 母版](source.blend) · [实测统计](stats.json)

[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

## 重建

在项目根目录执行以下命令，可重建母版、网页模型和回读图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- changbai
```

从已编辑的母版重新导出时附加 `--from-master`。 [场景代码](../expansion-nature/summits.py) · [共用建模与导出说明](../expansion-nature/README.md)
