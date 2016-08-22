import urllib.request, json, BTEdb, re, time
db = BTEdb.Database("/dev/shm/lainchan-scraper.json")
# Do not save a backup to revert the transaction from
db.BeginTransaction(False)
# This is displayed directly on the page.
status = open("/dev/shm/lainchan-scraper-status", "w")
status.write("Update in progress")
status.close()
# Add more boards as needed
boards = ['lam', "tech"]
# This regex attempts to find IPFS hashes. Right now it just looks for 46 letter long words. There's a better way because they all start with the same two character string but I will add that in a later update
regex = re.compile(r"\b[A-Za-z0-9]{46}\b")
# Clear last scrape's results
if db.TableExists("table"):
    db.Truncate("table")
else:
    db.CreateTable("table")
for board in boards: # From here it's pretty straightforward
    threads = json.loads(urllib.request.urlopen("https://lainchan.org/"+board+"/threads.json").read().decode("utf-8"))
    for page in threads:
        for thread in page["threads"]:
            print(thread["no"])
            time.sleep(5) # Sleep 5 seconds between thread requests, as a courtesy and to not overload the site.
            for post in json.loads(urllib.request.urlopen("https://lainchan.org/" + board + "/res/" + str(thread["no"]) + ".json").read().decode("utf-8"))["posts"]:
                if "com" in post: # com is the html text of the post
                    result = re.search(regex, post["com"])
                    if result:
                        i = 0 # From here down is a hack to actually get the matching text (the id) out of the regex results so we can actually generate URLs and print it to the site
                        while True:
                            try:
                                db.Insert("table", board = board, match = result.group(i), parent_thread_id = thread["no"], time = post["time"], text = post["com"], post = post["no"])
                                print(post["com"])
                            except:
                                break
                            i+= 1
# Clean up
db.CommitTransaction()
db.Destroy()
import time
status = open("/dev/shm/lainchan-scraper-status", "w")
# The line below looks complicated but it's not.
# Last scrape at (current time). Next scrape at (next hour after the current time)
# We take the current time and modulo it 3600 to get the seconds since the last hour. We then take 3600 - that value to get the seconds until the next hour. We add the result of that to the current time to get the time of the next "o'clock" hour
status.write("Last scrape at <span class=\"date\">" + str(int(time.time())) + "</span><br /> Next scrape at <span class=\"date\">" + str(3600 - (int(time.time()) % 3600) + int(time.time())) + "</span>")
status.close()
