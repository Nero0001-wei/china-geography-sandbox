# 开平碉楼

自力村的铭石楼立在稻田间，楼身窄高，顶层设拱廊和角塔。

自力村铭石楼坐标，参照碉楼与村落名录中的单体位置。取 1925 年落成的铭石楼与其外侧稻田，正面按带露台的主要立面。 188° 为正面方位记录，跨度约 34 米。

- [实景资料](https://www.jiangmen.gov.cn/bmpd/jmswhgdlytyj/zwgk/gzdt/content/post_3258271.html)
- [坐标来源](https://zh.wikipedia.org/wiki/%E5%BC%80%E5%B9%B3%E7%A2%89%E6%A5%BC)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/kaiping-diaolou.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- kaiping-diaolou
```
