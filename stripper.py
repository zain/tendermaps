from poller import watch_folder

def callback(path):
    print "New file: %s" % path

watch_folder("foo", callback, load_on_init=True)
