# 路线交通工具模型

这七个模型随城际路线移动。车身、车窗、轮架、机翼、桅杆等构件保存在各自的 Blender 母版内。模型都是原创通用外形，同类车次、航班和航线共用对应车型。普速客车保留一节机车和一节缩短的客车，高铁和城际动车各保留一节头车，在全国比例下能看出三种不同的车头。

| 模型 | 保留的主要特征 | 可编辑母版 | 沙盘资源 |
| --- | --- | --- | --- |
| 民航客机 | 后掠翼、翼梢小翼、带凹入进气口的双发动机和青色垂尾 | [母版](plane/source.blend) | [GLB](../../app/public/models/vehicles/plane.glb) |
| 自驾汽车 | 珊瑚红三厢、深色侧窗、车灯和五辐轮圈 | [母版](car/source.blend) | [GLB](../../app/public/models/vehicles/car.glb) |
| 普速列车 | 墨绿平头机车、受电弓、客车窗列和金色腰线 | [母版](train/source.blend) | [GLB](../../app/public/models/vehicles/train.glb) |
| 高铁 | 长鼻、红色侧带、连续前风挡和车顶电气设备 | [母版](high-speed-rail/source.blend) | [GLB](../../app/public/models/vehicles/high-speed-rail.glb) |
| 城际列车 | 较短的银蓝驾驶端、双扇宽客门和车头目的地显示牌 | [母版](intercity-rail/source.blend) | [GLB](../../app/public/models/vehicles/intercity-rail.glb) |
| 长途大巴 | 高层连窗、车下行李舱、两轴、长臂后视镜和屋顶空调 | [母版](coach/source.blend) | [GLB](../../app/public/models/vehicles/coach.glb) |
| 城际客轮 | 双船艏间的真实开口、蓝色水线、两层客舱、露天甲板栏杆和雷达 | [母版](ferry/source.blend) | [GLB](../../app/public/models/vehicles/ferry.glb) |

[参考与提示词](references/README.md) 保存实物来源、ImageGen 的正面／侧面／斜前方三视设计图，以及设计图与母版的取舍。各模型目录中的 `renders/front.png`、`side.png` 和 `three-quarter.png` 从最终 GLB 重新导入后渲染。模型统计、包围盒和 SHA-256 在[全国版清单](../../app/public/models/vehicles/manifest.json)内。

## 重建

已使用 Blender 5.2.1（Python API）验证。在项目根目录执行以下命令。macOS 可将示例中的 `blender` 替换为 `/Applications/Blender.app/Contents/MacOS/Blender`。

```sh
blender -b --python-exit-code 1 --python data/vehicles/build.py
```

只导出指定车种，或重新读取指定 GLB 出图时，可分别执行以下命令。

```sh
blender -b --python-exit-code 1 --python data/vehicles/build.py -- --stage export car train
blender -b --python-exit-code 1 --python data/vehicles/build.py -- --stage render car train
```

[造型脚本](vehicles.py)定义每种载具的几何和分组。[几何与材质](geometry.py)定义放样截面、标准色、基于物理的表面材质和轮组。标牌 PNG 已随源文件提供并打包在相应母版和 GLB 内。更新文字时，用安装了 Pillow 的 Python 运行 `python3 data/vehicles/make_signs.py`。可以用环境变量 `VEHICLE_SIGN_FONT` 指定带中文字形的字体路径。

母版以包围盒的底面中心为原点，Z 向上、车头朝 −Y。导出后的 GLB 为 Y 向上、车头朝 +Z，最低点为零。飞机按巡航姿态收起起落架。各车种用独立的等比显示尺寸；资产自身的单位为微缩造型单位。导出将同一模型合为一个网格，按材质分组渲染。普速列车因含两节车体，网页副本简化了小构件的倒角，母版仍保留圆角修改器。建模脚本、源标牌和输出均位于本项目，重建无网络依赖。

## 路线动画验收

南京至黄山的自驾演示沿驾车折线播放。公共交通查询返回的 G8965、G7207 分别沿所选方案的铁路轨迹播放。切换方案保留镜头，可在地图标题旁暂停或继续。系统开启减弱动态效果时，需要手动播放。同城行程及市内接驳段只显示已有线路。

飞机接驳缺少实际航迹时，可在航段里开启「预览机场间示意航线」。此时飞机沿两座机场之间的示意弧线移动。地图以虚线标示，班次仍待确认。

网页验收覆盖桌面与手机尺寸。南京至黄山的驾车、高铁及机场间示意均经浏览器验证。另用分段样例覆盖七款 GLB 加载、同城隐藏、暂停恢复与切换后的定位。

[桌面自驾截图](../../output/城际路线动画/南京至黄山自驾.png) · [桌面高铁截图](../../output/城际路线动画/南京至黄山高铁.png) · [手机高铁截图](../../output/城际路线动画/南京至黄山高铁手机.png) · [机场间示意截图](../../output/城际路线动画/南京至黄山机场间示意航线.png)
