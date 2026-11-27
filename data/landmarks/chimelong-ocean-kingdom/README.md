# 珠海长隆海洋王国

横琴海洋王国鲸鲨馆的青蓝色波浪立面和昂首盘绕的斑点鲸鲨雕塑。 [景区与实景资料](https://www.chimelong.com/zh/oceankingdom/exhibition/2324.html) · [鲸鲨馆入口实景](https://k.sina.cn/article_6513035436_1843508ac00100i6x5.html)

按实景修正设计图中的雕塑姿态，鲸鲨昂首弯曲向上，胸鳍朝两侧伸展。青蓝浪形门廊保留真实入口开洞，斑点通过 UV 贴图嵌入 GLB。

[三视设计参考](reference/design-triplet.jpg) · [完整 ImageGen 提示词](reference/imagegen-prompt.md)

## 地理与模型接入

- 展示锚点为横琴长隆海洋王国鲸鲨馆，WGS84 **113.5277113°E、22.0995395°N**。取 OpenStreetMap 鲸鲨馆建筑轮廓的代表点，落在海洋王国园内。 [坐标来源](https://www.openstreetmap.org/way/320028482)
- 正面朝园内临湖入口广场一侧。 地形取样跨度约 145 米，地图筛选归入主题乐园与动物园与全国代表。 [元数据](site.json)

## 全国版

| 资源 | 版本 | 三角面 | 文件大小 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [chimelong-ocean-kingdom.glb](../../../app/public/models/chimelong-ocean-kingdom.glb) | national-v1 | 7,690 | 823,760 字节 | 21 / 3 |

母版分组可编辑，回读实模图均由最终网页 GLB 在空白场景重新导入后渲染。[母版](source.blend) · [实测统计](stats.json)

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 重建

在项目根目录运行下列命令。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-scenic/build.py -- chimelong-ocean-kingdom
```

[场景源码](../expansion-scenic/structures.py) · [共用建模与导出说明](../expansion-scenic/README.md)
