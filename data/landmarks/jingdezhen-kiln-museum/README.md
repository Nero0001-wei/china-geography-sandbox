# 景德镇御窑博物馆

御窑博物馆的旧窑砖拱壳长短错落，在一处下沉庭院和水面外排开。

取御窑博物馆 OSM 节点。取朱锫建筑事务所设计的 2020 年前后落成的窑拱组团，保留可透视的砖拱洞和下沉面。 181° 为正面方位记录，跨度约 118 米。

- [实景资料](https://www.archdaily.com/zh/948088/jing-de-zhen-yu-yao-bo-wu-guan-zhu-pou-jian-zhu-shi-wu-suo)
- [坐标来源](https://www.openstreetmap.org/node/13711527662)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/jingdezhen-kiln-museum.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- jingdezhen-kiln-museum
```
