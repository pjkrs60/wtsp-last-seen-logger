from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from os import name as os_name
from selenium import webdriver
from subprocess import call
from getpass import getuser
from requests import post
from time import sleep

def main():
    global driver, net_error_count, net_error_count_online, net_error_count_start, online_time, current_time, start_count, main_error_count, old_error

    # Opening whatsapp web chat
    # driver = webdriver.Firefox() # Profile data folder saving not coded for firefox yet
    
    options = webdriver.ChromeOptions()
    options.add_argument('log-level=3')
    options.add_argument(chrome_user_data_path)
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(690,250) # minimizes window size
    
    current_time = str(datetime.now())
    startup_error_count = 0
    while True:
        try:
            driver.get("https://web.whatsapp.com/")
            WebDriverWait(driver, login_timeout).until(EC.element_to_be_clickable((By.CLASS_NAME, 'selectable-text'))).send_keys(contact)
            break
        except:
            write_log("### " + current_time[:19] + ' NET ERROR' + '\n')
            if not bool(startup_error_count): since_time = current_time[11:16]
            telegram_error_notify('NET FATAL ERROR since ' + since_time)
            startup_error_count += 1
            if startup_error_count < 5: sleep(30)
            else: sleep(150)
            try:
                driver.find_element_by_class_name('selectable-text').send_keys(contact)
                break
            except: pass
            
    sleep(3) # wait for contact to appear
    # from selenium.webdriver.common.keys import Keys
    # driver.find_element_by_class_name('selectable-text').send_keys(Keys.RETURN)
    try:
        for element in driver.find_elements_by_css_selector('._35k-1._1adfa._3-8er'):
            if contact in str(element.get_attribute('title')): element.click(); sleep(0.5)
    except:
        write_log("### " + current_time[:19] + "Contact not found !!!")
        telegram_send("Contact not found !!!", 0)
        from sys import exit; exit()
    driver.find_element_by_class_name('_1QWS8').click()

    c, _c = 0, 0
    current_time = str(datetime.now())
    startup_logging()
    cls_cnt, net_error_count, net_error_count_online, net_error_count_start = 0, 0, 0, 0

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
                offline_time = datetime.now() - timedelta(seconds = 10)
                current_time = str(offline_time)
                timespan = str(offline_time - online_time) # time for which target was online
                log_offline(current_time, timespan)
                try: telegram_send(current_time[11:16], 1)
                except Exception as e: write_log("### " + current_time[11:19] + ' ' + str(e))
            c = 0
        if 'QdF">Phone not connected</div>' in driver.page_source:
            log_net_err(current_time, 0)
        elif 'F">Computer not' in driver.page_source:
            log_net_err(current_time, 1)
            sleep(1) # Clicking reconnect button on yellow "not connected" popup
            try: driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[1]/div[3]/div/span/div/div/div[2]/div[2]/span/span[1]').click()
            except: pass
            sleep(10)
        else:
            net_error_count = 0
            if net_error_count_online == 0 and net_error_count_start != 0:
                timespan = str(datetime.now() - net_offline_time)
                to_write = "\t" + current_time[11:19] + "\t" + timespan[:7]
                # print(to_write)
                write_log(to_write + "\n")
                net_error_count_online = 1
        _c += 1
        main_error_count, old_error, startup_error_count = 0, '', 0
        if current_time[11:13] == "00": cls_cnt = daily_cron(current_time, cls_cnt)
        if not bool(_c % 30): driver.find_element_by_xpath("//div[@spellcheck='true']").click()
        sleep(check_interval)

def startup_logging(): # backs up last log file and prints logs of presemt day
    nam = ((_path + "/dat/data_bkup_" + current_time[:19]).replace(":", ";")).replace(' ', '_') + ".txt"
    try:
        precontents = open(data_path, encoding = "utf8").read()
        with open(nam, "w", encoding = 'utf8') as file: file.write(precontents)
        indx = len(precontents) - precontents[::-1].index('##########') - 12
        to_print = precontents[indx:].split('\n')
        clear_screen()
        print("Init:", current_time[:19], '\n', to_print[to_print.index('##########') + 1].strip())
        for line in to_print:
            if '#' not in line and 'Message' not in line and '|' in line:
                print(line.strip())
    except:
        start_date = "##########\n" + current_time[:10] + "\n\n"
        write_log(start_date)

def log_online(current_time): # logs when target comes online
    to_write = current_time[11:19] + "\t|"
    print(to_write, end = "")
    write_log(to_write)
    
def log_offline(current_time, timespan): # logs when target goes offline
    to_write = "\t" + current_time[11:19] + "\t" + timespan[2:7]
    print(to_write)
    write_log(to_write + "\n")
    
def log_net_err(current_time, beeper):
    global net_error_count_online, net_error_count_start, net_offline_time, net_error_count
    net_error_count_online, net_error_count_start = 0, 1
    if net_error_count == 0:
        net_error_count += 1
        net_offline_time = datetime.now()
        to_write = "### " + current_time[11:19]  + "\t|"
        telegram_error_notify('NET "not connected" ERROR')
        write_log(to_write)
        # print(to_write, end = '')

def write_log(msg):
    with open(data_path, "a", encoding = "utf8") as file: file.write(str(msg))

def clear_screen():
    call('clear' if os_name =='posix' else 'cls')
        
def daily_cron(current_time, cls_cnt): # to add date to log file once everyday
    if current_time[11:13] == "02" and cls_cnt == 0:
        clear_screen()
        to_write = "\n\n##########\n" + current_time[:10] + "\n"
        write_log(to_write)
        print(to_write)
        return 1
    elif current_time[11:13] == "03" and cls_cnt == 1:
        return 0

def telegram_error_notify(err):
    global old_error, err_cnt
    if err[:15] != old_error[:15]:
        telegram_send(err, 0)
    else:
        telegram_send(err, 1)
    old_error = err
    
def telegram_send(msg, _del): # sends last seen time to user via telegram bot & deletes previous last seen
    telegram_api_url_send = telegram_api_url + "sendMessage?chat_id={}&text={}".format(telegram_chat_id, str(msg))
    response_send = post(telegram_api_url_send).json()
    if bool(_del):
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

if __name__ == "__main__":
    contact = "<target_contact_name>" # Contact who's status it to be tracked
    telegram_chat_id = "<your_telegram_chat_id>" # Get chat id using telegram api's getupdates method
    telegram_bot_token = "<telegram_bot_token>" # Provided by Botfather
    
    # Leave following at default unless errors occur
    profile_number = "10" # Chrome profile number to save data in
    login_timeout = 40 # timeout to wait until whatsapp web starts (in seconds)
    check_interval = 1 # time to wait before each check (in seconds)
    _path = "." # folder path where the log file (s) will be written

    try:
        data_path = _path + "/data.txt"
        linux_username, old_error, err_cnt = getuser(), '', 0
        chrome_user_data_path = r"user-data-dir=/home/{}/.config/chromium/Profile {}".format(linux_username, profile_number)
        telegram_api_url = "https://api.telegram.org/bot{}/".format(telegram_bot_token)
        while True:
            try:
                main()
            except Exception as e:
                current_time = str(datetime.now())
                write_log("### " + current_time[11:19] + ' main(): ' + str(e) + '\n')
                main_error_count = 0
                if not bool(main_error_count):
                    try: driver.quit()
                    except: pass
                    main_error_count = 1
                    since_time = current_time[11:16]
                else:
                    while True: # Keeps pinging telegram once every 2 minutes
                        if not bool(main_error_count): 
                            telegram_error_notify('main(): ' + str(e)[:51] + '  since ' + since_time)
                            sleep(120)
    except KeyboardInterrupt:
        try: driver.quit()
        except: pass
    except Exception as e:
        write_log("### " + str(datetime.now())[11:19] + ' Program Crashed: ' + str(e) + '\n')
        telegram_send('Program CRASHED: ' + str(e)[:51], 0)
        sleep(3600)
