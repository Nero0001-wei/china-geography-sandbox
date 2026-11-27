# 青岛栈桥

栈桥从青岛湾的岸边笔直延向海中，桥端是八角重檐回澜阁。

以 OpenStreetMap 栈桥轮廓北侧的桥头作为展示锚点。回澜阁位于同一路径南端（120.3153814, 36.058288）。保留入海直堤、堤侧栏杆和回澜阁黄瓦八角重檐。模型正面朝青岛湾，岸端沿局部 +Y。 165° 为正面方位记录，跨度约 440 米。

- [实景资料](https://www.qingdao.gov.cn/yfqd/qdwl/cjfw/wyqhb/202009/t20200902_518755.shtml)
- [坐标来源](https://www.openstreetmap.org/way/1474305748)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/qingdao-zhanqiao.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- qingdao-zhanqiao
```
