from PIL import Image, ImageFilter
from poller import watch_folder

GREY_RANGE = 20

def load_scan(path):
    print "New file: %s" % path
    
    im = Image.open(path).convert("RGBA")
    pix = im.load()
    
    width, height = im.size
    
    hot_pixels = []
    rs = 0
    gs = 0
    bs = 0
    
    for x in range(0, width):
        for y in range(0, height):
            r, g, b, a = pix[x,y]
            if abs(r-g) < GREY_RANGE and abs(r-b) < GREY_RANGE and abs(g-b) < GREY_RANGE:
                pix[x,y] = (0,0,0,0)
            else:
                rs += r
                gs += g
                bs += b
                hot_pixels.append((x,y))
    
    avg = lambda i: i / len(hot_pixels)
    r,g,b = (avg(rs), avg(gs), avg(bs))
    if max(r,g,b) == r: color = (222,50,10,255)
    if max(r,g,b) == g: color = (48,150,74,255)
    if max(r,g,b) == b: color = (15,15,130,255)
    
    for x,y in hot_pixels:
        pix[x,y] = color
    
    im = im.filter(ImageFilter.EDGE_ENHANCE)
    im.save("im.png", "PNG")

if __name__ == '__main__':
    load_scan('/Users/zain/projects/tendermaps/scans/scan.png')
    #watch_folder("scans", load_scan, load_on_init=True)
