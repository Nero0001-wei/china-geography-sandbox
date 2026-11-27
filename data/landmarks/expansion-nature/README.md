# 全国沙盘自然景观微缩工坊

这批 25 座景观各自保留分组 Blender 母版、图像参考、定位资料、网页 GLB 和从 GLB 回读制作的三视实模图。统一采用底座中心原点，底面高度为零。Blender 中 Z 向上、正面朝 −Y，GLB 中 Y 向上、正面朝 +Z。

## 可编辑结构

[几何工具](shapes.py)根据带材质的面片建立可编辑网格。场景文件分别保存每个地点的地形配方与代表构件。

- [江河、湖泊与瀑布](waters.py)独立构造湖盆、河曲、落水台阶和水面，再布置岸边植被。
- [高山与石柱](summits.py)分别刻画火山口、砂岩柱群、冰川雪线和山顶建筑。
- [沙丘、溶洞与林场](terrain.py)含不同成因的岩丘和沙脊、真实穿洞以及阿里山林业铁路小火车。
- [展面纹理](../workshop-c/textures/)复用项目既有原创纹理。自然地形通过色块与网格塑形，主要纹理打包在母版并随全国版 GLB 嵌入。

## 重建与检查

在项目根目录调用 Blender 5.2.1。将示例中的 `changbai` 换成目标景点目录名即可。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-nature/build.py -- changbai
```

编辑已有母版后附加 `--from-master`，可从该母版重新导出网页文件并更新统计与回读图。附加 `--no-render` 可跳过渲染，附加 `--render-only` 可回读当前网页文件并更新三视实模图。
