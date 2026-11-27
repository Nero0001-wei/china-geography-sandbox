# 普陀山·普济禅寺 · 普济寺海印池及前殿

参考普济寺现存寺院布局与殿前海印池。 普济寺的红柱黄瓦殿宇临海印池，池上有可透水的石拱桥。 [实景和历史资料](https://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web2476/site/attach/0/3zyz-1-1/%E8%88%9F%E5%B1%B1%E5%B8%82%E4%BA%A4%E9%80%9A%E5%BF%97.pdf)

## 经纬度与方向

模型锚点取 WGS84 经度 `122.3824314`、纬度 `29.9877688`。按 OpenStreetMap 所标地物中心取 WGS84 锚点。 [定位来源](https://www.openstreetmap.org/node/4519392716)

展示面从海印池南岸朝向寺前建筑。 模型底面为零。Blender Z 向上、正面朝 −Y，GLB Y 向上、正面朝 +Z。地图展示方向由真北顺时针 176°，地形底座采样使用约 96 米横向尺度。

## 模型与验收

- [ImageGen 正面、侧面和侧前方设计参考](reference/design-triplet.jpg) · [完整提示词](reference/imagegen-prompt.md)
- [可编辑 Blender 母版](source.blend)保留结构分组，并打包纹理。模型构件、几何和材质可由[制作脚本](../expansion-east/)重建。
- [全国版 GLB](../../../app/public/models/putuo.glb)实测 **3,376 三角面**、664,676 字节，含 16 张内嵌纹理。[文件统计](stats.json)
- 从最终 GLB 重新导入拍摄。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录运行 Blender 5.2 重建母版、导出并渲染三张实模图。保存手工调整后的母版后加 `--from-master`，仅重拍实模图可加 `--render-only`。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/expansion-east/build.py -- putuo
```
