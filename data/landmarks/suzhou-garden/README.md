# 苏州拙政园 · 远香堂与荷花池

取中部远香堂及邻水游廊和部分荷花池。 素壁灰瓦的远香堂与游廊临荷池，曲桥和太湖石沿水岸分布。 [实景和历史资料](https://whc.unesco.org/en/list/813/)

## 经纬度与方向

模型锚点取 WGS84 经度 `120.6245434`、纬度 `31.3262713`。按 OpenStreetMap 所标地物中心取 WGS84 锚点。 [定位来源](https://www.openstreetmap.org/way/485084803)

从北侧池畔南望远香堂。 模型底面为零。Blender Z 向上、正面朝 −Y，GLB Y 向上、正面朝 +Z。地图展示方向由真北顺时针 4°，地形底座采样使用约 71 米横向尺度。

## 模型与验收

- [ImageGen 正面、侧面和侧前方设计参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)保留结构分组，并打包纹理。模型构件、几何和材质可由[制作脚本](../expansion-east/)重建。
- [全国版 GLB](../../../app/public/models/suzhou-garden.glb)实测 **5,422 三角面**、735,872 字节，含 13 张内嵌纹理。[文件统计](stats.json)
- 从最终 GLB 重新导入拍摄。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录运行 Blender 5.2 重建母版、导出并渲染三张实模图。保存手工调整后的母版后加 `--from-master`，仅重拍实模图可加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-east/build.py -- suzhou-garden
```
