import logging
import os
import uuid
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

# ----------------- HÀM HỖ TRỢ -----------------
def format_money(value):
    if value == int(value):
        return f"{int(value):,} VND"
    else:
        return f"{value:,.2f} VND"

def draw_centered_text(draw, image_width, y, text, font, fill):
    """Vẽ text căn giữa theo chiều ngang, tại độ cao y"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (image_width - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill)

def create_image_with_texts(
    sotienchuyen,
    thoigianchuyen,
    tennguoinhan,
    stk,
    noidungchuyen,
    y_money=670,
    y_time=810,
    y_name=1050,
    y_stk=1250,
    y_noidung=1310
):
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)

    image = Image.open("mb.png")
    draw = ImageDraw.Draw(image)
    image_width, _ = image.size

    # Font
    font_path = "font/sotien.otf"
    averta_font_path = "font/sotien.otf"

    font_money = ImageFont.truetype(font_path, 97)
    font_time = ImageFont.truetype(font_path, 44)
    font_name = ImageFont.truetype(font_path, 70)
    font_stk = ImageFont.truetype(averta_font_path, 40)
    font_ndck = ImageFont.truetype(averta_font_path, 40)

    # Màu chữ
    color_money = (33, 33, 200)
    color_time = (128, 128, 128)
    color_name = (37, 45, 66)
    color_content = (37, 45, 66)

    # Vẽ các dòng chữ
    draw_centered_text(draw, image_width, y_money, format_money(sotienchuyen), font_money, color_money)
    draw_centered_text(draw, image_width, y_time, thoigianchuyen, font_time, color_time)
    draw_centered_text(draw, image_width, y_name, tennguoinhan, font_name, color_name)
    draw_centered_text(draw, image_width, y_stk, stk, font_stk, color_content)
    draw_centered_text(draw, image_width, y_noidung, noidungchuyen, font_ndck, color_content)

    # Lưu ảnh
    random_filename = f"{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_dir, random_filename)
    image.save(output_path)
    return output_path

# ----------------- COMMAND HANDLER -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xin chào! Đây là bot Fake Bill.\n"
        "📌 Bạn có thể dùng lệnh /help để xem hướng dẫn."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Hướng dẫn sử dụng bot Fake Bill MBBANK:\n\n"
        "/start – Giới thiệu bot\n"
        "/help – Hiển thị danh sách lệnh\n"
        "/mb <số tiền> | <giờ:phút> | <tên người nhận> | <STK> | <nội dung chuyển khoản>\n\n"
        "Ví dụ:\n"
        "/mb 500000 | 14:20 | NGUYEN VAN A | 123456789 | Thanh toan tien dien"
    )

async def mb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_text = " ".join(context.args)
    parts = full_text.split("|")

    if len(parts) != 5:
        await update.message.reply_text(
            "❌ Sai cú pháp.\n"
            "✅ Đúng: /mb <số tiền> | <giờ:phút> | <tên người nhận> | <STK> | <nội dung chuyển khoản>\n"
            "Ví dụ:\n/mb 500000 | 14:20 | NGUYEN VAN A | 780380 | Thanh toan tien dien"
        )
        return

    try:
        sotienchuyen = float(parts[0].strip().replace(',', ''))
        gio_phut = parts[1].strip()
        tennguoinhan = parts[2].strip()
        stk = parts[3].strip()
        noidungchuyen = parts[4].strip()
    except Exception as e:
        await update.message.reply_text(f"Lỗi xử lý tham số: {e}")
        return

    ngay_hom_nay = datetime.now().strftime("%d/%m/%Y")
    thoigianchuyen = f"{gio_phut} - {ngay_hom_nay}"

    try:
        image_path = create_image_with_texts(
            sotienchuyen,
            thoigianchuyen,
            tennguoinhan,
            stk,
            noidungchuyen
        )
    except Exception as e:
        await update.message.reply_text(f"Lỗi khi tạo ảnh: {e}")
        return

    with open(image_path, "rb") as photo:
        await update.message.reply_photo(photo)

# ----------------- MAIN -----------------
def main():
    TOKEN = "7777600879:AAGdYxyPuWNPS3WQl9U1WN4e2nzRLxhM3Gk"  # Token bot của bạn

    application = ApplicationBuilder().token(TOKEN).build()

    # Đăng ký các lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("mb", mb_command))

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    print("Bot đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    main()
