# 中国地理沙盘

全国三维地形沙盘，支持搜索并定位地图地点、点选景点模型、搜索起终点和多种出行方式。网页端使用 Vite、React 和 Three.js，运行时直接读取项目内的地形与边界资产。

## 本地运行

需要 Node.js 20.19+ 或 22.12+。

```sh
cd app
npm ci
npm run dev
```

打开终端显示的本地地址。按住鼠标中键或右键拖动可平移地图，左键拖动地图空白处可旋转视角，滚动滚轮可缩放。触屏上可单指旋转、双指缩放和平移。用地图右侧的按钮切换正上方俯瞰、恢复全国视角、控制图层。点击陆地可读取坐标和海拔。右侧可以定位三级地势的代表性地貌、查看北纬 32° 剖面和南海诸岛附图。

用地图左上方的搜索框查找景点、省市或地貌。输入部分名称或地点加景点名（如「北京 故宫」），点击结果即可定位，也可用方向键和回车选择。地图搜索使用本地数据。

```sh
npm run build
npm run preview
```

## 静态预览构建

在 `app/` 运行 `npm run build -- --mode pages`，生成适合 GitHub Pages 仓库子路径的 `dist/`。可用 `npm run preview -- --mode pages` 在本地查看。此构建包含三维沙盘、地图搜索、景点和南京至黄山的内置线路。高德实时算路、地点联想与定位地址查询由本地服务提供，静态构建无需读取高德 Key。

`app/.env.local` 由 Git 忽略。公开部署完整沙盘前，请核对当前版本的底图公开使用授权和审图材料。[行政边界与附图](data/行政边界与附图.md)

## 南京至黄山驾车路线

打开网页，在「路线规划」窗口选择「体验南京至黄山路线」，或在本地网址后加 `?route=nanjing-huangshan`。沙盘会标出起终点并框入全程。旋转或缩放后可用「路线全览」返回，也可用「在高德查看」打开相同起终点。

- **起点和终点。** 南京采用玄武区石象路 7 号中山陵停车场，黄山采用黄山区汤口镇寨西的新国线黄山风景区游客集散中心。高德 POI 和原始 GCJ-02 坐标保存在[端点清单](app/shared/route-endpoints.js)。[南京停车场](https://ditu.amap.com/place/B0HGBZQ8WU) · [黄山集散中心](https://ditu.amap.com/place/B022F002XB)
- **内置路网参考。** [保存的路线](app/src/routes/nanjing-huangshan.json)来自一次 OSRM 小汽车算路，约 296.2 公里、3 小时 30 分，不计实时路况。请求使用两个 POI 的近似 WGS84 坐标，路网吸附距离分别约为 4 米和 19 米。原结果含 2,477 个点，内置折线按约 40 米容差简化至 358 点，里程和用时保留服务返回值。[复算同一请求](https://routing.openstreetmap.de/routed-car/route/v1/driving/118.846263,32.050379;118.171165,30.068529?overview=full&geometries=geojson&steps=true) · [OSRM 服务](https://routing.openstreetmap.de/about.html) · [© OpenStreetMap contributors，ODbL](https://www.openstreetmap.org/copyright)
- **高德查询。** 在 `app/.env.local` 设置 `AMAP_WEB_SERVICE_KEY` 为高德 Web 服务 Key，重启本地服务后重新打开路线。Vite 的 dev 和 preview 模式均通过同源 `GET /api/routes/nanjing-huangshan` 算路。成功时地图、里程、用时和来源一起更新。无 Key、无可行路线或请求失败时，页面保留内置路网参考并说明状态。仅部署 `dist/` 的静态站点需要另行部署该服务才能调用高德。[驾车规划接口](https://lbs.amap.com/api/webservice/guide/api/newroute)
- **地图对齐。** 高德查询及跳转使用 GCJ-02，返回的路线折线近似反算为 WGS84 后再投影到地形。OSRM 折线直接使用 WGS84。沙盘沿高程网格对路线补点，适合看跨省走向。

## 数据与验证

- [中国及周边地表底图，8710 × 6910 WebP](data/全国地表贴图.webp)；境内近景另有约 256 米/像素的[分块贴图](app/public/data/atlas/detail)
- [地形高程、卫星底色与山体晕渲](data/地形数据.md)
- 网页实测截图：[华东平原放大前后对照](output/地形贴图/华东平原对比.jpg) · [横断山脉明暗对照](output/地形贴图/山地明暗对比.jpg) · [桌面全国视图](output/地形贴图/全国视图.png) · [手机全国视图](output/地形贴图/手机视图.png)
- [海岸、水系与海底深度分带](data/海岸与水系.md)
- [行政边界与南海诸岛附图](data/行政边界与附图.md)

现代地图收录 117 处景点，覆盖 34 个省级行政区。展开工具栏的「景点」，可同时勾选多个类型和级别。景点需同时符合勾选的类型和级别，单选「博物馆与纪念地」会显示含中国国家博物馆在内的 14 处。取消勾选「显示景点名称」后，仍可点选模型、点位和数字聚合标记。全国视角优先显示全国代表，密集的同城景点合并标注，放大后展开。模型按主体 WGS84 坐标定位，进入视野时按需加载。[补录 17 处与验收](data/landmarks/web/现代地图补录17处验收.md) · [桌面预览](data/landmarks/web/117处全国总览.png) · [手机全国预览](data/landmarks/web/117处手机全国.png) · [模型清单](app/public/models/manifest.json)

[首批名单和选点依据](全国景点候选清单.md) · [首批逐项验收](data/landmarks/web/首批30处网页验收.md) · [沙盘出行规划设计](出行规划设计.md)。边界采用学习交流用数据，正式公开前需使用有相应用途授权的数据并按规定校核。


点选景点模型或名称可在地图左下角查看介绍、两条现场看点、资料来源和实景照片。照片随详情按需加载，详情卡里的「设为目的地」使用当前出行方式对应的已登记到达点。[景点介绍数据](app/src/landmark-guides.json) · [照片作者与授权](app/public/data/landmark-photos/ATTRIBUTIONS.md)

所有景点模型的正面默认沿所在位置的经线朝地理正南，重置视角时恢复该朝向。拖动地图空白处可绕看整张沙盘，左右拖动一个景点可单独转动它。键盘聚焦景点标签后，左右方向键每次转动 15°。

## 切换交通路网

点击沙盘右上角的「自然地形」或「交通路网」可直接切换底图。也可用 `?basemap=roads` 直接打开路网模式，此参数可与路线示例一起使用。切换底图保留视角和正在播放的车辆。

全国主要公路随项目提供；放大后，沙盘会按视野从 OpenFreeMap 加载更详细的 OpenStreetMap 道路。街道数据暂时不可用时仍可看全国概览。路网底图无需新增 Key，高德算路继续使用原有配置。[数据来源与重建方法](data/全国路网.md)

## 更新景点模型

各景点的取景资料、参考图、母版、重建命令和实模图保存在 `data/landmarks/<ID>/`。类型、展示级别、地理锚点与原始朝向记录写在 `site.json`。网页按 GLB 局部 +Z 为正面，将正面转向地理正南。按景点 README 导出 GLB 后，在项目根目录运行 `python3 scripts/sync_landmarks.py`，核对二进制 GLB 的面数、大小和 SHA-256 并更新网页目录。核实后的高德出行入口可登记在[到达点清单](data/landmarks/arrival-points.json)。

网页从画面左上方打光，用较弱的环境光保留背光面。模型更新后，可在项目根目录运行以下命令，按真实网格重新计算屋檐、门洞和构件交接处的顶点环境遮蔽。中山陵使用母版自带的顶点颜色。

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python scripts/bake_landmark_occlusion.py
```

## 重建网页贴图

按上述地形与水系说明生成陆地和水文中间纹理后，在项目根目录执行以下命令。

```sh
.venv/bin/python scripts/pack_atlas.py \
  --relief /tmp/china-atlas-texture/relief-color.webp \
  --hydro /tmp/china-atlas-texture/hydrography.webp \
  --export data/全国地表贴图.webp
```

在同一投影上生成近景切片。第一次构建会下载约 2.49 GB 的 USGS 高程原档，之后可复用缓存。

```sh
.venv/bin/python scripts/prepare_detail_dem.py /tmp/china-relief-input/detail-dem.vrt
.venv/bin/python scripts/build_detail_tiles.py \
  --dem /tmp/china-relief-input/detail-dem.vrt \
  --imagery /tmp/china-relief-input/world.200408.3x21600x21600.C1.jpg /tmp/china-relief-input/world.200408.3x21600x21600.D1.jpg \
  --cover /tmp/china-relief-input/cover.vrt \
  --cache /tmp/china-atlas-texture/sources \
  --hydro /tmp/china-atlas-texture/hydrography.webp \
  --base data/全国地表贴图.webp
```

网页先显示总览图，随屏幕像素密度按需读取 30 个区域分块，以及覆盖中国陆地和近岸的 111 个近景分块。近景网格以约 256 米间距采样，东西、南北两个方向的采样密度均为区域图的 4 倍。近景河湖与岸线依据矢量重新绘制，山体按细分高程计算光照。三层共用 Albers 投影，切换时保持地理位置对齐。
