# 北京故宫 · 太和殿

本模型表现紫禁城外朝中轴上的太和殿，现存形制为清康熙三十四年（1695 年）重建。取景集中在正殿、三层汉白玉台基和通向南侧的石阶。殿身按面阔十一间、进深五间布置，重檐庑殿顶保留正脊两端的大吻和四坡交线。真实殿宇连台基通高 35.05 米。[故宫博物院·太和殿](https://www.dpm.org.cn/explore/building/236465.html) · [实景外观](https://img.dpm.org.cn/Uploads/Picture/2020/07/03/s5efefbd5093a9.jpg) · [檐角脊兽实照](https://img.dpm.org.cn/Uploads/Picture/dc/1612%5B1024%5D.jpg)

## 参考和实模

- 用内置 ImageGen 生成了同一微缩模型的[正面、右侧和侧前方参考图](reference/ImageGen-三视图.png)，生成时使用的[完整提示词](reference/prompt.txt)一并保留。
- 模型保留参考图的宽体量、黄瓦与白台基。中轴南向的御道和两侧阶梯按实物方向布置。右侧面依照故宫原建筑仅呈现五间进深，修正了生成参考图侧面出现的居中大阶梯。前、侧屋檐都用真实几何起翘。南向长阶沿三层台基分段，周边院落于这件全国版中裁去。
- 黄琉璃瓦陇、菱花门、梁枋彩画、汉白玉表面、铺石、御道浅浮雕和匾额是独立的小幅 UV 纹理。全国版减少檐下斗栱与栏杆柱头，保留柱廊空间、屋檐挑出和三列正面梯道。
- 最终 GLB 从空场景重新导入，使用相同的正交摄影棚和光照拍摄。[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 模型定位

展示点取 OSM 太和殿建筑轮廓的面积质心，WGS84 经度 **116.39081395°**、纬度 **39.91589562°**。几何原点在正脊中点的正下方，南侧台阶向前伸出。GLB 的地面为 Y=0，正面朝局部 +Z。前檐的地理方位约 178.5°，进入当前沙盘后绕世界 Y 轴旋转约 0.140415 弧度。[太和殿建筑轮廓](https://www.openstreetmap.org/way/638449347) · [项目定位核验与出行入口](../两个试制景点定位.md)

## 文件与重建

| 版本 | 全国版文件 | 三角面 | 文件大小 | 材质及嵌入图像 |
| --- | --- | ---: | ---: | --- |
| national-v1 | [gugong.glb](../../../app/public/models/gugong.glb) | 7,098 | 547,604 字节 | 14 种材质、7 张贴图 |

[Blender 母版](source.blend)按三层台基、殿身、檐下彩画和上、下两层屋顶分成七个可编辑网格。所有贴图已打包。修改母版后在项目根目录执行下列命令即可更新网页 GLB、[统计文件](stats.json)与三个实模视图。在内存中的工作副本上删除标记为「近景细部」的面并合并同材质网格；磁盘上的母版保留原有细节。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background data/landmarks/gugong/source.blend --python-exit-code 1 --python data/landmarks/gugong/build.py -- --from-master
```

若要从程序化几何完整重建母版和全国版，使用 Blender 5.2.1 的下列命令。重建会覆盖本地母版，保留手工修改时使用上面的导出命令。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python-exit-code 1 --python data/landmarks/gugong/build.py
```

原始纹理 PNG 位于 `textures/`。需要重新绘制时运行 `python3 data/landmarks/gugong/textures.py`，使用 Pillow 和系统中文字体。Blender 重建直接加载现有 PNG。

## 网页实测

在 1440 × 900 桌面窗口和 390 × 844 手机视口验证 GLB 返回 HTTP 200，首批 30 个地标在全国视图均以约 25.3 个 CSS 像素为最长边。已在网页中核对模型点选、标签、键盘选择以及切换自驾和公共交通时带入的目的地。[全国视图](../web/全国视图.png) · [手机视图](../web/手机全国视图.png) · [本景点的斜视近景](web/斜视近景.png)
