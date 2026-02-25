import asyncio
import time
import requests
from playwright.async_api import async_playwright

# =======================================================
# CONFIGURATION
# =======================================================
TELEGRAM_BOT_TOKEN = "8670308114:AAHs2Qz4DZXHf6i6WuEmAYhJejYcMA7Tyno"
TELEGRAM_CHAT_ID = "5391749883"

MARKS = "65.67"
SET = "1"  # "1" or "2"
CHECK_INTERVAL_MINUTES = 4

URL = "https://rank.gateoverflow.in/mymarks/VisualizeMarks2.php"
# =======================================================

async def fetch_gate_stats():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(URL, timeout=60000)
            await asyncio.sleep(3)
            
            # Fill out the form
            await page.locator("#my-marks").fill(MARKS)
            # Select the correct set using value matching
            await page.locator(f"input[name='my-set'][value='{SET}']").check()
            await asyncio.sleep(2)  # pause for calculations
            
            # Extract page inner text
            text = await page.locator("body").inner_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            stats = {}
            for i, line in enumerate(lines):
                if line == "Normalized Marks":
                    stats["Normalized Marks"] = lines[i-1]
                elif line == "Qualifying Marks":
                    stats["Qualifying Marks"] = lines[i-1]
                elif line == "Expected Score":
                    stats["Expected Score"] = lines[i-1]
                elif line == "Rank in Set":
                    stats["Rank in Set"] = lines[i-1]
                elif line == "Normalized Rank":
                    stats["Normalized Rank"] = lines[i-1]
                elif line == "Rank Estimate":
                    stats["Rank Estimate"] = lines[i-1]
                    
            if not stats:
                return "Could not fetch data properly."
                
            message = (
                f"*GATE 2026 LIVE Rank Predictor*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📝 *Your Details*\n"
                f"🎯 *Raw Marks:* `{MARKS}`\n"
                f"📋 *Paper Set:* `{SET}`\n\n"
                f"✨ *Score Analysis*\n"
                f"📈 *Normalized Marks:* `{stats.get('Normalized Marks', 'N/A')}`\n"
                f"💯 *Expected Score:* `{stats.get('Expected Score', 'N/A')}`\n"
                f"✅ *Qualifying Marks:* `{stats.get('Qualifying Marks', 'N/A')}`\n\n"
                f"🏆 *Rank Prediction*\n"
                f"🥇 *Rank in Set:* `{stats.get('Rank in Set', 'N/A')}`\n"
                f"🌟 *Normalized Rank:* `{stats.get('Normalized Rank', 'N/A')}`\n"
                f"🔥 *Overall Estimate:* *{stats.get('Rank Estimate', 'N/A')}*\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⏱ _Updated: {time.strftime('%I:%M %p')}_"
            )
            return message
        except Exception as e:
            return f"Error fetching stats: {e}"
        finally:
            await browser.close()

def send_telegram_message(text):
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or not TELEGRAM_BOT_TOKEN:
        print("Note: please add your Telegram Bot Token to send real messages.")
        print("MOCK MESSAGE:\n" + text)
        return
        
    if TELEGRAM_CHAT_ID == "YOUR_TELEGRAM_CHAT_ID_HERE" or not TELEGRAM_CHAT_ID:
        print("Note: Telegram Chat ID is not set. Cannot send message.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Message sent successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Failed to send telegram message: {e}")

async def wait_for_chat_id():
    global TELEGRAM_CHAT_ID
    if TELEGRAM_CHAT_ID != "YOUR_TELEGRAM_CHAT_ID_HERE" and TELEGRAM_CHAT_ID != "":
        return
        
    print("\n" + "="*50)
    print("NO CHAT ID FOUND!")
    print("Please open Telegram and send ANY message to your bot right now.")
    print("Waiting for your message...")
    print("="*50 + "\n")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            response = requests.get(url)
            data = response.json()
            if data.get("ok") and data.get("result"):
                for update in data["result"]:
                    if "message" in update and "chat" in update["message"]:
                        chat_id = str(update["message"]["chat"]["id"])
                        TELEGRAM_CHAT_ID = chat_id
                        print(f"✅ Successfully captured your Chat ID: {chat_id}")
                        
                        # Clear updates
                        update_id = update["update_id"]
                        requests.get(url + f"?offset={update_id + 1}")
                        return
        except Exception:
            pass
        await asyncio.sleep(3)

async def main():
    if TELEGRAM_BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN_HERE" and TELEGRAM_CHAT_ID == "YOUR_TELEGRAM_CHAT_ID_HERE":
        await wait_for_chat_id()
        
    print(f"\n✅ Running GATE Rank Bot (GitHub Actions Trigger) at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    
    # Run 14 times with 4 minute sleep = ~56 minutes. 
    # This prevents GitHub from stopping it, while providing continuous updates!
    for i in range(14):
        print(f"\n--- Checking at {time.strftime('%Y-%m-%d %H:%M:%S')} (Run {i+1}/14) ---")
        message = await fetch_gate_stats()
        send_telegram_message(message)
        
        if i < 13:
            print(f"Sleeping for {CHECK_INTERVAL_MINUTES} minutes...")
            await asyncio.sleep(CHECK_INTERVAL_MINUTES * 60)
            
    print("Execution complete! Shutting down until next hourly trigger.")

if __name__ == "__main__":
    asyncio.run(main())
