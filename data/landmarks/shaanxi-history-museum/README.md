# 陕西历史博物馆本馆 · 小寨本馆中轴殿堂

按1991年开放的陕西历史博物馆小寨本馆布局。 小寨本馆以唐风中轴殿堂、四隅崇楼和两侧廊屋围合，保留灰黑瓦面与浅色石柱。 [官方景点资料](https://www.sxhm.com/history.html?_isa=1) · [建筑实景](https://commons.wikimedia.org/wiki/File:%E9%99%95%E5%8E%86%E5%8D%9A%E5%86%85%E9%83%A803.jpg)

## 经纬度与方向

WGS84 锚点为经度 `108.95052928`、纬度 `34.22568146`。取小寨馆区中央序厅的 OpenStreetMap 建筑轮廓中心。 [坐标来源](https://www.openstreetmap.org/way/1419576718)

自小寨东路南侧馆区入口朝内看中央序厅。 地图展示方向由真北顺时针 180°，地形安置约按 195 米横向尺度采样。母版以 Z 向上、−Y 为正面，导出 GLB 以 Y 向上、+Z 为正面，底面高度为零。

## 模型与验收

- [ImageGen 正面、侧面和侧前方参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)按结构分组并打包纹理。[重建脚本](../expansion-heritage/)
- [全国版 GLB](../../../app/public/models/shaanxi-history-museum.glb)实测 7,260 三角面、856,720 字节，含 14 张内嵌纹理。[文件统计](stats.json)
- 以下三张由最终 GLB 重新导入后渲染。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录调用 Blender 5.2 重建、导出和回读渲染。使用团队手工调整后的母版重新导出可在末尾加 `--from-master`，只回读最终 GLB 时加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-heritage/build.py -- shaanxi-history-museum
```
