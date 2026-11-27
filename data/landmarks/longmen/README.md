# 龙门石窟 · 奉先寺卢舍那大佛

唐代大像龛现存状态。坐佛向伊河，侧壁保留露天石龛。

以龛后弧形岩壁构图。缩小衣褶的密度，保留主尊高髻、面目、盘膝双腿和两侧侍像体量，石台向伊河方向伸出。 [景区资料与实景参考](https://ytsc.rootinhenan.gov.cn/sitesources/ytsc/page_pc/hnly/fjms/articlec716b8d99f6b4aa3ad4309161ed024db.html)

## 经纬度与展示方向

主体锚点为 WGS84 经度 `112.469977`、纬度 `34.5526931`。高德卢舍那大佛主体 POI 由 GCJ-02 迭代反算至 WGS84；另与 OSM 奉先寺点交叉核对。两条来源的坐标相距约 20 米。此差值用于说明两处标注的一致程度。大型建筑群和瀑布可有多个合理的代表点。[位置来源](https://ditu.amap.com/place/B0FFI960ON) · [交叉核对](https://www.openstreetmap.org/node/4223817597)

模型底面高度为 0。Blender 主视面朝 −Y，GLB 主视面朝 +Z，投放朝向为从真北顺时针 **90°**。记录的实地横向尺度约 38 米。沙盘对地标独立等比放大，地图位置取上述锚点。驾车与公共交通的候选入口见 [site.json](site.json)。

## 制作与交付

- [ImageGen 三视角设计参考](reference/三视角.png) · [完整提示词](reference/prompt.txt) · [原始整幅参考图](../workshop-b/references/1.png)
- [可编辑 Blender 母版](source.blend)按结构分组并打包纹理。几何及 UV 由[生成脚本](../workshop-b/sculptures.py)和[基础构件](../workshop-b/geometry.py)生成，[材质原图](../workshop-b/textures/)由[纹理脚本](../workshop-b/textures.py)绘制。
- [全国版 GLB](../../../app/public/models/longmen.glb)包含 7,529 个三角面、4 个材质和 4 张内嵌纹理，共 361,848 字节。[文件校验与尺寸](stats.json)
- 最终文件重新导入后，以正交相机拍摄三张实模图。[正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png)

在项目根目录使用 Blender 5.2 构建母版、导出并重新导入拍摄。Blender 可执行文件安装在 macOS 默认位置时，命令如下。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python data/landmarks/workshop-b/build.py -- longmen
```

原始母版经过手工编辑后，在同一命令末尾加 `--from-master` 可使用已保存的母版重新导出。用 `--render-only` 单独拍摄硬盘上的最终 GLB。Blender 的 Python 环境包含全部建模依赖，独立重绘纹理需要 Python 和 Pillow。
