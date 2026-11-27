# 中国国家博物馆 · 西平台及主馆西立面

取1959年原馆西立面与2011年改扩建完成后的整体馆舍。 天安门广场东侧的国博馆舍由对称石质两翼、开敞的西入口方柱廊和东侧新馆构成。 [官方景点资料](https://www.gmp.de/cn/projects/471/national-museum-of-china) · [建筑实景](https://www.chnmuseum.cn/zl/zlhg/201812/t20181220_32269.shtml)

## 经纬度与方向

WGS84 锚点为经度 `116.3953896`、纬度 `39.9037459`。取国博馆舍围合轮廓在 OpenStreetMap 的代表中心点。 [坐标来源](https://www.openstreetmap.org/relation/8607825)

以正对天安门广场的西入口柱廊为正面。 地图展示方向由真北顺时针 270°，地形安置约按 305 米横向尺度采样。母版以 Z 向上、−Y 为正面，导出 GLB 以 Y 向上、+Z 为正面，底面高度为零。

## 模型与验收

- [ImageGen 正面、侧面和侧前方参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)按结构分组并打包纹理。[重建脚本](../expansion-heritage/)
- [全国版 GLB](../../../app/public/models/national-museum-china.glb)实测 4,484 三角面、492,068 字节，含 7 张内嵌纹理。[文件统计](stats.json)
- 以下三张由最终 GLB 重新导入后渲染。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录调用 Blender 5.2 重建、导出和回读渲染。使用团队手工调整后的母版重新导出可在末尾加 `--from-master`，只回读最终 GLB 时加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-heritage/build.py -- national-museum-china
```
