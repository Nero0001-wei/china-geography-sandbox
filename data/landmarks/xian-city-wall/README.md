# 西安城墙·永宁门 · 永宁门南门三重门楼

采用南门闸楼和2014年箭楼复建后的现状。 城墙南门有城楼、箭楼、闸楼三道城门，模型保留灰砖垛口、可透视券洞、瓮城和跨护城河吊桥。 [官方景点资料](https://qjxq.xa.gov.cn/zjqj/gyqj/tsqj/5df21c5565cbd81235fc1efa.html) · [建筑实景](https://commons.wikimedia.org/wiki/File:Yongningmen_2016.jpg)

## 经纬度与方向

WGS84 锚点为经度 `108.9423179`、纬度 `34.2531039`。取 OpenStreetMap 永宁门城门地标点，邻近内城墙主城楼。 [坐标来源](https://www.openstreetmap.org/node/6817037487)

自永宁门南侧护城河外朝正北看城门建筑，模型正面朝南。 地图展示方向由真北顺时针 180°，地形安置约按 200 米横向尺度采样。母版以 Z 向上、−Y 为正面，导出 GLB 以 Y 向上、+Z 为正面，底面高度为零。

## 模型与验收

- [ImageGen 正面、侧面和侧前方参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)按结构分组并打包纹理。[重建脚本](../expansion-heritage/)
- [全国版 GLB](../../../app/public/models/xian-city-wall.glb)实测 5,588 三角面、705,248 字节，含 13 张内嵌纹理。[文件统计](stats.json)
- 以下三张由最终 GLB 重新导入后渲染。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录调用 Blender 5.2 重建、导出和回读渲染。使用团队手工调整后的母版重新导出可在末尾加 `--from-master`，只回读最终 GLB 时加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-heritage/build.py -- xian-city-wall
```
