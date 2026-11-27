from math import cos, sin, pi, sqrt
from geometry import *


def airplane():
    group('01 · Pressure hull')
    # Section heights follow the upswept tail cone and dropped radome of a single-aisle jet.
    stations=[(-5.62,.77,.045,.05),(-5.42,.80,.30,.26),(-5.10,.88,.49,.43),
              (-4.75,.97,.58,.54),(-4.22,1,.625,.62),(-3.55,1,.65,.65),
              (2.6,1,.65,.65),(3.35,1.02,.61,.60),(4.15,1.09,.46,.445),
              (5.1,1.17,.23,.23),(5.63,1.20,.065,.075)]
    shell=fuselage('Pressurised fuselage',stations,'pearl',32)
    def skin(y,z):
        for a,b in zip(stations,stations[1:]):
            if a[0]<=y<=b[0]:
                f=(y-a[0])/(b[0]-a[0])
                cz,rx,rz=[a[i]+f*(b[i]-a[i]) for i in [1,2,3]]
                return rx*sqrt(max(.001,1-((z-cz)/rz)**2))
    group('02 · Flight deck and cabin')
    for s in [-1,1]:
        for rows in [[(1.079,.018,.252),(1.116,.018,.288),(1.304,.020,.315),(1.344,.025,.288)],
                     [(1.121,.300,.365),(1.162,.307,.429),(1.317,.331,.431),(1.344,.307,.396)]]:
            front_decal(shell,'Flight-deck windscreen',rows if s==1 else opposite_rows(rows),'glass',5,3,lift=.021)
        for i in range(28):
            y=-3.66+i*.241
            if -1.1<y<-.72: continue
            profile=[(-.044,.087),(.041,.087),(.059,.055),(.059,-.052),(.037,-.082),
                     (-.036,-.082),(-.057,-.05),(-.057,.05)]
            panel('Cabin window',[(s*(skin(y+dy,1.15+dz)+.008),y+dy,1.15+dz)
                                  for dy,dz in profile],'glass')
        # Door outlines are flush with the fuselage; the cabin has no solid external pods.
        for y in [-4.02,3.09]:
            yz=[(y-.10,.82),(y+.12,.82),(y+.12,1.31),(y+.07,1.37),(y-.06,1.37),(y-.10,1.31)]
            pts=[(s*(skin(yy,zz)+.009),yy,zz) for yy,zz in yz]
            for p,q in zip(pts,pts[1:]+pts[:1]): beam('Door seam',p,q,.009,'steel')
        stripes=[(y,skin(y,.91)+.008,.88,.94) for y in [-4.70,-4.2,-3.55,2.6,3.35,4.10]]
        side_stripe('Waistline trim',s,stripes,'teal')

    def airfoil(name,s,sections,material):
        # wing stations: semispan, leading edge, trailing edge, mean height, thickness.
        rings=[]
        for span,lead,trail,z,thick in sections:
            rings.append([(span*s,lead+(trail-lead)*ch,z+thick*h)
                          for ch,h in [(0,0),(.14,.48),(.4,.54),(.74,.28),(1,0),(.55,-.31),(.12,-.29)]])
        return ring_loft(name,rings,material)
    group('03 · Wings and control surfaces')
    for s in [-1,1]:
        airfoil('Swept main wing',s,[(.42,-1.62,1.45,.74,.26),(1.6,-.82,1.55,.77,.19),
                (2.3,-.4,1.46,.83,.16),(4.65,.99,1.60,1.05,.09),(5.07,1.25,1.58,1.12,.045)],'silver')
        airfoil('Winglet',s,[(5.01,1.23,1.58,1.11,.06),(5.13,1.34,1.60,1.37,.05),
                (5.26,1.54,1.64,1.64,.035)],'teal')
        for x,y in [(1.57,1.51),(2.4,1.49),(3.1,1.51)]:
            fus = [(y-.36,.76+(x-1.5)*.07,.06,.075),(y+.05,.76+(x-1.5)*.07,.08,.08),
                   (y+.35,.77+(x-1.5)*.07,.025,.025)]
            o=fuselage('Flap track canoe',fus,'silver',8);o.location.x=s*x
        airfoil('Horizontal stabiliser',s,[(.2,3.50,5.00,1.17,.13),(2.23,4.82,5.20,1.50,.05)],'silver')
    ring_loft('Vertical stabiliser',[
        [(-.13,2.84,1.47),(.13,2.84,1.47),(.09,5.11,1.25),(-.09,5.11,1.25)],
        [(-.095,3.66,2.12),(.095,3.66,2.12),(.065,5.05,2.02),(-.065,5.05,2.02)],
        [(-.04,4.58,3.04),(.04,4.58,3.04),(.04,5.08,3.01),(-.04,5.08,3.01)]],'teal',False)
    for s in [-1,1]:
        panel('Tail diagonal',[(s*.099,3.8,2.16),(s*.074,4.98,2.39),
                                (s*.065,5.01,2.53),(s*.088,3.91,2.31)],'navy')
    group('04 · Turbofans')
    for s in [-1,1]:
        x=s*1.80
        box('Engine pylon',(x,-.72,.65),(.15,.93,.38),'steel',.065,2)
        # Continuous nacelle lip rolls into a real recessed intake ahead of the fan disk.
        engine=[(-1.98,.37,.327,.315),(-1.91,.37,.365,.35),(-1.70,.37,.394,.371),
                (-.98,.39,.35,.34),(-.55,.40,.23,.22)]
        rings=[[(x+rx*cos(k*2*pi/24),y,z+rz*sin(k*2*pi/24)) for k in range(24)] for y,z,rx,rz in engine]
        leading=rings[0]
        aperture=[(x+.279*cos(k*2*pi/24),-1.982,.37+.267*sin(k*2*pi/24)) for k in range(24)]
        inside=[(x+.26*cos(k*2*pi/24),-1.797,.37+.247*sin(k*2*pi/24)) for k in range(24)]
        outside=ring_loft('Engine nacelle',rings,'pearl'); outside.data.polygons[0].material_index=0
        # Remove the front cap instead of drawing a dark circle on a closed shell.
        import bmesh
        bm=bmesh.new();bm.from_mesh(outside.data);bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm,geom=[bm.faces[0]],context='FACES_ONLY');bm.to_mesh(outside.data);bm.free()
        for name,front,back,material in [('Intake rim',leading,aperture,'silver'),('Intake duct',aperture,inside,'gunmetal')]:
            mesh(name,front+back,[(i,(i+1)%24,(i+1)%24+24,i+24) for i in range(24)],material,True)
        cylinder('Fan face',(x,-1.79,.37),(x,-1.77,.37),.26,'seal',24)
        for i in range(12):
            theta=i*pi/6
            panel('Fan blade',[(x+r*cos(theta+t),y,.37+r*sin(theta+t)) for r,t,y in
                  [(.07,0,-1.82),(.243,.20,-1.812),(.248,.05,-1.808),(.082,-.15,-1.82)]],'steel')
        cylinder('Spinner',(x,-1.89,.37),(x,-1.79,.37),.022,'silver',14,.084)
        cylinder('Exhaust nozzle',(x,-.61,.405),(x,-.36,.405),.22,'gunmetal',18,.131)


def automobile():
    main='coral'
    group('01 · Painted shell')
    body=[(-2.23,.38,.66,.58,.77,.67,.66),(-2.14,.30,.78,.67,.87,.76,.79),
          (-1.83,.28,.81,.73,.915,.81,.84),(-.94,.27,.83,.82,.932,.90,.84),
          (.56,.27,.84,.84,.934,.91,.855),(1.53,.28,.82,.80,.916,.88,.84),
          (2.10,.33,.78,.75,.86,.82,.76),(2.20,.40,.70,.62,.78,.71,.68)]
    painted=vehicle_body('Painted unibody',body,main)
    box('Undertray',(0,0,.281),(1.42,3.64,.15),'gunmetal',.075,2)
    for s in [-1,1]:
        box('Rocker trim',(s*.868,.04,.32),(.077,2.36,.095),'gunmetal',.033,2)
    group('02 · Glazing and pillars')
    glass_sections=[(-1.06,.83,.84,.854,.852,.873,.812),(-.56,.85,.846,1.075,.813,1.295,.66),
                  (-.25,.86,.847,1.14,.811,1.427,.62),(.59,.86,.851,1.15,.812,1.430,.625),
                  (1.09,.86,.837,1.05,.801,1.264,.65),(1.49,.84,.801,.88,.807,.913,.728)]
    glass=vehicle_body('Continuous glazing',glass_sections,'glass')
    vehicle_body('Painted roof',[(-.39,1.388,.59,1.398,.622,1.426,.54),
              (-.19,1.410,.611,1.439,.623,1.466,.49),(.55,1.414,.613,1.439,.626,1.468,.50),
              (.75,1.378,.605,1.398,.627,1.431,.53)],main)
    for s in [-1,1]:
        for title,material,rows in [
            ('Windscreen frame',main,[(.882,-1.031,-.97),(1.08,-.798,-.735),(1.27,-.576,-.52),(1.40,-.302,-.248)]),
            ('B pillar','seal',[(.882,.096,.171),(1.224,.101,.176),(1.416,.12,.19)]),
            ('Rear screen frame',main,[(.888,1.399,1.463),(1.13,1.159,1.222),(1.26,1.024,1.088),(1.402,.600,.666)])]:
            flank_decal(glass,title,s,rows,material,.018)
        for y in [.138,.951]:
            flank_decal(painted,'Door shutline',s,[(.396,y-.02,y-.012),(.593,y-.01,y-.001),(.804,y,y+.009)],'gunmetal',.013)
        beam('Window beltline',(s*.857,-1.0,.869),(s*.857,1.39,.877),.018,'silver')
        for k in [-.17,.80]:
            box('Door handle',(s*.936,k,.786),(.035,.176,.036),'silver',.012,2)
        beam('Mirror arm',(s*.83,-.70,1.01),(s*.974,-.66,1.019),.028,'gunmetal')
        box('Wing mirror',(s*1.00,-.65,1.045),(.165,.213,.111),main,.044,2)
    group('03 · Lighting and wheels')
    for y in [-1.37,1.37]: axle_wheels(y,.335,.95,.335,.205,True)
    for s in [-1,1]:
        # Skin lamps wrap around both corners, matching the shoulder of each nose station.
        rows=[(.571,.405,.635),(.585,.352,.736),(.628,.379,.750),(.676,.597,.744)]
        front_decal(painted,'LED headlamp',rows if s==1 else opposite_rows(rows),'lamp',4,2,lift=.022)
        panel('Tail lamp',[(s*x,y,z) for x,y,z in
              [(.39,2.172,.646),(.77,2.142,.649),(.835,2.038,.73),(.75,2.125,.77),(.40,2.161,.716)]],'signal')
    front_decal(painted,'Grille surround',[(.427,-.43,.43),(.45,-.52,.52),(.578,-.539,.539),(.607,-.417,.417)],'gunmetal',6,2,lift=.019)
    for z in [.475,.532,.577]:
        front_decal(painted,'Grille blade',[(z,-.395,.395),(z+.012,-.409,.409)],'steel',6,1,lift=.031)
    front_decal(painted,'Number plate',[(.446,-.19,.19),(.545,-.19,.19)],'sign-plate',4,1,True,.047)


def bogie(y, half_width=.79):
    box('Bogie bolster',(0,y,.40),(1.35,1.18,.32),'gunmetal',.07)
    for yy in [y-.39,y+.39]:
        for s in [-1,1]:
            cylinder('Steel wheel tyre',(s*(half_width-.16),yy,.285),(s*half_width,yy,.285),.285,'gunmetal',12)
            cylinder('Wheel centre',(s*half_width,yy,.285),(s*(half_width+.018),yy,.285),.177,'steel',10)
    for s in [-1,1]:
        box('Bogie sideframe',(s*(half_width+.015),y,.37),(.13,1.15,.17),'steel',.056)
        for yy in [y-.38,y+.38]:
            cylinder('Axle box',(s*(half_width+.034),yy,.30),(s*(half_width+.105),yy,.30),.105,'gunmetal',10)


def pantograph(y,z,span=.80):
    for s in [-1,1]:
        for offset in [-.30,.30]:
            cylinder('Insulator',(s*.28,y+offset,z),(s*.28,y+offset,z+.13),.082,'seal',10)
        box('Pantograph base',(s*.28,y,z+.15),(.07,.78,.067),'steel',.018)
        start=(s*.255,y+.30,z+.17)
        elbow=(s*.23,y-.41,z+.42)
        end=(s*.17,y+.16,z+.71)
        beam('Lower lifting arm',start,elbow,.035,'gunmetal')
        beam('Upper lifting arm',elbow,end,.026,'gunmetal')
        beam('Guide link',(s*.255,y-.20,z+.17),(s*.23,y+.08,z+.34),.021,'steel')
    beam('Collector bow',(-span/2,y+.16,z+.72),(span/2,y+.16,z+.72),.030,'gunmetal')
    for s in [-1,1]:
        beam('Collector horn',(s*span/2,y+.16,z+.72),(s*(span/2+.12),y+.18,z+.65),.018,'gunmetal')


def rail_underfloor(front,rear):
    box('Underbody frame',(0,(front+rear)/2,.58),(1.31,rear-front,.32),'gunmetal',.09)
    for y in [front+.91,rear-.91]: bogie(y)
    box('Equipment enclosure',(0,(front+rear)/2,.40),(1.28,max(.55,rear-front-3.4),.34),'steel',.07)
    for s in [-1,1]:
        for end in [front,rear]:
            cylinder('Shock absorber',(s*.45,end,.55),(s*.45,end+.14,.55),.09,'gunmetal',12)


def coach_section(y,bottom=.64,top=2.39):
    return (y,bottom,.85,top-.31,.94,top,.76)


def locomotive():
    group('01 · Electric locomotive')
    front=-5.94
    rear=-.25
    shell=vehicle_body('Raked locomotive cab and machine room',[
        (front,.66,.70,1.25,.82,1.72,.73),(-5.80,.63,.84,1.58,.94,2.22,.75),
        coach_section(-5.53,top=2.46),coach_section(-.60,top=2.46),
        (-.37,.64,.84,1.54,.94,2.28,.76),(rear,.65,.75,1.47,.86,1.86,.73)],'green',False)
    for s in [-1,1]:
        rows=[(1.648,.055,.740),(1.691,.034,.755),(2.157,.038,.691),(2.191,.071,.646)]
        front_decal(shell,'Cab windscreen',rows if s==1 else opposite_rows(rows),'glass',4,1,lift=.016)
        side_panel('Cab side glazing',s,.949,[(-5.74,1.64),(-4.97,1.64),(-4.97,2.18),(-5.52,2.18)],'glass')
        side_stripe('Long waist stripe',s,[(-5.91,.845,1.34,1.44),(-5.80,.947,1.35,1.46),
                    (-.37,.947,1.35,1.46),(-.26,.87,1.35,1.45)],'cream')
        for y in [-4.31,-3.47,-2.63,-1.79]:
            box('Radiator face',(s*.949,y,1.83),(.023,.69,.52),'seal',.025)
            for i in range(4):
                box('Vent slat',(s*.966,y,1.62+i*.13),(.027,.61,.047),'green')
        for y in [-4.86,-.72]:
            for yy in [y-.16,y+.16]:
                beam('Cab access handrail',(s*.965,yy,.87),(s*.965,yy,1.70),.019,'silver')
            box('Cab steps',(s*.89,y,.69),(.17,.36,.085),'steel',.018)
        box('Lower face lamp box',(s*.56,-5.948,1.04),(.33,.09,.18),'gunmetal',.035,2)
        for x in [.50,.62]: cylinder('Locomotive lamp',(s*x,-6.001,1.05),(s*x,-5.97,1.05),.058,'lamp',12)
        beam('Windscreen wiper',(s*.18,-5.911,1.735),(s*.49,-5.839,2.002),.017,'seal')
    box('Nose waist stripe',(0,-5.945,1.39),(1.62,.016,.098),'cream')
    box('Lamp top housing',(0,-5.58,2.401),(.28,.23,.16),'green',.055,2)
    cylinder('Crown lamp',(0,-5.711,2.40),(0,-5.67,2.40),.086,'lamp')
    box('Front plough',(0,-5.94,.54),(1.55,.28,.25),'gunmetal',.065)
    box('Coupling shank',(0,-6.10,.61),(.25,.32,.14),'steel',.037)
    group('02 · Roof switchgear and chassis')
    rail_underfloor(-5.85,-.38)
    for y in [-5.06,-1.07]:
        pantograph(y,2.46)
    for yy in [-4.15,-1.97]:
        box('Roof cooling duct',(0,yy,2.51),(1.05,.72,.16),'steel',.055,2)
        for j in range(4):
            box('Louvre',(0,yy-.24+.16*j,2.601),(.81,.074,.028),'gunmetal')
    for yy in [-3.56,-2.58]:
        for s in [-1,1]:
            cylinder('High voltage bushing',(s*.36,yy,2.46),(s*.36,yy,2.70),.088,'gunmetal',10)
    beam('Roof busbar',(-.36,-3.56,2.71),(-.36,-2.58,2.71),.019,'steel')
    group('03 · Passenger coach')
    vehicle_body('Green passenger coach',[coach_section(.07),coach_section(.20,top=2.48),
                 coach_section(5.76,top=2.48),coach_section(5.94)],'green',False)
    vehicle_body('Arched carriage roof',[(.09,2.21,.91,2.30,.925,2.48,.74),
                 (.28,2.21,.93,2.35,.94,2.55,.70),(5.72,2.21,.93,2.35,.94,2.55,.70),
                 (5.91,2.21,.9,2.30,.925,2.48,.74)],'steel')
    for s in [-1,1]:
        for low,high in [(1.38,1.46),(2.14,2.18)]:
            side_stripe('Carriage waist stripe',s,[(.09,.947,low,high),(5.90,.947,low,high)],'cream')
        for i in range(8):
            y=.90+.591*i
            box('Window surround',(s*.944,y,1.85),(.03,.475,.47),'cream',.046,2)
            box('Carriage window',(s*.958,y,1.85),(.029,.42,.405),'glass',.040,2)
        for y in [.36,5.61]:
            box('Vestibule door',(s*.949,y,1.46),(.022,.39,1.23),'green',.03)
            box('Door glass',(s*.966,y,1.84),(.02,.27,.37),'glass',.033)
    for yy in [.35,5.64]:
        box('Roof fan housing',(0,yy,2.55),(.72,.39,.12),'silver',.055)
    box('Flexible gangway',(0,-.08,1.49),(1.24,.33,1.25),'rubber',.065)
    rail_underfloor(.1,5.85)


def emu(intercity=False):
    livery='blue' if intercity else 'red'
    shell='silver' if intercity else 'pearl'
    # The longer high-speed nose is noticeably lower and narrower than the regional cab.
    group('01 · Formed body and nose')
    if intercity:
        stations=[(-4.90,.61,.42,.91,.59,1.13,.42),(-4.64,.53,.68,1.23,.79,1.64,.57),
                 (-4.13,.51,.82,1.67,.92,2.16,.68),(-3.55,.51,.864,2.11,.97,2.50,.76),
                 (-2.94,.51,.865,2.13,.98,2.55,.76)]
    else:
        stations=[(-5.78,.55,.20,.66,.285,.78,.15),(-5.52,.49,.46,.79,.59,1.03,.36),
                  (-4.95,.47,.68,1.03,.79,1.32,.51),(-4.22,.46,.80,1.32,.90,1.68,.60),
                  (-3.57,.46,.86,1.68,.96,2.08,.65),(-2.70,.46,.87,1.99,.985,2.40,.74),
                  (-2.12,.46,.87,2.06,.985,2.46,.76)]
    shape=stations+[(4.54,)+stations[-1][1:],(4.73,)+stations[-1][1:]]
    tip=[(-5.16,.729,.10,.78,.16,.871,.10),(-5.08,.65,.30,.89,.41,1.00,.26)] if intercity else [(-5.87,.614,.072,.66,.12,.718,.064)]
    formed=vehicle_body('Monocoque head car',tip+shape,shell)
    def paint_at(st, values, material, name):
        for s in [-1,1]:
            side_stripe(name,s,[(t[0],t[4]+.009,low,high) for t,(low,high) in zip(st,values)],material)
    if intercity:
        paint_at(shape,[(.87,.987),(1.03,1.16),(1.17,1.31),(1.21,1.38),(1.24,1.40),(1.24,1.4),(1.24,1.4)],livery,'Regional blue ribbon')
    else:
        paint_at(shape,[(.63,.70),(.76,.86),(.99,1.095),(1.17,1.28),(1.26,1.37),(1.27,1.38),
                      (1.27,1.38),(1.27,1.38),(1.27,1.38)],livery,'Express speedline')
    window_rows=([(1.43,-.32,.32),(1.65,-.56,.56),(2.22,-.658,.658),(2.465,-.60,.60),(2.50,-.48,.48)]
                 if intercity else [(1.26,-.22,.22),(1.44,-.41,.41),(2.01,-.633,.633),(2.319,-.675,.675),(2.399,-.56,.56)])
    front_decal(formed,'Continuous driver windscreen',window_rows,'glass',8,4,lift=.046)
    for s in [-1,1]:
        cab_rows=([(1.66,-4.21,-3.30),(1.78,-4.073,-3.31),(2.05,-3.77,-3.32),(2.17,-3.61,-3.33)]
                 if intercity else [(1.66,-3.73,-2.46),(1.75,-3.62,-2.46),(1.99,-3.28,-2.47),(2.13,-3.01,-2.51)])
        flank_decal(formed,'Driver side glazing',s,cab_rows,'glass',.036,4,6)
        light_rows=([(1.098,.330,.438),(1.149,.350,.532),(1.223,.473,.585)]
                    if intercity else [(.916,.230,.337),(.954,.276,.398),(1.024,.369,.458)])
        front_decal(formed,'Nose light bezel',light_rows if s==1 else opposite_rows(light_rows),'steel',4,2,lift=.029)
        lamp_rows=[(z+.012,l+.025,r-.015) for z,l,r in light_rows]
        front_decal(formed,'Nose light',lamp_rows if s==1 else opposite_rows(lamp_rows),'lamp',4,2,lift=.042)
    group('02 · Passenger windows and doors')
    flank=stations[-1][4]
    for s in [-1,1]:
        first=-2.42 if intercity else -2.13
        side_stripe('Window shadow band',s,[(first,flank+.007,1.49,2.052),(4.65,flank+.007,1.49,2.052)],'seal')
        doors=[-2.06,1.31,3.93] if intercity else [-1.78,4.06]
        for i in range(12):
            y=first+.31+.563*i
            if y>=4.57 or any(abs(y-d)<(.49 if intercity else .42) for d in doors): continue
            box('Saloon window',(s*(flank+.015),y,1.77),(.025,.45,.43),'glass',.036,2)
        for y in doors:
            # Regional stock has visibly wider twin-leaf doors for shorter station stops.
            w=.75 if intercity else .51
            box('Doorframe',(s*(flank+.022),y,1.45),(.024,w+.043,1.32),'steel',.035)
            box('Plug door',(s*(flank+.036),y,1.45),(.024,w,1.28),shell,.03)
            for slide in ([-1,1] if intercity else [0]):
                box('Door glazing',(s*(flank+.054),y+slide*.17,1.80),(.023,.255 if intercity else .34,.456),'glass',.036)
            if intercity:
                box('Door centre seal',(s*(flank+.057),y,1.44),(.017,.017,1.25),'seal')
        beam('Skirt trim',(s*.934,-2.30,.61),(s*.934,4.56,.61),.023,'gunmetal')
    box('Rear gangway',(0,4.77,1.55),(1.18,.15,1.48),'gunmetal',.13,2)
    group('03 · Traction, suspension and rooftop')
    rail_underfloor(-3.95,4.65)
    pantograph(3.02,stations[-1][5],1.10)
    for y in ([.01,1.86] if intercity else [.80]):
        z=stations[-1][5]
        box('Air conditioning',(0,y,z+.091),(1.05,1.03,.18),'silver',.079,2)
        for i in range(5): box('Vent',(0,y-.34+i*.17,z+.185),(.72,.06,.025),'steel')
    if intercity:
        front_decal(formed,'Regional destination',[(2.28,-.30,.30),(2.354,-.31,.31)],'sign-intercity',4,2,True,.085)



def motorcoach():
    group('01 · Coachwork')
    shell=vehicle_body('High-deck touring coach',[(-4.26,.57,.77,1.14,.93,1.82,.74),
                 (-4.13,.46,.89,1.76,1.04,2.45,.85),(-3.73,.43,.92,2.31,1.071,2.80,.89),
                 (-3.33,.42,.93,2.43,1.075,2.91,.90),(3.55,.42,.93,2.43,1.075,2.91,.90),
                 (3.98,.47,.91,2.31,1.045,2.76,.85),(4.07,.54,.82,2.21,.95,2.60,.82)],'pearl')
    for s in [-1,1]:
        side_stripe('Touring blue lower coachwork',s,[(-4.13,1.041,.66,.83),(-3.73,1.078,.64,.84),(-2.92,1.080,.64,.92),
                    (1.9,1.08,.65,.95),(3.55,1.08,.68,1.25),(3.98,1.05,.74,1.29)],'blue')
        side_stripe('Continuous saloon glass',s,[(-3.87,1.067,1.73,2.37),(-3.45,1.08,1.65,2.50),
                    (3.49,1.08,1.66,2.50),(3.88,1.062,1.70,2.37)],'glass')
        for y in [-3.07,-2.08,-1.04,0,1.04,2.08,3.11]:
            box('Window mullion',(s*1.087,y,2.075),(.024,.052,.848),'seal')
        for y in [-.77,.13,1.03]:
            box('Luggage hold panel',(s*1.081,y,1.185),(.02,.84,.54),'silver',.031)
            box('Hold cover',(s*1.094,y,1.186),(.019,.793,.49),'pearl',.021)
            box('Recessed luggage handle',(s*1.109,y,1.375),(.019,.16,.039),'gunmetal',.01)
        for i in range(6):
            box('Engine intake grille',(s*1.077,3.24,1.035+i*.076),(.029,.70,.035),'gunmetal')
        beam('Mirror outrigger',(s*.94,-3.77,2.35),(s*1.22,-4.08,2.25),.041,'gunmetal')
        box('Touring mirror',(s*1.22,-4.09,2.13),(.12,.15,.31),'gunmetal',.048,2)
    # Lower step and glazed entry door on the kerb side.
    box('Entry surround',(1.084,-3.40,1.35),(.031,.63,1.46),'seal',.045)
    box('Entry glass',(1.104,-3.40,1.47),(.025,.54,1.14),'glass',.044)
    box('Entry seal',(1.124,-3.40,1.38),(.023,.03,1.29),'gunmetal')
    group('02 · Windscreen and lamps')
    front_decal(shell,'Panoramic windscreen',[(1.435,-.68,.68),(1.47,-.84,.84),(1.59,-.901,.901),
                (2.26,-.887,.887),(2.54,-.82,.82),(2.60,-.73,.73)],'glass',12,4,lift=.038)
    front_decal(shell,'Coach destination',[(2.28,-.405,.405),(2.425,-.404,.404)],'sign-coach',6,3,True,.065)
    for s in [-1,1]:
        beam('Windscreen wiper',(s*.10,-4.265,1.58),(s*.68,-4.232,1.84),.018,'seal')
        border=[(.970,.491,.793),(1.05,.485,.854),(1.15,.571,.863)]
        lamps=[(1.001,.52,.775),(1.063,.515,.826),(1.111,.597,.827)]
        front_decal(shell,'Headlight bezel',border if s==1 else opposite_rows(border),'gunmetal',4,2,lift=.021)
        front_decal(shell,'Coach headlight',lamps if s==1 else opposite_rows(lamps),'lamp',4,2,lift=.030)
        box('Tail lamp',(s*.80,4.055,1.40),(.13,.061,.54),'signal',.039,2)
    box('Front grille',(0,-4.252,.84),(.93,.043,.13),'seal',.029)
    box('Chassis',(0,0,.46),(1.65,7.28,.35),'gunmetal',.15,2)
    group('03 · Running gear and roof equipment')
    for y in [-2.60,2.42]: axle_wheels(y,.47,1.094,.47,.20,True)
    box('Roof HVAC',(0,.32,3.025),(1.37,2.18,.235),'silver',.11,3)
    for yy in [-.15,.77]:
        cylinder('AC fan shroud',(0,yy,3.138),(0,yy,3.169),.324,'gunmetal',20)
        for i in range(5): box('AC fan guard',(0,yy-.21+i*.105,3.17),(.41,.028,.02),'steel')
    for yy in [-2.13,2.57]: box('Escape hatch',(0,yy,2.929),(.78,.60,.05),'silver',.058,2)


def ferry():
    group('01 · Twin hulls and wet deck')
    for s in [-1,1]:
        hull=[(-4.99,.65,.025,.82,.04,1.0,.03),(-4.76,.28,.04,.83,.14,1.00,.16),
              (-4.10,.10,.13,.71,.34,1.035,.33),(-2.87,.028,.24,.69,.41,1.044,.38),
              (2.81,.008,.27,.68,.435,1.03,.39),(4.14,.17,.24,.72,.376,1.04,.34)]
        h=vehicle_body('Wave-piercing demi-hull',hull,'pearl');h.location.x=s*.86
        for q in [-1,1]:
            stripe=[(-4.83,.102,.67,.77),(-4.1,.346,.54,.65),(-2.87,.417,.49,.61),(2.81,.439,.50,.62),(4.14,.383,.52,.64)]
            mark=side_stripe('Blue boot top',q,stripe,'navy');mark.location.x=s*.86
    vehicle_body('Bridging deck and bow visor',[(-4.56,.82,.57,.97,.76,1.02,.75),(-3.85,.71,.82,1.00,1.08,1.08,1.05),
                 (-2.85,.69,1.17,1.02,1.27,1.12,1.18),(3.97,.70,1.15,1.00,1.23,1.09,1.15)],'pearl')
    vehicle_body('Foredeck',[(-4.50,1.008,.63,1.012,.67,1.029,.65),(-3.86,1.054,.96,1.057,.99,1.084,.97),
                 (-2.85,1.102,1.12,1.107,1.17,1.134,1.15),(3.95,1.074,1.12,1.081,1.16,1.112,1.14)],'steel',False)
    group('02 · Saloon and wheelhouse')
    lowerdeck=vehicle_body('Main deck saloon',[(-3.24,1.10,.92,1.48,.93,1.63,.79),
                 (-2.91,1.10,1.03,1.77,1.01,1.97,.94),(2.85,1.08,1.03,1.79,1.03,1.98,.94),
                 (3.18,1.08,.92,1.73,.97,1.93,.89)],'pearl',False)
    for s in [-1,1]:
        side_stripe('Saloon glazing',s,[(-3.15,.958,1.46,1.57),(-2.89,1.027,1.47,1.78),
                    (2.83,1.036,1.47,1.79),(3.07,.998,1.48,1.75)],'glass')
        for i in range(12):
            y=-2.68+i*.485
            box('Salon mullion',(s*1.040,y,1.63),(.029,.062,.32),'pearl')
        side_stripe('Sheer stripe',s,[(-3.11,.977,1.26,1.35),(-2.89,1.042,1.26,1.35),(2.84,1.042,1.27,1.36),(3.08,.999,1.27,1.36)],'blue')
    box('Upper promenade deck',(0,-.01,1.99),(2.20,6.39,.116),'pearl',.072,2)
    bridge=vehicle_body('Raised wheelhouse',[(-2.70,2.03,.66,2.26,.76,2.45,.66),(-2.38,2.03,.85,2.54,.87,2.73,.76),
                 (.64,2.03,.85,2.52,.87,2.71,.76),(1.04,2.03,.75,2.38,.79,2.57,.66)],'pearl',False)
    for s in [-1,1]:
        for obj,title,rows in [(bridge,'Wheelhouse front glazing',[(2.278,.018,.625),(2.316,.018,.700),(2.561,.022,.702),(2.593,.026,.659)]),
                               (lowerdeck,'Forward saloon glass',[(1.444,.025,.818),(1.481,.022,.864),(1.732,.022,.837),(1.759,.026,.79)])]:
            front_decal(obj,title,rows if s==1 else opposite_rows(rows),'glass',5,2,lift=.025)
        side_stripe('Bridge glazing',s,[(-2.61,.801,2.32,2.43),(-2.37,.876,2.32,2.57),(.60,.877,2.32,2.56),(.91,.82,2.32,2.47)],'glass')
        for yy in [-1.82,-1.18,-.54,.10]:
            box('Bridge window post',(s*.883,yy,2.445),(.022,.064,.264),'pearl')
    box('Bridge roof visor',(0,-.86,2.73),(1.78,3.13,.105),'pearl',.08,2)
    group('03 · Deck fittings and navigation equipment')
    for s in [-1,1]:
        for y in [1.29,2.03,2.73]:
            cylinder('Inflatable liferaft canister',(s*.68,y-.18,2.18),(s*.68,y+.18,2.18),.125,'pearl',14)
            box('Raft cradle',(s*.68,y,2.064),(.24,.40,.05),'gunmetal',.03)
        # Bow and stern rails are open geometry.
        for side,points in [('Fore',[(-4.45,.61,1.04),(-3.83,.96,1.09),(-3.31,1.11,1.12)]),
                            ('Aft',[(.98,1.04,2.04),(2.00,1.04,2.04),(3.08,1.04,2.04)])]:
            for yy,xx,zz in points:
                beam(side+' rail stanchion',(s*xx,yy,zz),(s*xx,yy,zz+.27),.024,'silver')
            for a,b in zip(points,points[1:]):
                for ht in [.14,.27]:
                    beam('Deck rail',(s*a[1],a[0],a[2]+ht),(s*b[1],b[0],b[2]+ht),.016,'silver')
        # Stern mooring bitt.
        cylinder('Mooring bitt',(s*.83,3.47,1.11),(s*.83,3.47,1.25),.066,'gunmetal',10)
    beam('Radar mast',(0,.10,2.74),(0,.28,3.40),.05,'pearl')
    box('Radar scanner',(0,.27,3.40),(.81,.13,.11),'silver',.046,2)
    beam('VHF aerial',(0,.36,2.76),(0,.48,3.54),.019,'gunmetal')
    for s in [-1,1]:
        # Four white grab bands divide the orange ring mounted on the upper promenade.
        for j in range(16):
            def ring_point(theta):
                return (s*1.066,1.18+.14*cos(theta),2.22+.14*sin(theta))
            cylinder('Lifebuoy',ring_point(j*pi/8),ring_point((j+1)*pi/8),.034,'pearl' if j%4==0 else 'coral',7)
        cylinder('Funnel',(s*.36,1.18,2.04),(s*.36,1.39,2.61),.175,'blue',14,.144)
        cylinder('Funnel top',(s*.36,1.36,2.55),(s*.36,1.41,2.68),.148,'gunmetal',14)
