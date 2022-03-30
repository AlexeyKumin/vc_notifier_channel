import config # file with bot token and other parameters
import requests
from parse_vc import VCNewsParser
import time # for sleep
from sqlighter import SQLighter

# function for send photo - requests api
def send_photo(image_path, image_caption=""):
    data = {"chat_id": config.chat_id, "caption": image_caption}
    url = 'https://api.telegram.org/bot'+ config.bot_token +'/sendPhoto' 
    with open(image_path, "rb") as image_file:
        ret = requests.post(url, data=data, files={"photo": image_file})
    return ret.json()

# connection with database
db = SQLighter(config.db_name)

# parser
parser = VCNewsParser()

count = 0
check_time = config.check_time # sleep time
while(True):
    print(count, "wake up", check_time, "seconds sleep, check for last post")
    count+=1

    if db.table_is_empty():
        last_post = config.initial_post
    else: 
        last_post = db.get_last_post()
    print("last_post is =", last_post)

    parser.set_last_post(last_post)

    # get lasts posts
    new_posts = parser.new_posts()
    if new_posts:
        for post in new_posts:
            info = parser.post_info(post)
            if (info['img_url'] != None and info['img_url'] != ''):
                photo_name = parser.download_image(info['img_url'])
                send_photo(photo_name, info['title'] + "\n\n" + info['description'] + "\n\n" + info['category'] + "\n\n" + info['link'])
                parser.delete_image(photo_name)
            else:
                photo_name = config.vc_logo_photo
                send_photo(photo_name, info['title'] + "\n\n" + info['description'] + "\n\n" + info['category'] + "\n\n" + info['link'])
        db.add_new_post(new_posts[-1])
        print("found new posts, last_post =", last_post)
    else:
        print("there are no new posts")

    print("sleep")
    time.sleep(check_time)
    
# close webdriver
parser.close_all_sessions()