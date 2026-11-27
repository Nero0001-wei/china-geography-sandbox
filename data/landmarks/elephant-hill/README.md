# 桂林象鼻山 · 水月洞、象鼻与山顶普贤塔

取现状石灰岩山体、水月洞与山顶普贤塔；选择江北侧观景方向。

由山体和下探的石鼻围出水月洞，保留贯通岩壁与水面的空间。峰顶设置普贤塔和高低不一的植被。 [景区资料与实景参考](https://m.glljsh.com/)

## 经纬度与展示方向

主体锚点为 WGS84 经度 `110.292042`、纬度 `25.2703267`。取 OSM 水月洞天然洞口节点。两条来源的坐标相距约 6 米。此差值用于说明两处标注的一致程度。大型建筑群和瀑布可有多个合理的代表点。[位置来源](https://www.openstreetmap.org/node/9482724876) · [交叉核对](https://ditu.amap.com/place/B0FFG2AQ25)

模型底面高度为 0。Blender 主视面朝 −Y，GLB 主视面朝 +Z，投放朝向为从真北顺时针 **20°**。记录的实地横向尺度约 70 米。沙盘对地标独立等比放大，地图位置取上述锚点。驾车与公共交通的候选入口见 [site.json](site.json)。

## 制作与交付

- [ImageGen 三视角设计参考](reference/三视角.png) · [完整提示词](reference/prompt.txt) · [原始整幅参考图](../workshop-b/references/2.png)
- [可编辑 Blender 母版](source.blend)按结构分组并打包纹理。几何及 UV 由[生成脚本](../workshop-b/sculptures.py)和[基础构件](../workshop-b/geometry.py)生成，[材质原图](../workshop-b/textures/)由[纹理脚本](../workshop-b/textures.py)绘制。
- [全国版 GLB](../../../app/public/models/elephant-hill.glb)包含 7,530 个三角面、7 个材质和 7 张内嵌纹理，共 747,204 字节。[文件校验与尺寸](stats.json)
- 最终文件重新导入后，以正交相机拍摄三张实模图。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录使用 Blender 5.2 构建母版、导出并重新导入拍摄。Blender 可执行文件安装在 macOS 默认位置时，命令如下。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/workshop-b/build.py -- elephant-hill
```

原始母版经过手工编辑后，在同一命令末尾加 `--from-master` 可使用已保存的母版重新导出。用 `--render-only` 单独拍摄硬盘上的最终 GLB。Blender 的 Python 环境包含全部建模依赖，独立重绘纹理需要 Python 和 Pillow。
