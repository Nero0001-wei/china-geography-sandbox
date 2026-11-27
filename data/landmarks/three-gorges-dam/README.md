# 三峡大坝

长江三峡主坝中段以连续闸墩和泄洪孔组织坝面，两侧接出混凝土坝体。

以坝体条目坐标作为主坝构图中心。表现已建成主坝的局部，下游为正面；水面的高度差为缩尺示意。 124° 为正面方位记录，跨度约 2309 米。

- [实景资料](https://www.cypc.com.cn/sxjt/sxgc4/gcgk7/index.html)
- [坐标来源](https://www.wikidata.org/wiki/Q12514)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/three-gorges-dam.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- three-gorges-dam
```
