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
from sys import stdout

def main():
    global driver, net_error_count, net_error_count_online, net_error_count_start, online_time, current_time, start_count, main_error_count

    # Opening whatsapp web chat
    # driver = webdriver.Firefox() # Profile data folder saving not coded for firefox yet
    if vlog: print('Opening chrome')
    options = webdriver.ChromeOptions()
    options.add_argument('log-level=3')
    options.add_argument(chrome_user_data_path)
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(650,630) # minimizes window size
    
    current_time = str(datetime.now())
    startup_error_count = 0
    while True:
        try:
            if vlog: print('Loading wtsp')
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
        if vlog: print('Contact selection')
        for element in driver.find_elements_by_css_selector('._ccCW.FqYAR.i0jNr'): # WTSP KEEPS CHANGING 1
            if contact in str(element.get_attribute('title')):
                sleep(1)
                for i in range(2):
                    try:
                        element.click()
                        sleep(0.5)
                    except: pass
    except:
        write_log("### " + current_time[:19] + " Contact not found")
        telegram_send("Contact not found", 0)
        from sys import exit; exit()
    try: driver.find_element_by_class_name('_28-cz').click() # clicks the back arrow after searching # WTSP KEEPS CHANGING 2
    except: pass

    c, _c = 0, 0
    current_time = str(datetime.now())
    startup_logging()
    net_error_count, net_error_count_online, net_error_count_start = 0, 0, 0
    
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
        stdout.flush()
        if 'Phone not connected</div>' in driver.page_source:
            log_net_err(current_time)
            if net_error_count > 0:
                net_error_count += 1
                if not bool(net_error_count % 120): telegram_error_notify('NET "not connected" ERROR')
        elif 'Computer not connected</div>' in driver.page_source:
            log_net_err(current_time)
            sleep(1) # Clicking reconnect button on yellow "not connected" popup
            try: driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[1]/div[3]/div/span/div/div/div[2]/div[2]/span/span[1]').click()
            except: pass
            sleep(10)
        else:
            net_error_count = 0
            if net_error_count_online == 0 and net_error_count_start != 0:
                timespan = str(datetime.now() - net_offline_time)
                to_write = "\t|\t" + current_time[11:19] + "\t" + timespan[:7]
                telegram_send('', 2)
                print(to_write)
                write_log(to_write + "\n", 0)
                net_error_count_online = 1
        _c += 1
        main_error_count, startup_error_count = 0, 0
        current_time = str(datetime.now())
        if current_time[11:19] == "00:00:00": daily_cron(current_time); sleep(1)
        # if not bool(_c % 30): driver.find_element_by_xpath("//div[@spellcheck='true']").click()
        try: # to prevent connections from sleeping
            if not bool(_c % 30):
                # print(current_time[17:19], end = ' ')
                driver.find_element_by_xpath('//span[contains(text(),"TODAY")]').click()
        except: pass
        try:
            if open(data_path, encoding = "utf8").read()[-1] == '\n' and current_time[18] == '0':
                stdout.write('\r# ' + current_time[17:19]) # Print time every 10 seconds to give visual feedback that prog running
        except: pass
        stdout.flush()
        sleep(check_interval)

def startup_logging(): # backs up last log file and prints logs of presemt day
    global start_date
    nam = ((_path + "/dat/data_bkup_" + current_time[:19]).replace(":", ";")).replace(' ', '_') + ".txt"
    try:
        precontents = open(data_path, encoding = "utf8").read()
        with open(nam, "w", encoding = 'utf8') as file: file.write(precontents)
        indx = len(precontents) - precontents[::-1].index('##########') - 11
        to_print = precontents[indx:].split('\n')
        if vlog: clear_screen()
        start_date = "Init: " + current_time[:19]
        print(start_date + '\n' + to_print[to_print.index('##########') + 1].strip())
        for line in to_print:
            if '#' not in line and '|' in line:
                print(line.strip())
    except:
        start_date = "##########\n" + current_time[:10] + "\n"
        write_log(start_date)
        if vlog: clear_screen()
        print(start_date)

def log_online(current_time): # logs when target comes online
    to_write = current_time[11:19] + "\t"
    # print(to_write, end = "")
    stdout.write('\r' + to_write)
    write_log(to_write)
    
def log_offline(current_time, timespan): # logs when target goes offline
    to_write = "|\t" + current_time[11:19] + "\t" + timespan[2:7]
    print(to_write)
    write_log(to_write + "\n", 0)
    
def log_net_err(current_time):
    global net_error_count_online, net_error_count_start, net_offline_time, net_error_count
    net_error_count_online, net_error_count_start = 0, 1
    if net_error_count == 0:
        net_error_count = 1
        net_offline_time = datetime.now()
        to_write = "### " + current_time[11:19]
        write_log(to_write)
        # print(to_write, end = '')
        stdout.write('\r' + to_write)
        stdout.flush()

def write_log(msg, newline = 1):
    if newline:
        if open(data_path, encoding = "utf8").read()[-1] == '\n': pass
        else: msg = '\n' + msg
    with open(data_path, "a", encoding = "utf8") as file: file.write(str(msg))
    # with open(data_dir2, "a", encoding = "utf8") as file: file.write(str(msg))
    stdout.flush()

def clear_screen():
    call('clear' if os_name =='posix' else 'cls')
    
def daily_cron(current_time): # to add date to log file once everyday
    clear_screen()
    to_write = "##########\n" + current_time[:10] + "\n"
    write_log('\n\n' + to_write)
    print(start_date + '\n' + to_write)

def telegram_error_notify(err):
    global old_error
    if err[:15] == old_error[:15]:
        telegram_send(err, 1)
    else:
        telegram_send(err, 0)
    old_error = err

def telegram_send(msg, _del): # sends last seen time to user via telegram bot & deletes previous last seen
    global msg_id
    if _del < 2:
        telegram_api_url_send = telegram_api_url + "sendMessage?chat_id={}&text={}".format(telegram_chat_id, str(msg))
        try: response_send = post(telegram_api_url_send).json()
        except: return
    if bool(_del):
        # if _del < 2: msg_id = int(response_send['result']['message_id']) - 1
        if _del < 2: msg_id = int(response_send['result']['message_id']) - 3
        else: msg_id -= 3
        try: telegram_api_url_del = telegram_api_url + "deleteMessage?chat_id={}&message_id={}".format(telegram_chat_id, msg_id)
        except: return
        try: response = post(telegram_api_url_del)
        except: return
        response.close()
        for i in range(1,4):
            if response.json() != {"ok":True, "result":True}: # If deletion fails
                try: telegram_api_url_del = telegram_api_url + "deleteMessage?chat_id={}&message_id={}".format(telegram_chat_id, msg_id - i)
                except: return
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
    login_timeout = 60 # timeout to wait until whatsapp web starts (in seconds)
    check_interval = 1 # time to wait before each check (in seconds)
    _path = "." # folder path where the log file (s) will be written
    vlog = True # initial logging switch

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
        while True:
            telegram_error_notify('Program CRASHED: ' + str(e)[:51], 0)
            sleep(120)
