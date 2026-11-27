# 古迹、园林与街区微缩模型

本目录含 23 处景点的 Blender 重建源码。每处景点目录中的 `site.json` 保存作品题材、历史版本、地图位置、朝向及尺度，`reference/` 保存设计参考和完整提示词。

各个场景使用同一坐标约定。门洞、桥孔和围院用真实几何开口，曲面屋脊与人像由轮廓网格生成。瓦纹、石材和水面由 UV 表面表现。常规材质复用 [workshop-c 材质图](../workshop-c/textures/)，特定蓝瓦及砂岩由构建脚本生成纹理。

在项目根目录调用 Blender 5.2。示例重建天坛母版、导出网页 GLB 并重新导入渲染三张实模图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 2 --python-exit-code 1 --python data/landmarks/expansion-east/build.py -- temple-of-heaven
```

修改母版后用 `--from-master` 导出；只回读 GLB 并重拍时使用 `--render-only`。文件统计从 GLB 内的索引缓冲定义读取。
