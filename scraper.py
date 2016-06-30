import urllib.request, json, BTEdb, re, time
db = BTEdb.Database("/dev/shm/lainchan-scraper.json")
db.BeginTransaction(False)
boards = ['lam', "tech"]
regex = re.compile(r"\b[A-Za-z0-9]{46}\b")
if db.TableExists("table"):
    db.Truncate("table")
else:
    db.CreateTable("table")
for board in boards:
    threads = json.loads(urllib.request.urlopen("https://lainchan.org/"+board+"/threads.json").read().decode("utf-8"))
    for page in threads:
        for thread in page["threads"]:
            print(thread["no"])
            time.sleep(5)
            for post in json.loads(urllib.request.urlopen("https://lainchan.org/" + board + "/res/" + str(thread["no"]) + ".json").read().decode("utf-8"))["posts"]:
                if "com" in post:
                    result = re.search(regex, post["com"])
                    if result:
                        i = 0
                        while True:
                            try:
                                db.Insert("table", board = board, match = result.group(i), parent_thread_id = thread["no"], time = post["time"], text = post["com"], post = post["no"])
                                print(post["com"])
                            except:
                                break
                            i+= 1
db.CommitTransaction()
db.Destroy()
