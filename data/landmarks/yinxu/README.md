# 安阳殷墟 · 宫殿宗庙区仿殷大殿与妇好墓展示

采用小屯宫殿宗庙区保护展示设施的现貌，妇好墓享堂与夯土台基取代表性构件并缩并到同一底座。 殷墟宫殿宗庙区的现代仿殷大殿采用宽低双层茅屋顶，旁设夯土基址与妇好墓享堂示意。 [官方景点资料](https://cpc.people.com.cn/GB/64176/64180/2527073.html) · [建筑实景](https://commons.wikimedia.org/wiki/File:26233-Anyang_(49068282726).jpg)

## 经纬度与方向

WGS84 锚点为经度 `114.31898528`、纬度 `36.12173037`。依据保护展示建筑实景与 OpenStreetMap 仿殷大殿长条建筑轮廓交叉核对，取屋顶轮廓中心。 [坐标来源](https://www.openstreetmap.org/way/810623293)

取仿殷大殿南侧庭院朝向，与 OSM 屋顶长边的南向法线近似。 地图展示方向由真北顺时针 182°，地形安置约按 65 米横向尺度采样。母版以 Z 向上、−Y 为正面，导出 GLB 以 Y 向上、+Z 为正面，底面高度为零。

## 模型与验收

- [ImageGen 正面、侧面和侧前方参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)按结构分组并打包纹理。[重建脚本](../expansion-heritage/)
- [全国版 GLB](../../../app/public/models/yinxu.glb)实测 2,456 三角面、455,052 字节，含 11 张内嵌纹理。[文件统计](stats.json)
- 以下三张由最终 GLB 重新导入后渲染。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录调用 Blender 5.2 重建、导出和回读渲染。使用团队手工调整后的母版重新导出可在末尾加 `--from-master`，只回读最终 GLB 时加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-heritage/build.py -- yinxu
```
