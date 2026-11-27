# 澳门大三巴牌坊

保留石质立面的五层山花、贯通门洞、窗洞与面向前地的石阶。17世纪教堂大火后留存的花岗岩立面。[景区或机构资料](https://www.wh.mo/gb/site/detail/18) · [补充资料](https://www.wh.mo/upload/mhImage/arc/18/20231122/164601-1.jpg)

## 制作取舍

对照澳门文化局南立面测绘图，把设计参照中圆弧门口改成平门楣，在同一片薄墙上做出底层三个门洞、二层三个拱窗和逐渐收窄的上层。侧面能同时看见阶梯、立面厚度、前伸的柱式与山花。

[ImageGen 正面、右侧和侧前方参考](reference/三视角.webp) · [提示词原文](reference/prompt.txt) · [原始三景九格图](../workshop-c/reference/C.png)

## 地理锚点

OpenStreetMap 大三巴现存立面地物轮廓的面积质心。 经纬度顺序为经度、纬度，WGS84 **113.5408602°、22.1974569°**。GLB 的局部 +Z 朝地理方位 179.1°，以正北为 0° 顺时针计。按澳门文化局南立面实测图，以及 OSM 牌坊两条约 89.1° 的长边，取向南法线。[主体定位来源](https://www.openstreetmap.org/way/192183185) · [地图接入元数据](site.json)

地理取样覆盖约 23 米。全国沙盘使用统一显示尺度。模型局部原点对齐主体锚点，底面高度为零。出行时可分别检索“栢港停车场”与“白鸽巢总站”。

## 模型与回读结果

| 网页资产 | 版本 | 三角面 | 字节数 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [st-pauls.glb](../../../app/public/models/st-pauls.glb) | national-v1 | 4,490 | 446,084 | 5 / 5 |

实模图来自空白场景重新导入网页 GLB 后的三角度正交渲染。材质均从 GLB 内部读取。原始分组和贴图保存在[可编辑 Blender 母版](source.blend)，导出与母版的 SHA-256 记录于[实测统计](stats.json)。

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 网页预览

[全国视图](../web/全国视图.png) · [手机全国视图](../web/手机全国视图.png) · [景点斜视近景](web/斜视近景.png)

## 重建

在项目根目录使用 Blender 5.2.1。修改母版后，以下命令从已保存的分组网格导出并更新网页文件、面数和实模图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/workshop-c/build.py -- st-pauls --from-master
```

完整重建时移除 `--from-master`。几何位于[场景脚本](../workshop-c/sites.py)，重复构件使用[几何函数](../workshop-c/geometry.py)，[导出脚本](../workshop-c/build.py)读取已备好的[原创材质贴图](../workshop-c/textures/)。如需重新生成贴图，可用带 Pillow 的 Python 执行 `python3 data/landmarks/workshop-c/surfaces.py`。
