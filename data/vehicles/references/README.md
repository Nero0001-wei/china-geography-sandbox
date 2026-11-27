# 路线交通工具建模参考 · v1

本批模型服务于中国地理沙盘的路线演示，采用当代民用交通工具外形。下列实物资料用来校正轮廓和构件位置。颜色和条带按沙盘的七种方式自行搭配。查询日期为 2026 年 11 月 26 日。

| 模型 ID | 参考车型、识别部位与本版取舍 | 实物资料 |
| --- | --- | --- |
| `plane` | 单通道双发客机。两侧翼下各有一个圆形发动机进气口，俯视保留后掠主翼、平尾和青蓝色垂尾。飞行姿态收起起落架。A320 的机长约 37.6 米、带翼梢小翼时翼展约 35.8 米，二者接近。 | [空中客车 A320 系列尺寸表，第 5 页](https://www.airbus.com/sites/default/files/2025-04/Airbus-A320-Family-Facts-and-Figures-April-2025.pdf) |
| `car` | 参考紧凑型四门三厢轿车。前机盖、拱起的车顶和较短的行李厢构成三个体块。珊瑚红车身配深色玻璃，车顶平整。 | [大众汽车 Jetta 外观资料](https://www.vw.com/en/models/jetta.html/__layer/layers/showrooms/jetta/_2025/explore_the_jetta/exterior/exterior/master.layer) |
| `train` | 参考机车牵引的普速客运列车。保留方形驾驶室、双前窗、车顶受电弓与一节缩短的客车，用墨绿与奶油金腰线连贯车身。HXD3D 是机车结构的参考，这个通用模型也可用于不同普速车次。 | [中车大连 HXD3D 干线客运电力机车](https://www.crrcgc.cc/dl/2016-04/20/article_D801B2B30B0E487880A9ED77E479BC3B.html) |
| `high-speed-rail` | 参照 CR400AF 的长鼻、前风挡与平顺车体。选取流线形头车代表高速动车组，白色壳体加细红带，在俯视时与常规机车区分。 | [中车青岛四方 CR400AF 型动车组](https://www.crrcgc.cc/sfgf/2015-11/04/article_E7691BD1DADD4C799E29B682C86DADD3.html) |
| `intercity-rail` | 参照 CRH6A 的折面前风挡、短流线车头和宽客门。银色车体用两条深蓝腰线标出，C 字头城际列车采用这一通用外形。 | [中车四方 CRH6A 城际动车组](https://www.crrcgc.cc/sfgf/2017-12/08/article_AA4E578E91F441E2BC5554104D1F98B3.html) |
| `coach` | 参考 12 米级长途大巴。高地板把一排侧窗抬高，行李舱门占据车身下侧板，前端保留大幅弧形风挡。车身蓝白两色。 | [宇通 T12 公路客车与行李舱参数](https://en.yutong.com/products/T12-param.shtml) |
| `ferry` | 选取往返沿海城市的双体高速客轮。正面能看到两只船艏与其间的开口，侧面可辨双层客舱、驾驶室和蓝色水线。 | [Incat Crowther 的 40 米双体客轮设计](https://www.incatcrowther.com/ships/ferries/commuter/ic17109/) · [金光飞航港澳船队](https://m.cotaiwaterjet.com/en/our-ferries.html) |

## 参考图与坐标

各图从左到右为正面、侧面、略俯视的前侧视角，位置索引如下。文本文件保留整段 ImageGen 输入，图内没有车型文字。普速列车用机车和一节短客车表现传统编组，高铁与城际列车各用一节头车。长途大巴的生成参考画出了三根车轴，母版按 12 米级客车保留前、后两轴。

| 参考图 | 从上到下 | 提示词 |
| --- | --- | --- |
| [航空参考](air.png) | 飞机 | [原文](air.prompt.txt) |
| [自驾与铁路参考](core.png) | 自驾车、普速列车、高铁头车 | [原文](core.prompt.txt) |
| [城际交通参考](regional.png) | 城际列车、长途大巴、城际客轮 | [原文](regional.prompt.txt) |

Blender 母版采用 Z 向上、行进方向朝 −Y。导出后 GLB 采用 Y 向上、行进方向朝 +Z。每种车都以自身的最长尺寸确定展示比例，路线动画沿路段切线转向。飞机与轿车在地图上采用各自可辨认的显示尺度。设计图是体块与色彩参考，最终车窗数、转向架和车身细节以重新导入 GLB 的实模图为准。
