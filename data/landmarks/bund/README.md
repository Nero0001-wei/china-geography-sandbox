# 上海外滩微缩模型

以中间海关大楼钟楼为最高体块，四个方向均有钟面。南侧原汇丰银行的石柱廊和铜穹顶与钟楼错落，江面与立面平行。

## 实景和定位

以上海外滩 13 号 1927 年海关大楼为主体，南侧配原汇丰银行圆顶；两楼沿黄浦江北南排列，正立面对江。 [实景与景区资料](https://whlyj.sh.gov.cn/zxta/20230721/42925f1923764d98bfa7198785e56512.html) · [OpenStreetMap 主体地物](https://www.openstreetmap.org/way/178407318)

模型原点对应 WGS84 经度 **121.48543543°**、纬度 **31.23861504°**。Blender 底面为 Z=0，正面朝 −Y；导出后 GLB 底面为 Y=0，+Z 对应地理方位约 **105°**（从正北顺时针）。用于贴地核查的主体周边范围约 150 米。[坐标与出行查询词](site.json)

相邻沿江街面做比例压缩。地图点放在海关建筑中心，底座随街面向南延展。

## 参考与实模

- [ImageGen 三视图](reference/三视图.png) · [完整生成提示词](reference/prompt.txt)
- 从最终 GLB 导回 Blender 拍摄的实模图：[正面](renders/正面.png)、[右侧](renders/右侧.png)、[侧前方](renders/侧前方.png)。
- [带材质的分组母版](source.blend) · [全国版 GLB](web/bund.glb) · [网页中的同一资源](../../../app/public/models/bund.glb)

**三视角对照记录**　正面确认圆顶位于主钟楼左侧，右侧可辨钟面和窗列，斜面保留滨江建筑朝向与高低次序。相邻街廓宽度作了压缩。

## 重建

在仓库根目录运行，`blender` 为 Blender 5.2 的可执行文件。已保存的母版和 GLB 均嵌入贴图。修改脚本时可直接使用随项目保存的 [材质图](../workshop-a/textures/)；如需重制贴图，[绘制脚本](../workshop-a/textures.py) 使用 Python、Pillow 和系统中文字体。

```sh
# 从结构脚本重建母版、导出网页文件、回读成品拍摄三视图
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- bund

# 从已手动编辑并保存的母版交付同名模型
blender -b --factory-startup --python-exit-code 1 -P data/landmarks/workshop-a/build.py -- bund --from-master
```

[场景结构脚本](../workshop-a/models.py) · [几何与材质构件](../workshop-a/geometry.py) · [导出与实模拍摄](../workshop-a/build.py)

`national-v1` 最终文件含 **3,560 个三角面**、9 个材质、6 张嵌入贴图，大小 **310,860 字节**。校验值和局部边界见[导出统计](stats.json)。
