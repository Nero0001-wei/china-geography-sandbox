# 天安门广场

广场北端的天安门城楼有红墙、五道券门和黄瓦重檐，正对南北中轴。

以广场北端天安门城楼坐标为模型锚点。取广场北端视角，表现现状城台、城楼、华表和南侧铺地。 178.5° 为正面方位记录，跨度约 155 米。

- [实景资料](https://www.beijing.gov.cn/zhengce/zhengcefagui/202301/W020230130329977849629.pdf)
- [坐标来源](https://commons.wikimedia.org/wiki/Tiananmen)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/tiananmen-square.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- tiananmen-square
```
