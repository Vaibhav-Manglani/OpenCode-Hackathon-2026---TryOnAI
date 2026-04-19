# VirtualTryOn Telegram Bot

AI-powered Telegram bot that:

* Puts jewellery/clothing on a model
* Redesigns jewellery into multiple variations
* Generates premium social media creatives

Built using **Python + Telegram Bot API + Replicate (Flux models)**

---

## Features

### 1. 📸 Put it on a model

Upload one or more product images → get a photorealistic model wearing them.

### 2. ✏️ Redesign jewellery

Upload one image → get 4 redesigned variations (A, B, C, D).

### 3. 📱 Social media creatives

Upload one image → generate:

* Instagram post (1:1)
* Story (9:16)
* Facebook banner (1.91:1)

- Auto caption

---

## Setup

### 1. Clone repo

```bash
git clone Vaibhav-Manglani/OpenCode-Hackathon-2026---TryOnAI
cd Vaibhav-Manglani/OpenCode-Hackathon-2026---TryOnAI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env`

```env
TELEGRAM_BOT_KEY=your_telegram_bot_token
REPLICATE_API_TOKEN=your_replicate_api_key
```

Get bot token from Telegram via BotFather.

---

## Run the bot

```bash
python app.py
```

You should see:

```
Bot running...
```

---

## How to use

1. Open your bot in Telegram
2. Type `/start`
3. Choose a mode:

   * Try-on
   * Redesign
   * Social
4. Select sub-category
5. Upload image(s)
6. Click **Generate**

---

## Project Structure

```
.
├── app.py          # Telegram bot logic (UI + flow)
├── main.py         # Image generation (Replicate)
├── prompt.json     # Prompt templates
├── requirements.txt
├── .env
└── uploads/        # Temp image storage
```

---

## Notes

* Try-on supports **multiple images → single output**
* Redesign & Social accept **only 1 image**
* Outputs are auto-cleaned after processing
* Handles async + timeout-safe Telegram requests

---

## Future Improvements

* Auto jewellery detection (type, metal, style)
* Better caption generation (LLM-based)
* Web UI version
* Batch processing
