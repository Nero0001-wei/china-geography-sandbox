# 维多利亚港·尖沙咀海滨

尖沙咀旧火车站钟楼的红砖塔身与天星码头并立，渡轮从近岸擦过。

用尖沙咀钟楼建筑轮廓中心为锚点。取九龙一侧的钟楼与码头，正面朝向维港。钟楼为 20 世纪初遗存，码头及渡轮以现状概括。 185° 为正面方位记录，跨度约 190 米。

- [实景资料](https://www.discoverhongkong.com/tc/attractions/top-things-to-see-and-do-around-tsim-sha-tsui-promenade.html)
- [坐标来源](https://www.openstreetmap.org/way/37664321)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/victoria-harbour.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- victoria-harbour
```
