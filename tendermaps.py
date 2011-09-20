from PIL import Image, ImageFilter
import os, time

GREY_RANGE = 20
ACCEPTABLE_FILETYPES = sorted(['png', 'jpg', 'jpeg', 'tif', 'gif'])

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


def watch_folder(path, callback, load_on_init=False):
    abs_path = os.path.abspath(path)
    
    conn = pymongo.Connection()
    db = conn.tendermaps
    
    print "Watching for new files of type %s in folder:\n%s\n" % (ACCEPTABLE_FILETYPES, abs_path)
    
    while True:
        file_list = []
        for root, folders, files in os.walk(abs_path):
            for filename in files:
                if filename.split('.')[-1].lower() in ACCEPTABLE_FILETYPES:
                    file_list.append(os.path.join(root, filename))
        
        
        paths = db.paths
        result = paths.find_one({"_id": abs_path})
        
        if result:
            last_file_list = result["files"] 
        elif load_on_init:
            last_file_list = []
        else:
            last_file_list = file_list
        
        new_files = set(file_list) - set(last_file_list)
        
        for path in new_files:
            callback(path)
        
        paths.remove({"_id": abs_path})
        paths.insert({"_id": abs_path, "files": file_list})
        
        time.sleep(3)


if __name__ == '__main__':
    load_scan('/Users/zain/projects/tendermaps/scans/scan.png')
    #watch_folder("scans", load_scan, load_on_init=True)
