# 黄山 · 玉屏迎客松

本件取玉屏景区青狮石旁的迎客松单株及根下岩体。全国视角保留向一侧伸展的长迎客枝、分层伞状松冠、盘根入岩三处特征。黄山市政府公布的树高为 10.08 米，手臂枝长 9.42 米，模型据此把长枝做成接近树高的跨度。裸根、岩石风化和枝叶疏密作了微缩概括。[黄山市政府·迎客松](https://www.huangshan.gov.cn/zwgk/public/6615714/10445226.html) · [国家林草局·实景资料](https://www.forestry.gov.cn/c/www/dfdt/596061.jhtml) · [中国科大玉屏实景照片（图 2）](https://metalisotopes.ustc.edu.cn/news/NdCuMgMgONd.html)

| 资源 | 内容 |
| --- | --- |
| 设计参考 | [ImageGen 三视角原图](reference/三视角.png)，左为正面，中为侧面，右为侧前方。[完整提示词](reference/prompt.txt) |
| 可编辑母版 | [source.blend](source.blend)，按岩座、木质骨架、松冠三个集合分组。各根、枝条、松冠团和针束可以分别调整，材质贴图已打包 |
| 全国版 | [huangshan.glb](../../../app/public/models/huangshan.glb)，版本 national-v1。岩座、裸根、树冠和弧形镂空针束均为可旋转观察的几何 |
| GLB 回读渲染 | [正面](renders/正面.png) · [右侧](renders/右侧.png) · [侧前方](renders/侧前方.png) |
| 生成与统计 | [建模及回读渲染脚本](build.py) · [原创材质纹理脚本](textures.py) · [实测尺寸、面数和校验值](stats.json) |

## 定位与显示

树干入岩处的水平投影是局部原点，最低岩座底面在零高度。地理锚点取单株树的 WGS84 坐标 **东经 118.1703509°、北纬 30.1245907°**。Blender 正面朝 −Y，GLB 正面朝 +Z。下部主枝主要沿 GLB +X 伸展，枝末略偏 +Z。地图展示时，模型正面（局部 +Z）沿锚点经线朝地理正南。游览从玉屏景区观景平台一侧看树，驾车或公共交通定位到汤口换乘设施。地形高程与高德坐标的误差核对见[定位记录](../两个试制景点定位.md)。[OSM 单株树节点](https://www.openstreetmap.org/node/793824902/history/11)

## 导出与验收

母版 **12,612 个三角面**。从已保存的母版内存副本压缩冠内轮廓、每团松针保留八个弧形伸展方向和三个稍上扬的顶簇，再减少细枝、苔斑的面数。网站用 GLB **7,675 个三角面，1,137,740 字节**，5 个材质、4 张内嵌贴图。针叶使用 alpha mask 保留细缝，树皮和花岗岩带 UV 纹理。导出后清空场景并重新导入 GLB，检验资源、预算与轴向，再逐一渲染正、侧、侧前视图。三个视角均可辨认外伸低枝，侧视能看到朝前后展开的实际冠幅。

## 重建

在本目录执行下列命令。已随母版保存的纹理可直接使用，重新生成纹理时需要 Python 3 和 Pillow。模型与图片使用 Blender 5.2.1 构建。第一条命令仅在要重绘纹理时执行。

```sh
python3 textures.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --factory-startup --python-exit-code 1 --python build.py
```

单独从已有 GLB 重渲染三个视角可执行：

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 4 --factory-startup --python-exit-code 1 --python build.py -- --render-only
```

## 网页实测

在 1440 × 900 桌面窗口和 390 × 844 手机视口验证 GLB 返回 HTTP 200，首批 30 个地标在全国视图均以约 25.3 个 CSS 像素为最长边。已在网页中核对模型点选、标签、键盘选择以及切换自驾和公共交通时带入的目的地。[全国视图](../web/全国视图.png) · [手机视图](../web/手机全国视图.png) · [本景点的斜视近景](web/斜视近景.png)
