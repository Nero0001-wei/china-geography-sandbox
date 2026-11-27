# 恭王府博物馆 · 银安殿及东西配殿

按2008年依据恭亲王时期格局原址重建的银安殿现貌建模。 恭王府正殿绿琉璃瓦下开五间，院落两侧分布灰瓦配殿，殿前月台两端是对称石阶。 [官方景点资料](https://www.pgm.org.cn/pgm/wfjd/201402/4bd8662d01834dc4888ffd229d2e0dff.shtml) · [建筑实景](https://www.pgm.org.cn/pgm/wfjd/201402/4bd8662d01834dc4888ffd229d2e0dff/images/%E9%93%B6%E5%AE%89%E6%AE%BF.jpg)

## 经纬度与方向

WGS84 锚点为经度 `116.3800886`、纬度 `39.9353469`。取银安殿建筑轮廓中心点。 [坐标来源](https://www.openstreetmap.org/way/561187414)

朝向银安殿南侧中院。 地图展示方向由真北顺时针 180°，地形安置约按 67 米横向尺度采样。母版以 Z 向上、−Y 为正面，导出 GLB 以 Y 向上、+Z 为正面，底面高度为零。

## 模型与验收

- [ImageGen 正面、侧面和侧前方参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)按结构分组并打包纹理。[重建脚本](../expansion-heritage/)
- [全国版 GLB](../../../app/public/models/prince-kung.glb)实测 6,212 三角面、816,824 字节，含 15 张内嵌纹理。[文件统计](stats.json)
- 以下三张由最终 GLB 重新导入后渲染。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录调用 Blender 5.2 重建、导出和回读渲染。使用团队手工调整后的母版重新导出可在末尾加 `--from-master`，只回读最终 GLB 时加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-heritage/build.py -- prince-kung
```
