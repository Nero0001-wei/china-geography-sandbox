# 大唐芙蓉园紫云楼

紫云楼立在朱褐色高台上，灰瓦重檐与朱柱构成临湖楼阁的剪影。现状仿唐建筑，以2023年改扩建后公开照片为参考。[景区或机构资料](https://nwin.cscec.com/xwzx/qydt/202305/3671538.html) · [补充资料](https://www.nith.edu.cn/__local/D/26/50/AEA45F963E93C94EFC72D145DDC_430CB94B_148A9EC.pdf)

## 制作取舍

按设计院的鸟瞰和实景照片把设计参考的偏金色屋面改为灰瓦。将四层的最低一层纳入褐色高台，突出三层檐线、朱色柱廊、角亭与临湖石台。

[ImageGen 正面、右侧和侧前方参考](reference/三视角.webp) · [提示词原文](reference/prompt.txt) · [原始三景九格图](../workshop-c/reference/B.png)

## 地理锚点

高德「大唐芙蓉园-紫云楼」主体 POI，GCJ-02（108.973888, 34.212819）按项目迭代逆算为 WGS84；非测绘成果。 经纬度顺序为经度、纬度，WGS84 **108.9691462°、34.2143631°**。GLB 的局部 +Z 朝地理方位 0°，以正北为 0° 顺时针计。取北侧临芙蓉湖的展示正面。园区规划图所示主轴南北向，南侧元功门—紫云楼—北侧湖面相接。[主体定位来源](https://www.amap.com/place/B001D0Z5D3) · [地图接入元数据](site.json)

地理取样覆盖约 92 米。全国沙盘使用统一显示尺度。模型局部原点对齐主体锚点，底面高度为零。出行时可分别检索“大唐芙蓉园西门停车场”与“大唐芙蓉园地铁站”。

## 模型与回读结果

| 网页资产 | 版本 | 三角面 | 字节数 | 材质 / 嵌入贴图 |
| --- | --- | ---: | ---: | ---: |
| [tang-paradise.glb](../../../app/public/models/tang-paradise.glb) | national-v1 | 7,450 | 802,480 | 10 / 10 |

实模图来自空白场景重新导入网页 GLB 后的三角度正交渲染。材质均从 GLB 内部读取。原始分组和贴图保存在[可编辑 Blender 母版](source.blend)，导出与母版的 SHA-256 记录于[实测统计](stats.json)。

[正面实模](renders/正面.png) · [右侧实模](renders/右侧.png) · [侧前方实模](renders/侧前方.png)

## 网页预览

[全国视图](../web/全国视图.png) · [手机全国视图](../web/手机全国视图.png) · [景点斜视近景](web/斜视近景.png)

## 重建

在项目根目录使用 Blender 5.2.1。修改母版后，以下命令从已保存的分组网格导出并更新网页文件、面数和实模图。

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python-exit-code 1 -P data/landmarks/workshop-c/build.py -- tang-paradise --from-master
```

完整重建时移除 `--from-master`。几何位于[场景脚本](../workshop-c/sites.py)，重复构件使用[几何函数](../workshop-c/geometry.py)，[导出脚本](../workshop-c/build.py)读取已备好的[原创材质贴图](../workshop-c/textures/)。如需重新生成贴图，可用带 Pillow 的 Python 执行 `python3 data/landmarks/workshop-c/surfaces.py`。
