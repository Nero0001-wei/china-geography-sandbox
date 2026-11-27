# 云冈石窟 · 第二十窟露天坐佛

取北魏昙曜五窟中现存敞露的第二十窟。 浅褐色坐佛和两侧小龛嵌在武州山风化岩壁上。 [实景和历史资料](https://whc.unesco.org/en/list/1039/)

## 经纬度与方向

模型锚点取 WGS84 经度 `113.1227613`、纬度 `40.1102231`。按 OpenStreetMap 所标地物中心取 WGS84 锚点。 [定位来源](https://www.openstreetmap.org/node/5740709321)

沿窟前南侧步道，展示主佛面相和东侧龛壁。 模型底面为零。Blender Z 向上、正面朝 −Y，GLB Y 向上、正面朝 +Z。地图展示方向由真北顺时针 165°，地形底座采样使用约 27 米横向尺度。

## 模型与验收

- [ImageGen 正面、侧面和侧前方设计参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)保留结构分组，并打包纹理。模型构件、几何和材质可由[制作脚本](../expansion-east/)重建。
- [全国版 GLB](../../../app/public/models/yungang.glb)实测 **5,162 三角面**、535,132 字节，含 5 张内嵌纹理。[文件统计](stats.json)
- 从最终 GLB 重新导入拍摄。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录运行 Blender 5.2 重建母版、导出并渲染三张实模图。保存手工调整后的母版后加 `--from-master`，仅重拍实模图可加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-east/build.py -- yungang
```
