from PIL import Image, ImageFilter
import json, os


GREY_RANGE = 20
ACCEPTABLE_FILETYPES = sorted(['png', 'jpg', 'jpeg', 'tif', 'gif'])
IN_FOLDER = os.path.abspath('scans/')
OUT_FOLDER = os.path.abspath('out/')
LISTFILE = os.path.join(OUT_FOLDER, 'list.json')


def load_scan(path):
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
    
    filename = os.path.basename(path)
    out_path = os.path.join(OUT_FOLDER, "%s.png" % filename.split('.')[0])
    im.save(out_path, "PNG")


def find_new_files(folder):
    try:
        with open(LISTFILE, 'r') as f:
            last_maps = json.loads(f.read())
    except IOError:
        # file doesn't exist
        last_maps = {}
        with open(LISTFILE, 'w') as f:
            f.write(json.dumps(last_maps))
    
    maps = {}
    for filename in os.listdir(folder):
        if filename.split('.')[1] in ACCEPTABLE_FILETYPES:
            maps[filename] = {
                "bbox": ((0,0),(0,0)),
                "description": get_description(folder, filename),
                "last_modified": os.path.getmtime(os.path.join(folder, filename)),
            }
    
    maps = json.loads(json.dumps(maps))
    new_files = [f for f, props in maps.items() if f not in last_maps or last_maps[f] != props]
    
    if maps != last_maps:
        with open(LISTFILE, 'w') as f:
            f.write(json.dumps(maps))
    
    return new_files


def get_description(folder, filename):
        txt_filename = "%s.txt" % filename.split(".")[0]
        path = os.path.join(folder, txt_filename)
        try:
            with open(path, 'r') as f:
                return f.read()
        except IOError:
            with open(path, 'w') as f:
                f.write("")
            return ""


if __name__ == '__main__':
    new_files = find_new_files(IN_FOLDER)
    
    for filename in new_files:
        print "Processing [%s]... " % filename,
        load_scan(os.path.join(IN_FOLDER, filename))
        print "Done."
