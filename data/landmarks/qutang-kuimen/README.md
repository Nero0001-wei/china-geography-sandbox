# 长江三峡·瞿塘峡夔门

奉节瞿塘峡西口的赤甲山和白盐山夹峙江面，取白帝城一侧望入夔门的视角。 [景区与实景资料](https://www.cq.gov.cn/zjcq/cycq/zmjd/zqaaaaajjq/202606/t20260604_15729050.html) · [重庆市档案馆·夔门与白帝城](https://jda.cq.gov.cn/web/article/1464346337456713728/web/content_1464346337456713728.html)

从白帝城一带的上游方向看，两壁由近岸宽水面向陡狭峡口合拢。暖灰赤甲山和较浅的白盐山用不同岩色表现，江上小船用来提示峡壁尺度。

[三视设计参考](reference/design-triplet.jpg) · [完整 ImageGen 提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点为奉节瞿塘关北岸观景点，WGS84 **109.5768917°E、31.0414631°N**。取 OpenStreetMap 瞿塘关东侧标注的岸边观景点，模型代表附近水道阔窄变化及两岸山壁。 [坐标来源](https://www.openstreetmap.org/node/9531506505)
- 主体位置另记为 **109.5792208°E、31.0388181°N**。 [主体地物来源](https://www.openstreetmap.org/node/347498410)
- 模型正面约朝西北 302°，对应夔门向白帝城所在上游的方向。 地形取样跨度约 1400 米，地图筛选归入自然风光与全国代表。 [元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [qutang-kuimen.glb](../../../app/public/models/qutang-kuimen.glb) | national-v1 | 7,690 | 752,528 字节 | 17 / 3 |

母版分组可编辑，回读实模图均由最终网页 GLB 在空白场景重新导入后渲染。[母版](source.blend) · [实测统计](stats.json)

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 重建

在项目根目录运行下列命令。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-scenic/build.py -- qutang-kuimen
```

[场景源码](../expansion-scenic/natural.py) · [共用建模与导出说明](../expansion-scenic/README.md)
