from PIL import Image

SRC = "/Users/jarvis/.hermes/cache/images/img_e604720b9f1b.jpg"
OUT = "/Users/jarvis/projects/kokovideo/storyboard_frames"

im = Image.open(SRC).convert("RGB")
W, H = im.size
xs = [round(i * W / 3) for i in range(4)]
ys = [round(i * H / 3) for i in range(4)]
n = 0
for r in range(3):
    for c in range(3):
        n += 1
        box = (xs[c], ys[r], xs[c + 1], ys[r + 1])
        t = im.crop(box)
        fn = f"{OUT}/frame_{n:02d}_r{r+1}c{c+1}.png"
        t.save(fn)
        print(fn, t.size)
