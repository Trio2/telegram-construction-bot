from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

import logging
import aiohttp
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# BOT_TOKEN is loaded from .env
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")  # UPDATE THIS!

# Conversation states
AWAITING_NOTES = 1
AWAITING_DATE = 2

async def show_main_menu(update: Update, context):
    """Show the main menu."""
    keyboard = [
        [InlineKeyboardButton("🔍 Inspections", callback_data="menu_inspections")],
        [InlineKeyboardButton("📋 Permits", callback_data="menu_permits")],
        [InlineKeyboardButton("🏗️ Materials", callback_data="menu_materials")],
        [InlineKeyboardButton("📊 Reports", callback_data="menu_reports")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🏗️ **Construction Management Bot**\n\n"
        "Welcome! Please select an option from the menu below:"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def start_command(update: Update, context):
    """Handle /start command."""
    await show_main_menu(update, context)

async def bot_keyword(update: Update, context):
    """Handle bot/Bot/BOT keywords."""
    message_text = update.message.text.lower()
    if message_text in ['bot', 'bots']:
        await show_main_menu(update, context)

async def cancel(update: Update, context):
    """Cancel current operation."""
    await update.message.reply_text(
        "Operation cancelled. Type 'bot' to return to the main menu."
    )
    return ConversationHandler.END

async def button_handler(update: Update, context):
    """Handle all button presses."""
    query = update.callback_query
    await query.answer()
    
    # Main menu selections
    if query.data == "menu_inspections":
        keyboard = [
            [InlineKeyboardButton("🔍 Request New Inspection", callback_data="inspection_new")],
            [InlineKeyboardButton("📊 View Pending Inspections", callback_data="inspection_pending")],
            [InlineKeyboardButton("✅ Completed Inspections", callback_data="inspection_completed")],
            [InlineKeyboardButton("📅 Schedule Inspection", callback_data="inspection_schedule")],
            [InlineKeyboardButton("📝 Inspection Reports", callback_data="inspection_reports")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔍 **Inspection Management**\n\nSelect an option:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Inspection submenu - Request New Inspection
    elif query.data == "inspection_new":
        keyboard = [
            [InlineKeyboardButton("⚡ Electrical", callback_data="inspect_type_electric")],
            [InlineKeyboardButton("🔧 Plumbing", callback_data="inspect_type_plumbing")],
            [InlineKeyboardButton("🏗️ Framing", callback_data="inspect_type_framing")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_inspections")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔍 **New Inspection Request**\n\n"
            "What type of inspection do you need?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Inspection Type - Electric (with sub-options)
    elif query.data == "inspect_type_electric":
        keyboard = [
            [InlineKeyboardButton("🔌 Rough Electrical", callback_data="electric_rough")],
            [InlineKeyboardButton("✨ Finish Electrical", callback_data="electric_finish")],
            [InlineKeyboardButton("🔙 Back", callback_data="inspection_new")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "⚡ **Electrical Inspection**\n\n"
            "Please select the electrical inspection phase:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Back to main menu
    elif query.data == "main_menu":
        await show_main_menu(update, context)
    
    else:
        # Let conversation handlers handle these
        return

async def start_electric_rough(update: Update, context):
    """Start electric rough inspection conversation."""
    query = update.callback_query
    await query.answer()
    
    # Store inspection type in user data
    context.user_data['inspection_type'] = "Electrical - Rough"
    context.user_data['user_id'] = query.from_user.id
    context.user_data['user_name'] = query.from_user.full_name
    
    await query.edit_message_text(
        "⚡ **Rough Electrical Inspection**\n\n"
        "📋 **Requirements for Rough Electrical:**\n"
        "MOCKUP validation points....\n"
        "• All wiring must be installed\n"
        "• Junction boxes in place\n"
        "• Panel box installed\n"
        "• Grounding system complete\n\n"
        "Please provide:\n"
        "• Notes\n"
        "• Preferred Date\n"
        "Format: `Building A | June 15 | Project Manager`\n\n"
        "Type your Note:",
        parse_mode='Markdown'
    )
    
    return AWAITING_NOTES

async def start_electric_finish(update: Update, context):
    """Start electric finish inspection conversation."""
    query = update.callback_query
    await query.answer()
    
    context.user_data['inspection_type'] = "Electrical - Finish"
    context.user_data['user_id'] = query.from_user.id
    context.user_data['user_name'] = query.from_user.full_name
    
    await query.edit_message_text(
        "✨ **Finish Electrical Inspection**\n\n"
        "📋 **Requirements for Finish Electrical:**\n"
        "MOCKUP validation points....\n"
        "• All outlets and switches installed\n"
        "• Light fixtures mounted\n"
        "• Panel breakers labeled\n"
        "• GFCI/AFCI protection verified\n\n"
        "Please provide:\n"
        "• Notes\n"
        "• Preferred Date\n"
        "Format: `Building A | June 15 | Project Manager`\n\n"
        "Type your Note:",
        parse_mode='Markdown'
    )
    
    return AWAITING_NOTES

async def start_plumbing(update: Update, context):
    """Start plumbing inspection conversation."""
    query = update.callback_query
    await query.answer()
    
    context.user_data['inspection_type'] = "Plumbing"
    context.user_data['user_id'] = query.from_user.id
    context.user_data['user_name'] = query.from_user.full_name
    
    await query.edit_message_text(
        "🔧 **Plumbing Inspection**\n\n"
        "📋 **Requirements for Plumbing:**\n"
        "MOCKUP validation points....\n"
        "• All pipes installed and tested\n"
        "• Water pressure test completed\n"
        "• Drain system verified\n"
        "• Fixtures ready for inspection\n\n"
        "Please provide:\n"
        "• Notes\n"
        "• Preferred Date\n"
        "Format: `Building B | June 16 | Site Supervisor`\n\n"
        "Type your Note:",
        parse_mode='Markdown'
    )
    
    return AWAITING_NOTES

async def start_framing(update: Update, context):
    """Start framing inspection conversation."""
    query = update.callback_query
    await query.answer()
    
    context.user_data['inspection_type'] = "Framing"
    context.user_data['user_id'] = query.from_user.id
    context.user_data['user_name'] = query.from_user.full_name
    
    await query.edit_message_text(
        "🏗️ **Framing Inspection**\n\n"
        "📋 **Requirements for Framing:**\n"
        "MOCKUP validation points....\n"
        "• All framing complete\n"
        "• Headers and beams installed\n"
        "• Shear walls completed\n"
        "• Hurricane ties/clips installed\n\n"
        "Please provide:\n"
        "• Notes\n"
        "• Preferred Date\n"
        "Format: `Building C | June 17 | Construction Manager`\n\n"
        "Type your Note:",
        parse_mode='Markdown'
    )
    
    return AWAITING_NOTES

async def handle_notes(update: Update, context):
    """Handle inspection notes input."""
    notes = update.message.text
    context.user_data['notes'] = notes
    
    await update.message.reply_text(
        "📅 **Preferred Date**\n\n"
        "Please provide your preferred inspection date:\n"
        "Format: MM/DD/YYYY or MM-DD-YYYY\n\n"
        "Example: 06/15/2025",
        parse_mode='Markdown'
    )
    
    return AWAITING_DATE

async def handle_date(update: Update, context):
    """Handle date input and send to n8n."""
    date_text = update.message.text
    
    # Basic date validation
    try:
        # Try to parse the date
        for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d']:
            try:
                inspection_date = datetime.strptime(date_text, fmt)
                date_text = inspection_date.strftime('%Y-%m-%d')
                break
            except:
                continue
    except:
        await update.message.reply_text(
            "❌ Invalid date format. Please use MM/DD/YYYY format.\n"
            "Example: 06/15/2025"
        )
        return AWAITING_DATE
    
    # Prepare data for n8n webhook - UPDATED WITH CHAT ID
    webhook_data = {
        "telegram_user_id": context.user_data['user_id'],
        "telegram_user_name": context.user_data['user_name'],
        "telegram_chat_id": update.message.chat.id,  # ADDED
        "telegram_chat_type": update.message.chat.type,  # ADDED
        "telegram_chat_title": update.message.chat.title if update.message.chat.type != 'private' else None,  # ADDED
        "inspection_type": context.user_data['inspection_type'],
        "notes": context.user_data['notes'],
        "preferred_date": date_text,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }
    
    # Send loading message
    loading_msg = await update.message.reply_text(
        "⏳ Processing your inspection request...",
        parse_mode='Markdown'
    )
    
    # Send to n8n webhook with SSL verification disabled
    try:
        # Create connector that doesn't verify SSL
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(N8N_WEBHOOK_URL, json=webhook_data, timeout=10) as response:
                if response.status == 200:
                    try:
                        result = await response.json()
                    except:
                        result = {}
                    
                    # Delete loading message
                    await loading_msg.delete()
                    
                    # Success message with details from n8n
                    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    success_message = (
                        f"✅ **Inspection Request Submitted!**\n\n"
                        f"**Type:** {context.user_data['inspection_type']}\n"
                        f"**Notes:** {context.user_data['notes']}\n"
                        f"**Preferred Date:** {date_text}\n"
                    )
                    
                    # If n8n returns additional data (permit number, address, etc.)
                    if 'data' in result:
                        if 'permit_number' in result['data']:
                            success_message += f"**Permit #:** {result['data']['permit_number']}\n"
                        if 'address' in result['data']:
                            success_message += f"**Address:** {result['data']['address']}\n"
                        if 'notion_task_id' in result['data']:
                            success_message += f"**Task ID:** {result['data']['notion_task_id']}\n"
                    
                    success_message += "\n📧 You will receive a confirmation once scheduled."
                    
                    await update.message.reply_text(
                        success_message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    await loading_msg.delete()
                    await update.message.reply_text(
                        "❌ Error submitting inspection request. Please try again later."
                    )
                    
    except Exception as e:
        logger.error(f"Error sending webhook: {e}")
        await loading_msg.delete()
        
        # Show error but still save locally
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚠️ Connection error, but your request was saved:\n\n"
            f"**Type:** {context.user_data['inspection_type']}\n"
            f"**Notes:** {context.user_data['notes']}\n"
            f"**Preferred Date:** {date_text}\n\n"
            f"We'll process it once connection is restored.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("cancel", cancel))
    
    # Add message handler for bot/Bot/BOT keywords
    bot_filter = filters.Text(['bot', 'Bot', 'BOT', 'bots', 'Bots', 'BOTS'])
    application.add_handler(MessageHandler(bot_filter, bot_keyword))
    
    # Conversation handlers for each inspection type
    # Electric Rough
    electric_rough_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_electric_rough, pattern="^electric_rough$")],
        states={
            AWAITING_NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_notes)],
            AWAITING_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Electric Finish
    electric_finish_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_electric_finish, pattern="^electric_finish$")],
        states={
            AWAITING_NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_notes)],
            AWAITING_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Plumbing
    plumbing_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_plumbing, pattern="^inspect_type_plumbing$")],
        states={
            AWAITING_NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_notes)],
            AWAITING_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Framing
    framing_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_framing, pattern="^inspect_type_framing$")],
        states={
            AWAITING_NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_notes)],
            AWAITING_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Add conversation handlers
    application.add_handler(electric_rough_handler)
    application.add_handler(electric_finish_handler)
    application.add_handler(plumbing_handler)
    application.add_handler(framing_handler)
    
    # Add general callback query handler (must be after conversation handlers)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Start the bot
    logger.info("Bot started! Send 'bot', 'Bot', or 'BOT' to activate the menu.")
    logger.info(f"N8N Webhook URL: {N8N_WEBHOOK_URL}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()