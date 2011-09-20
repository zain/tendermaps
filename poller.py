import pymongo, os, time

ACCEPTABLE_FILETYPES = sorted(['png', 'jpg', 'jpeg', 'tif', 'gif'])

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
