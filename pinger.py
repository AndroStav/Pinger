import asyncio
import os
import subprocess
from datetime import datetime
import telegram
import csv

TGTOKEN = "telegram_bot_token"
CHAT_ID = "chat_id"
THREAD_ID = "thread_id"
bot = telegram.Bot(TGTOKEN)

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
                    print(f"Некоректний рядок: {row}")
        return ip_list
    
    except csv.Error as e:
        print(f"Помилка читання CSV файлу!\n{e}")
        return None
    except FileNotFoundError as e:
        print(f"Файл не знайдено!\n{e}")
        return None
    except Exception as e:
        print(f"Помилка відкривання файлу!\n{e}")
        return None

def ping(host):
    if os.name == 'nt':
        command = ['ping', '-n', '1', '-w', '1000', host]
    else:
        command = ['ping', '-c', '1', '-w', '1', host]
    
    try:
        r = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return r
    except Exception as e:
        print(f"Помилка пінгу!\n{e}")
        return None

async def sendmess(message):
    while True:
        try:
            await bot.send_message(chat_id=CHAT_ID, message_thread_id=THREAD_ID, text=message, read_timeout=60, write_timeout=60, connect_timeout=60)
            return
        
        except telegram.error.TelegramError as e:
            print(f"Помилка телеграму!\n{e}")
            await asyncio.sleep(15)

        except asyncio.CancelledError as e:
            print(f"Помилка CancelledError!\n{e}")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"Помилка!\n{e}")
            await asyncio.sleep(15)

def current_time():
    return datetime.now().strftime('%H:%M:%S')

async def main():
    ip_list = read_ip_file()
    if ip_list == None:
        return 1
    
    while True:
        try:
            for i in ip_list:
                response = ping(i[0])
        
                if response == 0:
                    if i[2] == 1:
                        await sendmess(f"✅ {i[1]} {current_time()} піднявся! \n({i[0]})")
                        i[2] = 0
                else:
                    if i[2] == 0:
                        await sendmess(f"🔴 {i[1]} {current_time()} впав! \n({i[0]})")
                        i[2] = 1
                
            await asyncio.sleep(5)
        
        except asyncio.CancelledError as e:
            print(f"Виникла помилка CancelledError: {e}")
            await asyncio.sleep(15)
        except Exception as e:
            print(f"Виникла помилка: {e}")
            await asyncio.sleep(15)
    
if __name__ == "__main__":
    asyncio.run(main())
