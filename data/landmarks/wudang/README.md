# 武当山 · 天柱峰·金殿及紫金城

取明永乐十四年铸造的天柱峰金殿及山顶石墙。 鎏金铜殿位于陡峭岩峰之顶，下方是一圈石城和攀登石阶。 [实景和历史资料](https://whc.unesco.org/en/list/705/)

## 经纬度与方向

模型锚点取 WGS84 经度 `111.0043393`、纬度 `32.4007757`。按 OpenStreetMap 所标地物中心取 WGS84 锚点。 [定位来源](https://www.openstreetmap.org/way/635842275)

以临太和宫登顶路径一侧为展示面，朝向为图上近似。 模型底面为零。Blender Z 向上、正面朝 −Y，GLB Y 向上、正面朝 +Z。地图展示方向由真北顺时针 160°，地形底座采样使用约 60 米横向尺度。

## 模型与验收

- [ImageGen 正面、侧面和侧前方设计参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)保留结构分组，并打包纹理。模型构件、几何和材质可由[制作脚本](../expansion-east/)重建。
- [全国版 GLB](../../../app/public/models/wudang.glb)实测 **3,202 三角面**、561,620 字节，含 12 张内嵌纹理。[文件统计](stats.json)
- 从最终 GLB 重新导入拍摄。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录运行 Blender 5.2 重建母版、导出并渲染三张实模图。保存手工调整后的母版后加 `--from-master`，仅重拍实模图可加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-east/build.py -- wudang
```
