from selenium import webdriver
import requests
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os



driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com")

load_dotenv()
api = os.getenv("GROQ_API_KEY")

print("Please Scan your QR Code under 40 sec..")
time.sleep(40)
 
chat_name = input("Who's Chat you want to open : ").strip()
time.sleep(10)


# Find the chat and click the chat
try:
    print("chat finding..")
    chat = None
    try:
        chat = driver.find_element(By.XPATH,f"//span[@title='{chat_name}']")
        
    except:
        chat = driver.find_element(By.XPATH,F"//span[@aria-label='{chat_name}']")

    chat.click()
    print("Chat found sucessfully..")

except Exception as e:
    print(f"Eror; {e}")

last_msg_seen = ""


while True :
    # fetch the message from receiver 
    try:
        messages = driver.find_elements(By.CSS_SELECTOR, "div.message-in span.selectable-text")
        if not messages :
            time.sleep(3)
            continue

        last_msg = messages[-1].text.strip()

        # only reply to new message 
        if last_msg != last_msg_seen:
            print(f"New message : {last_msg}")
            last_msg_seen = last_msg

            # Connect message to Groq API
            
            url = "https://api.groq.com/openai/v1/chat/completions"

            headers = {
                "Authorization" : f"Bearer {api}",
                "Content-Type" : "application/json",
            }

            data = {
                "model" : "llama-3.1-8b-instant",
                "messages" :[
                    {
                            "role": "system",
                            "content": (
                                "You are Jarvis, a friendly and intelligent AI who chats casually "
                                "like a human on WhatsApp. Keep replies short, natural, and conversational — "
                                "no robotic tone, no unnecessary details. If the user greets you, greet back warmly. "
                                "If the user asks a question, reply helpfully and politely."
                            )
                        },
                        {"role": "user", "content": last_msg}
                    ],
                    "temperature" : 0.8,

            }
            
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200 :
                result = response.json()
                reply_text = result["choices"][0]["message"]["content"]
            else :
                print("Error",response.status_code, response.text)

            # Reply in the reply box
            try:
                reply_box = driver.find_element(By.CSS_SELECTOR,"div[contenteditable='true'][data-tab='10']")
            except:
                reply_box = driver.find_element(By.CSS_SELECTOR,"div[contenteditable='true']")
        
            reply_box.send_keys(reply_text + Keys.ENTER)

        print("Waiting for new messgage..")
        time.sleep(5)

    except Exception as e:
        print(f"Error; {e}")
    time.sleep(3)



