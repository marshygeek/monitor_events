from chrome_devtools import Chrome
from time import time

chr = Chrome(timeout=200)

chr.call_method("Page.navigate", url="https://www.fonbet.com/live")

chr.show_events(time())
