import sys, numpy as np, poses, time
from PIL import Image
names = sys.argv[1:] or poses.ORDER; ppm = 0.9; tiles = []
L = np.array([-0.5, 0.75, 0.45]); L /= np.linalg.norm(L)
for n in names:
    t0 = time.time(); h = poses.hand(n); R = h.render(ppm=ppm)
    sh = np.clip(R['N'] @ L, 0, 1) * 0.75 + 0.25; img = np.where(np.isnan(R['Z']), 1.0, sh)
    # darken depth edges so overlaps show
    Z = np.nan_to_num(R['Z'], nan=-999); e = (np.abs(np.diff(Z, axis=0, prepend=Z[:1])) > 4) | (np.abs(np.diff(Z, axis=1, prepend=Z[:, :1])) > 4); img[e] = 0
    tiles.append(Image.fromarray((img * 255).astype(np.uint8))); print(n, round(time.time() - t0, 1), flush=True)
w, hh = tiles[0].size; cols = 6; rows = (len(tiles) + cols - 1) // cols; S = Image.new('L', (cols * w, rows * hh), 255)
for i, t in enumerate(tiles): S.paste(t, ((i % cols) * w, (i // cols) * hh))
S.save('/tmp/hs/preview.png')
