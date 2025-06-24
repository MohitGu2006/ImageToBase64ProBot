
import telebot
import base64
import os
import io
import time
from datetime import datetime, timedelta
from PIL import Image
from PIL import ExifTags

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = [int(os.getenv("ADMIN_ID", "123456789"))]  # Replace with your real Telegram user ID

# Initialize bot and track start time
bot = telebot.TeleBot(BOT_TOKEN)
start_time = time.time()

def is_admin(user_id):
    """Check if user is admin"""
    return user_id in ADMIN_ID

def get_uptime():
    """Calculate bot uptime"""
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    
    return f"🕒 Bot Uptime: {days} days, {hours} hours, {minutes} minutes"

def get_image_info(image_path):
    """Extract image information"""
    try:
        with Image.open(image_path) as img:
            format_name = img.format
            width, height = img.size
            file_size = os.path.getsize(image_path)
            file_size_kb = round(file_size / 1024, 2)
            
        return {
            'format': format_name,
            'dimensions': f"{width} × {height}",
            'size_kb': file_size_kb
        }
    except Exception as e:
        return None

def image_to_base64(image_path):
    """Convert image to base64"""
    try:
        with open(image_path, 'rb') as image_file:
            base64_string = base64.b64encode(image_file.read()).decode('utf-8')
        return base64_string
    except Exception as e:
        return None

def create_base64_file(base64_string):
    """Create a text file with base64 content using timestamp format"""
    try:
        # Generate filename with timestamp format: Base64_YYYYMMDD_HHMMSS.txt
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Base64_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(base64_string)
        return filename
    except Exception as e:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Welcome message"""
    welcome_text = """
🤖 **Welcome to Professional Image to Base64 Converter Bot!**

📋 **How to use:**
• Send me any image (photo or document)
• I'll convert it to Base64 format
• You'll receive detailed image information
• Download the complete Base64 data as a `.txt` file

✨ **Supported formats:** JPG, PNG, WEBP, GIF, BMP, and more!

🔐 **Features:**
• Extract image metadata (format, dimensions, file size)
• Base64 preview (first 100 characters)
• Downloadable Base64 file with timestamp
• Admin uptime tracking

📤 **Just send an image to get started!**
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['uptime'])
def send_uptime(message):
    """Show bot uptime (admin only)"""
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Access Denied. Admin only.")
        return
    
    uptime_info = get_uptime()
    bot.reply_to(message, uptime_info)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Handle photo messages"""
    try:
        # Get the largest photo size
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        
        # Download the image
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save temporarily
        temp_image_path = f"temp_image_{message.message_id}.jpg"
        with open(temp_image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Process the image
        process_image(message, temp_image_path)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error processing image: {str(e)}")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Handle document messages (images only)"""
    try:
        document = message.document
        
        # Check if it's an image with proper error message
        if not document.mime_type or not document.mime_type.startswith('image/'):
            bot.reply_to(message, "❌ Unsupported file type")
            return
        
        file_info = bot.get_file(document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save temporarily with original extension
        file_extension = document.file_name.split('.')[-1] if '.' in document.file_name else 'jpg'
        temp_image_path = f"temp_image_{message.message_id}.{file_extension}"
        
        with open(temp_image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Process the image
        process_image(message, temp_image_path)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error processing document: {str(e)}")

def process_image(message, image_path):
    """Process image and send response"""
    try:
        # Get image information
        image_info = get_image_info(image_path)
        if not image_info:
            bot.reply_to(message, "❌ Unsupported file type")
            cleanup_file(image_path)
            return

def get_exif_data(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()

        if not exif_data:
            return "📭 No EXIF metadata found."

        result = []
        for tag_id, value in exif_data.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            result.append(f"🔹 {tag}: {value}")

        return "\n".join(result[:10])  # Limit output to 10 entries

    except Exception as e:
        return f"❌ Error extracting EXIF: {str(e)}"


def process_image(message, image_path):
    """Process image and send response"""
    try:
        # Get image information
        image_info = get_image_info(image_path)
        if not image_info:
            bot.reply_to(message, "❌ Unsupported file type")
            cleanup_file(image_path)
            return

        # Get EXIF data
        exif_data = get_exif_data(image_path)

        # Convert to base64
        base64_string = image_to_base64(image_path)
        if not base64_string:
            bot.reply_to(message, "❌ Error converting image to Base64.")
            cleanup_file(image_path)
            return

        # Create base64 preview (first 100 characters)
        base64_preview = base64_string[:100] + "..." if len(base64_string) > 100 else base64_string

        # Create response message with professional formatting
        response_text = f"""
✅ **Image Processed Successfully!**

📷 **Format:** {image_info['format']}
📏 **Resolution:** {image_info['dimensions']} pixels
💾 **File Size:** {image_info['size_kb']} KB
🔐 **Base64 Preview:** `{base64_preview}`

🧾 **EXIF Data (partial):**
{exif_data}

📄 **Complete Base64 data available in file below ⬇️**
        """

        # Create and send base64 file with timestamp format
        base64_filename = create_base64_file(base64_string)
        if base64_filename:
            # Send message with image info
            bot.reply_to(message, response_text, parse_mode='Markdown')

            # Send base64 file
            with open(base64_filename, 'rb') as base64_file:
                bot.send_document(message.chat.id, base64_file,
                                  caption="📄 Complete Base64 data - Professional format")

            # Cleanup base64 file
            cleanup_file(base64_filename)
        else:
            bot.reply_to(message, "❌ Error creating Base64 file.")

        # Cleanup temporary image
        cleanup_file(image_path)

    except Exception as e:
        bot.reply_to(message, f"❌ Error processing image: {str(e)}")
        cleanup_file(image_path)


def cleanup_file(file_path):
    """Safely delete temporary files"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass  # Ignore cleanup errors

@bot.message_handler(commands=['decode'])
def decode_base64_image(message):
    bot.reply_to(message, "📩 Send your Base64 string now.")

@bot.message_handler(func=lambda msg: msg.reply_to_message and 'Send your Base64' in msg.reply_to_message.text)
def handle_base64_decode(message):
    try:
        base64_data = message.text.strip()
        image_data = base64.b64decode(base64_data)
        file_name = f"decoded_{message.message_id}.png"
        with open(file_name, "wb") as f:
            f.write(image_data)
        with open(file_name, "rb") as img:
            bot.send_photo(message.chat.id, img, caption="🖼️ Here’s your decoded image!")
        os.remove(file_name)
    except Exception:
        bot.reply_to(message, "❌ Invalid Base64 string.")

@bot.message_handler(commands=['length'])
def check_length(message):
    bot.reply_to(message, "📩 Send Base64 text to calculate size.")

@bot.message_handler(func=lambda msg: msg.reply_to_message and 'Send Base64 text' in msg.reply_to_message.text)
def base64_length(message):
    length = len(message.text)
    kb = round((length * 3 / 4) / 1024, 2)
    bot.reply_to(message, f"🔢 Length: `{length}` characters\n💾 Approx Size: `{kb} KB`", parse_mode='Markdown')

@bot.message_handler(commands=['menu'])
def show_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔄 Convert Image", "📥 Decode Base64")
    markup.row("📊 Check Base64 Length", "📤 Upload File")
    bot.send_message(message.chat.id, "🔘 Choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Handle all other message types"""
    help_text = """
🤖 **I can only process images!**

📤 **Please send:**
• Photo (directly from camera/gallery)
• Image file as document (JPG, PNG, WEBP, BMP, etc.)

ℹ️ **Commands:**
• `/start` - Show welcome message
• `/uptime` - Show bot uptime (admin only)

📋 **Send an image to convert it to Base64 format!**
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

if __name__ == "__main__":
    print("🚀 Starting Professional Telegram Image to Base64 Bot...")
    print(f"🕒 Bot started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 Admin ID(s): {ADMIN_ID}")
    print("📡 Bot is ready and listening for messages...")
    
    try:
        # Start bot polling
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        print("🛑 Bot stopped.")
