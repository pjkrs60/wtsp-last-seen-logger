from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from selenium import webdriver
from winsound import Beep
from requests import post
from time import sleep

def main():
    global driver, beep_count, beep_count_online, beep_count_start, online_time

    # Opening whatsapp web chat
    # driver = webdriver.Firefox() # Profile saving not coded for firefox yet
    
    options = webdriver.ChromeOptions()
    options.add_argument(chrome_user_data_path)
    options.add_argument('log-level=3')
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(690,250) # minimizes window size
    driver.get("https://web.whatsapp.com/")
    WebDriverWait(driver, login_timeout).until(EC.element_to_be_clickable((By.XPATH, \
'/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]'))).send_keys(contact)
    sleep(2) # wait for contact to appear
    driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[1]/div/label\
/div/div[2]').send_keys(Keys.RETURN)

    current_time = str(datetime.now())
    backup_log(current_time)
    print("Started at:", current_time[:19])
    c, _c = 0, 0
    cls_cnt, beep_count, beep_count_online, beep_count_start = 0, 0, 0, 0
    
    while True: # time offset in current time is to remove wait time for online status to appear/disappear
        current_time = str(datetime.now())
        if ">online</span>" in driver.page_source:
            if not bool(c):
                online_time = datetime.now() - timedelta(seconds = 3)
                current_time = str(online_time)
                log_online(current_time)
            c = 1
        else:
            if bool(c):
                offline_time = datetime.now() - timedelta(seconds = 15)
                current_time = str(offline_time)
                timespan = str(offline_time - online_time) # timespan is the time for which target was online
                log_offline(current_time, timespan)
                try: telegram_send(current_time[11:16])
                except: pass
            c = 0
        if current_time[11:13] == "02": cls_cnt = daily_cron(current_time, cls_cnt)
        if 'QdF">Phone not connected</div>' in driver.page_source:
            log_net_online(current_time, 0)
            beep_count += 1
        elif 'F">Computer not' in driver.page_source:
            log_net_online(current_time, 1)
            beep_count += beep_count_raise
            sleep(1)
            try: driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[1]/div[3]/div/span/div/div/div[2]/div[2]/span/span[1]').click()
            except: pass
            sleep(3)
        else:
            beep_count = 0
            if beep_count_online == 0 and beep_count_start != 0:
                timespan = str(datetime.now() - net_offline_time)
                to_write = "\t" + current_time[11:19] + "\t" + timespan[:7]
                print(to_write)
                write_log(to_write + "\n")
                beep_count_online = 1
        _c += 1
        if not bool(_c % 30): driver.find_element_by_xpath("//div[@spellcheck='true']").click()
        sleep(check_interval)
        
def backup_log(current_time): # backs up last log file at every program run
    nam = (("./dat/data_bkup_" + current_time[:19]).replace(":", ";")).replace(' ', '_') + ".txt"
    start_date = "##########\n" + current_time[:10] + "\n"
    try:
        a = open("./dat/data.txt", "r", encoding = "utf8").read()
        with open(nam, "w", encoding = 'utf8') as file: file.write(a)
    except:
        write_log(start_date)

def clear_screen(): # works only in spyder ide (clears ipython console every 24 hrs)
    try:
        from IPython import get_ipython
        get_ipython().magic('clear') # clears console
    except Exception as e:
        print("###\nError: ", e)
        
def daily_cron(current_time, cls_cnt): # to add date to log file once everyday
    if current_time[11:13] == "02" and cls_cnt == 0:
        clear_screen()
        print("# CLEANED")
        to_write = "\n\n##########\n" + current_time[:10] + "\n"
        write_log(to_write)
        print(to_write)
        return 1
    elif current_time[11:13] == "03" and cls_cnt == 1:
        return 0

def log_online(current_time): # logs when target comes online
    to_write = current_time[11:19] + "\t|"
    print(to_write, end = "")
    write_log(to_write)
    
def log_offline(current_time, timespan): # logs when target goes offline
    to_write = "\t" + current_time[11:19] + "\t" + timespan[2:7]
    print(to_write)
    write_log(to_write + "\n")
    
def log_net_online(current_time, beeper):
    global beep_count_online, beep_count_start, net_offline_time
    beep_count_online, beep_count_start = 0, 1
    if beep_count == 0:
        net_offline_time = datetime.now()
        to_write = "### " + current_time[11:19]  + "\t|"
        print(to_write, end = '')
        write_log(to_write)
    if beep_count % beeper_interval == 0:
        if bool(beeper): beep2()
        else: beep()
        
def write_log(msg):
    with open("./dat/data.txt", "a", encoding = "utf8") as file: file.write(msg)
    
def telegram_send(msg): # sends last seen time to user via telegram bot & deletes previous last seen
    telegram_api_url_send = telegram_api_url + "sendMessage?chat_id={}&text={}".format(telegram_chat_id, msg)
    response_send = post(telegram_api_url_send).json()
    
    msg_id = int(response_send['result']['message_id']) - 1
    telegram_api_url_del = telegram_api_url + "deleteMessage?chat_id={}&message_id={}".format(telegram_chat_id, msg_id)
    response = post(telegram_api_url_del)
    response.close()
    for i in range(1,4):
        if response.json() != {"ok":True, "result":True}: # If deletion fails
            telegram_api_url_del = telegram_api_url + "deleteMessage?chat_id={}&message_id={}".format(telegram_chat_id, msg_id - i)
            response = post(telegram_api_url_del)
            response.close()
            sleep(0.5)
        else: break

def beep():
    for i in range(10, 17):
        Beep(i * 150, 300)
        
def beep2():
    for i in range(10, 12):
        Beep(i * 150, 300)
        
def beep3():
    for i in range(3):
        beep()
        sleep(3)
       
if __name__ == "__main__":
    
    contact = "<target_contact_name>" # Contact who's status it to be tracked
    telegram_chat_id = "<your_telegram_chat_id>" # Get chat id using telegram api's getupdates method
    telegram_bot_token = "<telegram_bot_token>" # Provided by Botfather
    
    # Leave following at default unless errors occur
    profile_number = "10" # Chrome profile number to save data in
    login_timeout = 30 # timeout to wait until whatsapp web starts (in seconds)
    beeper_interval = 15 # (in seconds)
    check_interval = 1 # time to wait before each check (in seconds)
    
    try:
        windows_username = getuser()  # get user username
        chrome_user_data_path = r"user-data-dir=C:\Users\{}\AppData\Local\Google\Chrome\User Data\Profile {}".format(windows_username, profile_number)
        telegram_api_url = "https://api.telegram.org/bot{}/".format(telegram_bot_token)
        beeper_interval *= (1 / check_interval)
        beep_count_raise = beeper_interval / 4
    except KeyboardInterrupt:
        try:driver.quit()
        except: pass
    except Exception as e:
        print(e)
        beep3()
