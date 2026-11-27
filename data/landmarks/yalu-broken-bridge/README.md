# 鸭绿江断桥

鸭绿江断桥的钢桁架自丹东岸伸入江中，尽头可见断面和裸露的石桥墩。

取 OpenStreetMap 断桥在丹东岸的桥头节点，桥面局部 +X 对应东南。表现修整后可步行的中国一侧桥段。局部 −X 是丹东岸，+X 指向江中；保留断口的镂空桁架。 223° 为正面方位记录，跨度约 255 米。

- [实景资料](https://files.dandong.gov.cn/files/ueditor/DDSZF/jsp/upload/file/20230318/1679113984062057190.pdf)
- [坐标来源](https://www.openstreetmap.org/way/1119773891)
- [三视设计参考](reference/design-triplet.jpg)与[生成提示词](reference/imagegen-prompt.md)
- [可编辑母版](source.blend)、[全国版 GLB](../../../app/public/models/yalu-broken-bridge.glb)和[实测统计](stats.json)
- 重新导入全国版后的[正面](renders/正面.png)、[右侧](renders/右侧.png)与[侧前方](renders/侧前方.png)

在项目根目录重建模型。Blender 5.2.1 为本次使用的版本。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 -P data/landmarks/expansion-urban/build.py -- yalu-broken-bridge
```
