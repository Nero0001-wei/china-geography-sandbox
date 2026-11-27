# 岳阳楼 · 岳阳楼主楼

取1880年大修重建形制，保留三层盔顶和临湖城台。 洞庭湖畔城台上的三层木楼以金瓦盔顶、如意斗拱与朱色回廊为特征。 [实景和历史资料](https://www.hunan.gov.cn/hnszf/c101480/202108/t20210830_20411802.html)

## 经纬度与方向

模型锚点取 WGS84 经度 `113.0883327`、纬度 `29.3846862`。按 OpenStreetMap 所标地物中心取 WGS84 锚点。 [定位来源](https://www.openstreetmap.org/way/230337579)

依据湖南省政府建筑资料，取坐西朝东的主立面。 模型底面为零。Blender Z 向上、正面朝 −Y，GLB Y 向上、正面朝 +Z。地图展示方向由真北顺时针 90°，地形底座采样使用约 36 米横向尺度。

## 模型与验收

- [ImageGen 正面、侧面和侧前方设计参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)保留结构分组，并打包纹理。模型构件、几何和材质可由[制作脚本](../expansion-east/)重建。
- [全国版 GLB](../../../app/public/models/yueyang-tower.glb)实测 **4,976 三角面**、622,248 字节，含 11 张内嵌纹理。[文件统计](stats.json)
- 从最终 GLB 重新导入拍摄。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录运行 Blender 5.2 重建母版、导出并渲染三张实模图。保存手工调整后的母版后加 `--from-master`，仅重拍实模图可加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-east/build.py -- yueyang-tower
```
