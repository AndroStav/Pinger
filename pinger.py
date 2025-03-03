import asyncio, os, subprocess, telegram, csv, configparser, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, filename="pinger.log", filemode="w", format="%(asctime)s %(levelname)s [%(funcName)s]: %(message)s")

def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    
    if not config.sections():
        logging.error(f"Не вдалося завантажити конфігурацію з файлу: {filename}")
        return None
    
    logging.info("Конфігурація завантажена")
    return config

def read_ip_file():
    ip_list = []
    try:
        with open("ip.csv", "r", encoding="utf-8") as ip_csv:
            reader = csv.reader(ip_csv)
            for row in reader:
                if len(row) == 2:
                    ip = row[0]   # IP-адреса
                    name = row[1] # Опис
                    is_up = 0     # Is up
                    # Додаємо дані в масив
                    ip_list.append([ip, name, is_up])
                else:
                    logging.error(f"Некоректний рядок: {row}")
        logging.info("IP-адреси завантажені")
        return ip_list
    
    except csv.Error as e:
        logging.error(f"Помилка читання CSV файлу: {e}")
        return None
    except FileNotFoundError as e:
        logging.error(f"CSV файл не знайдено: {e}")
        return None
    except Exception as e:
        logging.error(f"Помилка відкривання CSV файлу: {e}")
        return None

def ping(host, is_up):
    if is_up == 0:
        delay = 5
    else:
        delay = 1
    
    if os.name == 'nt':
        command = ['ping', '-n', '1', '-w', str(delay*1000), host]
    else:
        command = ['ping', '-c', '1', '-w', str(delay), host]
    
    try:
        r = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return r
    except Exception as e:
        logging.error(f"Помилка пінгу: {e}")
        return None

async def sendmess(bot, CHAT_ID, THREAD_ID, message):
    while True:
        try:
            await bot.send_message(chat_id=CHAT_ID, message_thread_id=THREAD_ID, text=message, read_timeout=60, write_timeout=60, connect_timeout=60)
            logging.info("Повідомлення відправлено")
            return
        
        except telegram.error.TelegramError as e:
            logging.error(f"Помилка телеграму: {e}")
            await asyncio.sleep(DELAY_ERROR)

        except asyncio.CancelledError as e:
            logging.error(f"Помилка CancelledError: {e}")
            await asyncio.sleep(DELAY_ERROR)

        except Exception as e:
            logging.error(f"Помилка: {e}")
            await asyncio.sleep(DELAY_ERROR)

def current_time():
    return datetime.now().strftime('%H:%M:%S')

async def pinger(ip, name, is_up, bot, CHAT_ID, THREAD_ID):
    logging.debug(f"Запуск пінгера для {name} ({ip})")
    
    while True:
        try:
            time = current_time()
            response = ping(ip, is_up)
        
            if response == 0:
                if is_up == 1:
                    logging.info(f"{name} піднявся! ({ip})")
                    await sendmess(bot, CHAT_ID, THREAD_ID, f"✅ {name} {time} піднявся! \n({ip})")
                    is_up = 0
            elif response == 1:
                if is_up == 0:
                    logging.info(f"{name} впав! ({ip})")
                    await sendmess(bot, CHAT_ID, THREAD_ID, f"🔴 {name} {time} впав! \n({ip})")
                    is_up = 1
                
            await asyncio.sleep(DELAY)
        
        except asyncio.CancelledError as e:
            logging.error(f"Помилка CancelledError: {e}")
            await asyncio.sleep(DELAY_ERROR)
        except Exception as e:
            logging.error(f"Помилка: {e}")
            await asyncio.sleep(DELAY_ERROR)

async def main():
    config = load_config("config.ini")
    if config is None:
        return 1
    
    ip_list = read_ip_file()
    if ip_list == None:
        return 1
    
    global DELAY, DELAY_ERROR
    TGTOKEN = config["General"]["TGTOKEN"]
    CHAT_ID = config["General"]["CHAT_ID"]
    THREAD_ID = config["General"]["THREAD_ID"]
    
    DELAY = int(config["Settings"]["DELAY"])
    DELAY_ERROR = int(config["Settings"]["DELAY_ERROR"])
    
    bot = telegram.Bot(TGTOKEN)
    
    tasks = []
    for i in ip_list:
        tasks.append(asyncio.create_task(pinger(i[0], i[1], i[2], bot, CHAT_ID, THREAD_ID)))
    print("Програму запущено!")
    logging.info("Програму запущено!")
    await asyncio.gather(*tasks)
    
if __name__ == "__main__":
    asyncio.run(main())
