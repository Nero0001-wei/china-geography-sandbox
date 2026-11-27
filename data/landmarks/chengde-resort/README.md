# 承德避暑山庄 · 湖区水心榭

康熙时修建的水心榭横跨下湖与银湖之间的水面。 灰瓦红柱的三亭和水下桥墩连成一道榭桥，水面伸向两岸。 [实景和历史资料](https://www.bishushanzhuang.com.cn/index.php/scenic/pic_list/id/193.html)

## 经纬度与方向

模型锚点取 WGS84 经度 `117.93868`、纬度 `40.98347`。用 Esri World Imagery 影像中的中榭屋顶中心，按景区官方照片的三亭排列交叉定位。 [定位来源](https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/18/98300/216952)

按影像中三座亭榭的东北至西南连线，取面向西北侧湖面的展示方向。 模型底面为零。Blender Z 向上、正面朝 −Y，GLB Y 向上、正面朝 +Z。地图展示方向由真北顺时针 302°，地形底座采样使用约 96 米横向尺度。

## 模型与验收

- [ImageGen 正面、侧面和侧前方设计参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)保留结构分组，并打包纹理。模型构件、几何和材质可由[制作脚本](../expansion-east/)重建。
- [全国版 GLB](../../../app/public/models/chengde-resort.glb)实测 **4,744 三角面**、621,252 字节，含 11 张内嵌纹理。[文件统计](stats.json)
- 从最终 GLB 重新导入拍摄。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录运行 Blender 5.2 重建母版、导出并渲染三张实模图。保存手工调整后的母版后加 `--from-master`，仅重拍实模图可加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-east/build.py -- chengde-resort
```
