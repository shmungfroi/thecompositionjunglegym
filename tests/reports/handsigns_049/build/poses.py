"""The seventeen poses. Angles in degrees; each joint bends only the way a real one does."""
import numpy as np
from hand3d import Hand
flat = dict(index=(4, 7, 4), middle=(2, 5, 3), ring=(5, 8, 5), little=(9, 13, 7))
soft = dict(index=(10, 14, 8), middle=(7, 11, 6), ring=(12, 16, 9), little=(18, 22, 12))
droop = dict(index=(14, 20, 10), middle=(19, 24, 12), ring=(24, 28, 14), little=(29, 32, 16))
cupd = dict(index=(14, 22, 12), middle=(17, 25, 13), ring=(21, 28, 15), little=(26, 32, 17))
fist = dict(index=(74, 96, 62), middle=(78, 98, 64), ring=(80, 100, 66), little=(82, 100, 68))
loose = dict(index=(66, 90, 55), middle=(72, 94, 58), ring=(76, 96, 60), little=(78, 96, 62))
point = dict(index=(-4, 5, 3), middle=(78, 98, 64), ring=(80, 100, 66), little=(82, 100, 68))
tog = dict(index=3, middle=0, ring=-2, little=-6); fan = dict(index=13, middle=3, ring=-8, little=-20)
T_along = [(-.84, -.22, .50), (-.96, -.09, .26), (-.99, -.03, .14), (0, .45, .9)]
T_up = [(-.80, -.12, .58), (-.60, 0, .80), (-.46, .05, .89), (0, 1, 0)]
T_wide = [(-.50, -.15, .85), (-.30, 0, .95), (-.12, .05, .99), (0, 1, 0)]
T_fist = [(-.82, -.26, .51), (-.93, -.34, -.12), (-.88, -.36, -.30), (-.3, -.3, .9)]
T_down = [(-.74, -.60, .32), (-.30, -.95, .10), (-.18, -.98, .02), (-1, 0, .2)]
T_thup = [(-.85, -.10, .52), (-.32, 0, .95), (-.14, .05, .99), (0, 1, 0)]
T_drop = [(-.80, -.50, .34), (-.62, -.76, .20), (-.55, -.82, .12), (-.6, .3, .7)]
T_hang = [(-.82, -.36, .44), (-.92, -.28, .26), (-.95, -.26, .16), (0, .45, .9)]
SIG = {
 'mi': dict(flex=flat, spread=tog, thumb=T_along, elev=32, yaw=-8, pitch=0),
 're': dict(flex=flat, spread=tog, thumb=T_along, elev=30, yaw=-8, pitch=28),
 'ri': dict(flex=flat, spread=tog, thumb=T_along, elev=28, yaw=-8, pitch=50),
 'me': dict(flex=soft, spread=tog, thumb=T_along, elev=32, yaw=-8, pitch=-28),
 'ra': dict(flex=flat, spread=tog, thumb=T_drop, elev=26, yaw=-8, pitch=28),
 'do': dict(fill=(26, -24), flex=fist, spread=tog, thumb=T_fist, elev=26, yaw=-14, pitch=0),
 'di': dict(fill=(26, -24), flex=fist, spread=tog, thumb=T_fist, elev=26, yaw=-14, pitch=28),
 'fa': dict(fill=(26, -24), flex=loose, spread=tog, thumb=T_down, elev=20, yaw=-14, pitch=0),
 'fi': dict(fill=(26, -24), flex=loose, spread=tog, thumb=T_thup, roll=82, elev=10, yaw=-10, pitch=0),
 'so': dict(flex=soft, spread=tog, thumb=T_up, roll=80, elev=10, yaw=-6, pitch=0),
 'si': dict(flex=flat, spread=fan, thumb=T_wide, roll=78, elev=10, yaw=-6, pitch=16),
 'se': dict(flex=soft, spread=tog, thumb=T_up, roll=74, elev=14, yaw=-6, pitch=-30),
 'la': dict(flex=droop, spread=tog, thumb=T_hang, wrist=(46, 0), elev=10, yaw=-20, pitch=4),
 'le': dict(flex=droop, spread=tog, thumb=T_hang, wrist=(58, 0), elev=10, yaw=-20, pitch=-7),
 'li': dict(flex=cupd, spread=tog, thumb=T_up, wrist=(14, 0), roll=180, elev=40, yaw=14, pitch=8, cup=2),
 'ti': dict(fill=(8, -24), flex=point, spread=tog, thumb=T_fist, elev=24, yaw=-12, pitch=36),
 'te': dict(fill=(8, -24), flex=point, spread=tog, thumb=T_fist, elev=30, yaw=-12, pitch=-36),
}
ORDER = ['do', 'di', 'ra', 're', 'ri', 'me', 'mi', 'fa', 'fi', 'se', 'so', 'si', 'le', 'la', 'li', 'te', 'ti']
def hand(n, **kw):
    a = dict(SIG[n]); a.update(kw); return Hand(**a)

WIN_L = (270, 216); WIN_S = (235, 188)
_fr = {}
def frame(n, small=False):
    """centre the drawing in the window; shorten the forearm if the pose would not fit"""
    key = (n, small); WIN = WIN_S if small else WIN_L
    if key in _fr: return _fr[key]
    arm = 30 if small else 58
    for _ in range(3):
        h = hand(n, arm=arm); R = h.render(win=(600, 600), ppm=0.5, centre=(-60, 0)); m = ~np.isnan(R['Z']); ys, xs = np.where(m)
        x0, x1 = xs.min() / .5 - 300 - 60, xs.max() / .5 - 300 - 60; y1, y0 = 300 - ys.min() / .5, 300 - ys.max() / .5
        ex = max((x1 - x0) - (WIN[0] - 14), (y1 - y0) - (WIN[1] - 14))
        if ex <= 0 or arm <= 14: break
        arm = max(14, arm - ex * 1.1)
    _fr[key] = dict(arm=arm, centre=((x0 + x1) / 2, (y0 + y1) / 2), win=WIN); return _fr[key]
