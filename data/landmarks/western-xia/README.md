# 西夏陵 · 三号陵园

取三号陵现存夯土陵塔和陵园残墙的一段。 贺兰山东麓的多层夯土陵塔与低矮陵园残墙由沙土色层次勾勒。 [实景和历史资料](https://whc.unesco.org/zh/list/1736)

## 经纬度与方向

模型锚点取 WGS84 经度 `105.986625`、纬度 `38.43523`。按 OpenStreetMap 所标地物中心取 WGS84 锚点。 [定位来源](https://www.openstreetmap.org/way/316192094)

从陵园南侧礼仪路径顺看陵塔。 模型底面为零。Blender Z 向上、正面朝 −Y，GLB Y 向上、正面朝 +Z。地图展示方向由真北顺时针 183°，地形底座采样使用约 152 米横向尺度。

## 模型与验收

- [ImageGen 正面、侧面和侧前方设计参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)保留结构分组，并打包纹理。模型构件、几何和材质可由[制作脚本](../expansion-east/)重建。
- [全国版 GLB](../../../app/public/models/western-xia.glb)实测 **1,960 三角面**、220,536 字节，含 3 张内嵌纹理。[文件统计](stats.json)
- 从最终 GLB 重新导入拍摄。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录运行 Blender 5.2 重建母版、导出并渲染三张实模图。保存手工调整后的母版后加 `--from-master`，仅重拍实模图可加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-east/build.py -- western-xia
```
