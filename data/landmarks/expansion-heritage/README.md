# 博物馆、考古遗址与街区微缩模型

本目录含中国国家博物馆、恭王府博物馆、陕西历史博物馆本馆、西安城墙永宁门、安阳殷墟和婺源篁岭的重建脚本。六处景点的目录分别保存位置依据、原始照片链接、设计参考和提示词、可编辑母版及最终 GLB 的实模图。

场景几何使用 Blender 本地轴向，正面朝 −Y，底面高为零。石墙和屋瓦用贴图表现纹理，永宁门三座门楼的券洞和吊桥下方水道保留真实空隙。门楼、院落、屋顶、柱廊和地形在母版中分组保存。常规纹理复用 [workshop-c 材质图](../workshop-c/textures/)，石材和茅草屋顶用构建脚本生成的可重现纹理。

在项目根目录运行 Blender 5.2。示例重建国博母版、导出网页 GLB，再重新导入渲染三视图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 2 --python-exit-code 1 --python data/landmarks/expansion-heritage/build.py -- national-museum-china
```

换用对应景点目录名即可重建其他景点。修改保存母版后可加 `--from-master` 重新导出。单独用最终 GLB 重拍可加 `--render-only`。
