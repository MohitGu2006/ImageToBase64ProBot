# 🖼️ Image2Base64ProBot

A fast and professional Telegram bot that converts any image to Base64 format with downloadable file support and image metadata extraction.

---

## 🚀 Features

- 🔄 Converts image (photo or document) to Base64
- 📏 Extracts format, resolution, and file size
- 📄 Sends Base64 string as `.txt` file
- 🔐 Admin-only uptime command
- 🧬 Clean Base64 preview in message

---

## 📷 Supported Image Types

- JPG / JPEG
- PNG
- WEBP
- BMP
- GIF
- Others supported by Pillow

---

## ⚙️ Setup & Deployment

### 🔧 Local Setup

```bash
git clone https://github.com/yourusername/ImageToBase64ProBot
cd ImageToBase64ProBot
pip install -r requirements.txt
```

Edit your `main.py`:

```python
BOT_TOKEN = "your_actual_bot_token_here"
```

Then run:

```bash
python main.py
```

---

### 🚀 Deploy to Railway

1. Go to [https://railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub Repo**
3. Select this repository
4. Railway will auto-detect `Procfile`
5. Click **Deploy**

---

## 🔒 Security Tip

**Do not share your BOT_TOKEN publicly.**  
If your repository is public, use environment variables or `.env` file to load the token securely.

---

## 🧠 Future Ideas

- Convert Base64 back to image
- PDF/Image to Base64
- QR code of Base64 output
- Auto-expire file links

---

## 📄 License

This project is licensed under the MIT License. Feel free to fork and improve.

---

## 👨‍💻 Developed by

**Mohit Gupta**  
Telegram: [@YourTelegramHandle]  
GitHub: [github.com/yourusername](https://github.com/yourusername)