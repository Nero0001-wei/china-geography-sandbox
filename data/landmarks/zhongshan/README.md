# 中山陵全国沙盘模型

模型表现 1929 年建成的中山陵主体，取钟山南麓通往祭堂的台阶中轴、三层石台与蓝瓦祭堂。模型沿用南京城市沙盘的微缩构图，三段台阶和建筑比例经过艺术化概括。真实建筑以南京市中山陵园管理局的[中山陵景区资料](https://zschina.nanjing.gov.cn/fjms/jqjd/zsljq/)及[中轴线介绍](https://zschina.nanjing.gov.cn/lyzx/202504/t20250425_5135983.html)为参考。

## 资产与重建

- `source.blend` 是南京城市沙盘 `中山陵模型/web/中山陵_网页版.blend` 的独立可编辑副本。`reference/` 保留源项目的无树木正面、侧前方设计图及原始说明。南京目录中未找到与这两张图对应的独立提示词文件。
- `build.py` 在本地副本上以网格折叠减面，保留蓝瓦、台阶、栏杆和三个拱门的凹进。铺石、石砌两张贴图下采样至 512 级，顶点环境遮蔽继续随导出文件保存。GLB 使用 Y 向上、正面朝 +Z、底座中心 Y 为零的坐标约定。
- 网页资产位于 `app/public/models/zhongshan.glb`。模型清单和 `stats.json` 记录实际导出数据。运行脚本后，从最终 GLB 回读渲染的正面、右侧、侧前方实模图在 `renders/`。

在项目根目录使用 Blender 5.2.1 重建。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background data/landmarks/zhongshan/source.blend --python-exit-code 1 --python data/landmarks/zhongshan/build.py
```

| 网页版本 | 最终三角面 | GLB 大小 |
| --- | ---: | ---: |
| 南京城市沙盘 | 36,774 | 4,261,256 字节 |
| 全国地理沙盘 | 7,220 | 1,138,564 字节 |

## 展示锚点与出行入口

| 用途 | 地点 | 坐标（经度、纬度） |
| --- | --- | --- |
| 模型展示 | [祭堂建筑轮廓](https://www.openstreetmap.org/way/483693967)质心 | WGS84 `118.848288, 32.064383` |
| 驾车 | [中山陵停车场](https://ditu.amap.com/place/B0HGBZQ8WU)，玄武区石象路 7 号中山陵园风景区内 | GCJ-02 `118.851346, 32.048217` |
| 公交 | [中山陵停车场（公交站）](https://ditu.amap.com/place/BV11676369)，停车场旁的公交、景区观光车接驳点 | GCJ-02 `118.849568, 32.047947` |

祭堂地理朝向为南，模型按 Albers 投影在该点的正南方向绕世界 Y 轴旋转约 0.13949 弧度。全国视图下的模型最大边按约 25.3 个 CSS 像素（原始 38 像素的三分之二）展示，随相机缩放调整。模型与出行目的地分别登记在 `app/shared/landmarks.js`。自驾停车和景区接驳信息见[南京交管说明](https://www.nanjing.gov.cn/msxx/202509/t20250930_5660636.html)及[中山陵园管理局交通接驳信息](https://zschina.nanjing.gov.cn/fjms/fwzn/ggclx/)。

## 网页核验

Apple M5、Chrome 157 下用 1440 × 900 桌面窗口和 390 × 844 触屏模拟检查，模型资源返回 HTTP 200，网页无脚本错误或横向溢出。桌面可直接点击蓝瓦建筑，从标签或景点列表也可键盘选择。切换自驾和公交时，表单分别带入停车场和公交站。截图见 [全国视图](../web/全国视图.png) 与 [斜视近景](web/斜视近景.png)。
