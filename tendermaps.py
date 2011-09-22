from PIL import Image, ImageFilter
import json, os


DEBUG = True # prints some extra stuff on each run
IN_FOLDER = os.path.abspath('in/') # location of the scanned images and their descriptions
OUT_FOLDER = os.path.abspath('public_html/scans/') # location where the processed scans will go
LISTFILE = os.path.join(OUT_FOLDER, 'list.json') # stores info from the last time this was run
GREY_SENSITIVITY = 20 # how much channel variance to allow before a pixel is considered colored
WHITE_MIN = 150 # if any channel is greater, the pixel is considered white (outside the border)
ACCEPTABLE_FILETYPES = sorted(['png', 'jpg', 'jpeg', 'tif', 'gif']) # scan filetypes


def get_stored_list(listfile_path):
    """Parse & return the listfile containing a list of maps seen the last time this was run"""
    try:
        with open(listfile_path, 'r') as f:
            filelist = json.loads(f.read())
    except IOError: # file doesn't exist
        filelist = {}
    
    return filelist


def get_current_list(folder):
    """Return a list of images currently within `folder`, zipped with their descriptions"""
    
    def get_description(filename):
        """Returns the contents of <filename>.txt within the same folder as <filename>.png"""
        txt_filename = "%s.txt" % filename.split(".")[0]
        path = os.path.join(folder, txt_filename)
        try:
            with open(path, 'r') as f:
                return f.read()
        except IOError: # file doesn't exist, so create it
            with open(path, 'w') as f:
                f.write("")
            return ""
    
    maps = {}
    for filename in os.listdir(folder):
        filetype = filename.split('.')[-1] if len(filename.split('.')) > 1 else ""
        
        if filetype in ACCEPTABLE_FILETYPES:
            maps[filename] = {
                "description": get_description(filename),
                "last_modified": os.path.getmtime(os.path.join(folder, filename)),
            }
    
    return maps


def difference(filelist1, filelist2):
    """Returns any files in filelist2 that different from filelist1"""
    # normalize the two dicts, mainly to give both dicts unicode keys
    filelist1 = json.loads(json.dumps(filelist1))
    filelist2 = json.loads(json.dumps(filelist2))
    
    diff = []
    for filename, properties in filelist2.items():
        if filename not in filelist1 \
                or filelist1[filename]['description'] != properties['description'] \
                or filelist1[filename]['last_modified'] != properties['last_modified']:
            diff.append(filename)
    
    return diff


def crop_to_border(im):
    width, height = im.size
    pix = im.load()
    
    mid_x = width / 2
    mid_y = height / 2
    
    is_white = lambda r, g, b, a: r > WHITE_MIN or g > WHITE_MIN or b > WHITE_MIN
    
    x = 0
    while x < width:
        p = pix[x, mid_y]
        if not is_white(*p):
            while not is_white(*p):
                x += 1
                p = pix[x, mid_y]
            break
        x += 1
    
    y = 0
    while y < height:
        p = pix[mid_x, y]
        if not is_white(*p):
            while not is_white(*p):
                y += 1
                p = pix[mid_x, y]
            break
        y += 1
    
    left, upper = x, y
    
    x = width - 1
    while x > 0:
        p = pix[x, mid_y]
        if not is_white(*p):
            while not is_white(*p):
                x -= 1
                p = pix[x, mid_y]
            break
        x -= 1
    
    y = height - 1
    while y > 0:
        p = pix[mid_x, y]
        if not is_white(*p):
            while not is_white(*p):
                y -= 1
                p = pix[mid_x, y]
            break
        y -= 1
    
    right, lower = x, y
    
    return im.crop((left, upper, right, lower))


def load_scan(im, sensitivity, filename, save_to):
    """
        Modifies the image scan at `path` to turn all greyscale pixels transparent, then crops the
        image to only include the map, and returns the lat/lon bounds of that map. A pixel is
        considered grayscale when all its color channels are within `sensitivity` of each other.
    """
    pix = im.load()
    
    width, height = im.size
    
    hot_pixels = []
    rs = 0
    gs = 0
    bs = 0
    
    # first pass, turn greyscale pixels transparent, and average the color of the sharpie-drawn part
    for x in range(0, width):
        for y in range(0, height):
            r, g, b, a = pix[x,y]
            if abs(r-g) < sensitivity and abs(r-b) < sensitivity and abs(g-b) < sensitivity:
                pix[x,y] = (0,0,0,0)
            else:
                rs += r
                gs += g
                bs += b
                hot_pixels.append((x,y))
    
    # pick a single color to re-color the drawn part, based on the dominant channel
    avg = lambda i: i / len(hot_pixels) if len(hot_pixels) != 0 else i
    r,g,b = (avg(rs), avg(gs), avg(bs))
    if max(r,g,b) == r: color = (222,50,10,255)
    if max(r,g,b) == g: color = (48,150,74,255)
    if max(r,g,b) == b: color = (15,15,130,255)
    
    # second pass, re-color the drawn part to the one single color (this makes it look smexy)
    for x,y in hot_pixels:
        pix[x,y] = color
    
    # clears out some of the noise around the drawn part, but slightly changes the color
    im = im.filter(ImageFilter.EDGE_ENHANCE)
    
    if not os.path.exists(OUT_FOLDER):
        os.makedirs(OUT_FOLDER)
    
    out_path = os.path.join(save_to, "%s.png" % filename.split('.')[0])
    im.save(out_path, "PNG")


def store_list(filelist, listfile):
    f = open(listfile, 'w')
    f.write(json.dumps(filelist))
    f.close()


if __name__ == '__main__':
    then_files = get_stored_list(LISTFILE)
    if DEBUG: print "> Files: [%s] in %s" % (", ".join(then_files.keys()), LISTFILE)
    now_files = get_current_list(IN_FOLDER)
    if DEBUG: print "> Files: [%s] in %s" % (", ".join(now_files.keys()), IN_FOLDER)
    
    new_files = difference(then_files, now_files)
    if DEBUG: print "> New or changed files: [%s]" % ", ".join(new_files)
    
    if new_files:
        for filename in new_files:
            scan = Image.open(os.path.join(IN_FOLDER, filename)).convert("RGBA")
            print "> Loading %s (%sx%s)." % (filename, scan.size[0], scan.size[1])
            scan = crop_to_border(scan)
            load_scan(scan, GREY_SENSITIVITY, filename, save_to=OUT_FOLDER)
            print "Loaded %s (%sx%s)." % (filename, scan.size[0], scan.size[1])
        store_list(now_files, LISTFILE)
        if DEBUG: print "All done. Bye!\n"
    else:
        if DEBUG: print "Nothing to do. Bye!\n"
