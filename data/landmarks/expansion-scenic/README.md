# 壶口、夔门、洱海、天眼和鲸鲨馆微缩模型

[自然景观源码](natural.py)保留壶口的河槽层理与水帘、夔门两侧的高差、洱海小普陀和海印村岸段。[工程与乐园源码](structures.py)分别搭建天眼的下凹反射盘、六塔与中央馈源舱，以及鲸鲨馆的立体雕塑、波浪门廊和嵌入式斑点贴图。

可编辑母版按地形、主体、建筑、植被等结构分组。模型底座中心对应展示锚，底面高度为零。Blender 正面为局部 −Y，导出的 GLB 正面为 +Z。[导出与回读入口](build.py)复用[主工坊的低模和渲染工具](../expansion-nature/README.md)。

## 重建

在项目根目录使用 Blender 5.2.1，将示例中的 `hukou-falls` 替换成目标景点 ID。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/expansion-scenic/build.py -- hukou-falls
```

`--from-master` 从已编辑的母版重新导出。`--no-render` 跳过回读渲染。`--render-only` 从现有网页 GLB 重新制作三视图。
