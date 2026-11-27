# 婺源篁岭 · 篁岭古村·天街与晒秋

取修缮开放后的古村片段和秋季的晒秋陈设。 篁岭的徽派民居沿坡层叠，灰瓦马头墙前的木架托着晾晒辣椒、玉米的竹匾。 [官方景点资料](https://new.wyhl.cc/site/wyhl/lyzx/rmhd/detail2024-10-28-312.html) · [建筑实景](https://commons.wikimedia.org/wiki/File:Autumn_sun_drying_at_Huangling.jpg)

## 经纬度与方向

WGS84 锚点为经度 `118.1132609`、纬度 `29.3235898`。模型涵盖晒工坊、天街周边坡地，取 OpenStreetMap 坡地古村代表点。 [坐标来源](https://www.openstreetmap.org/node/4818081345)

取面向北侧低处的坡面展示方向。 地图展示方向由真北顺时针 5°，地形安置约按 105 米横向尺度采样。母版以 Z 向上、−Y 为正面，导出 GLB 以 Y 向上、+Z 为正面，底面高度为零。

## 模型与验收

- [ImageGen 正面、侧面和侧前方参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)按结构分组并打包纹理。[重建脚本](../expansion-heritage/)
- [全国版 GLB](../../../app/public/models/huangling.glb)实测 7,450 三角面、934,684 字节，含 13 张内嵌纹理。[文件统计](stats.json)
- 以下三张由最终 GLB 重新导入后渲染。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录调用 Blender 5.2 重建、导出和回读渲染。使用团队手工调整后的母版重新导出可在末尾加 `--from-master`，只回读最终 GLB 时加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-heritage/build.py -- huangling
```
