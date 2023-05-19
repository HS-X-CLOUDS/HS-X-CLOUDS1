from os import remove as osremove, path as ospath, mkdir
from sys import prefix
from threading import Thread
from PIL import Image
from telegram.ext import CommandHandler, CallbackQueryHandler

from bot import AS_DOC_USERS, AS_MEDIA_USERS, dispatcher, AS_DOCUMENT, DB_URI, PRE_DICT, LEECH_DICT, \
                PAID_USERS, CAP_DICT, REM_DICT, SUF_DICT, CFONT_DICT
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage, sendPhoto
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper import button_build
from bot.helper.ext_utils.db_handler import DbManger


def getleechinfo(from_user):
    user_id = from_user.id
    name = from_user.full_name
    buttons = button_build.ButtonMaker()
    thumbpath = f"Thumbnails/{user_id}.jpg"
    prefix = PRE_DICT.get(user_id, "Not Exists")
    suffix = SUF_DICT.get(user_id, "Not Exists")
    caption = CAP_DICT.get(user_id, "ɴᴏᴛ ᴇxɪsᴛs")
    dumpid = LEECH_DICT.get(user_id, "Not Exists")
    remname = REM_DICT.get(user_id, "Not Exists")
    cfont = CFONT_DICT.get(user_id, ["Not Exists"])[0]
    if (
        user_id in AS_DOC_USERS
        or user_id not in AS_MEDIA_USERS
        and AS_DOCUMENT
    ):
        ltype = "ᴅᴏᴄᴜᴍᴇɴᴛ"
        buttons.sbutton("ᴍᴇᴅɪᴀ", f"leechset {user_id} med")
    else:
        ltype = "ᴍᴇᴅɪᴀ"
        buttons.sbutton("ᴅᴏᴄᴜᴍᴇɴᴛ", f"leechset {user_id} doc")
        
    uplan = "Paid User" if user_id in PAID_USERS else "Normal User"

    if ospath.exists(thumbpath):
        thumbmsg = "ᴇxɪsᴛs"
        buttons.sbutton("✘ ᴛʜᴜᴍʙɴᴀɪʟ", f"leechset {user_id} thumb")
        buttons.sbutton("👀 ᴛʜᴜᴍʙɴᴀɪʟ", f"leechset {user_id} showthumb")
    else:
        thumbmsg = "ɴᴏᴛ ᴇxɪsᴛs"
    if prefix != "Not Exists":
        buttons.sbutton("✘ ᴘʀᴇɴᴀᴍᴇ", f"leechset {user_id} prename")
    if suffix != "Not Exists":
        buttons.sbutton("✘ sᴜғғɪx", f"leechset {user_id} suffix")
    if caption != "Not Exists": 
        buttons.sbutton("✘ ᴄᴀᴘᴛᴏɪɴ", f"leechset {user_id} cap")
    if dumpid != "Not Exists":
        buttons.sbutton("✘ ᴅᴜᴍᴘ-ɪᴅ", f"leechset {user_id} dump")
    if remname != "Not Exists": 
        buttons.sbutton("✘ ʀᴇᴍɴᴀᴍᴇ", f"leechset {user_id} rem")
    if cfont != "Not Exists": 
        buttons.sbutton("✘ ᴄᴀᴘғᴏɴᴛ", f"leechset {user_id} cfont")

    button = buttons.build_menu(2)

    text = f'''<u>ʟᴇᴇᴄʜ sᴇᴛᴛɪɴɢ ғᴏʀ<a href='tg://user?id={user_id}'>{name}</a></u>
    
‣ ʟᴇᴇᴄʜ-ᴛʏᴘᴇ : <b>{ltype}</b>
‣ ᴄᴜsᴛᴏᴍ-ᴛʜᴜᴍʙɴᴀɪʟ : <b>{thumbmsg}</b>
‣ ᴘʀᴇғɪx : <b>{prefix}</b>
‣ sᴜғғɪx : <b>{suffix}</b>
‣ ᴄᴀᴘᴛɪᴏɴ : <b>{caption}</b>
‣ ᴄᴀᴘғᴏɴᴛ : <b>{cfont}</b>
‣ ʀᴇᴍɴᴀᴍᴇ : <b>{remname}</b>
‣ ᴅᴜᴍᴘ-ɪᴅ : <b>{dumpid}</b>
‣ ᴜsᴇʀ-ᴘʟᴀɴ : <b>{uplan}</b>'''
    return text, button

def editLeechType(message, query):
    msg, button = getleechinfo(query.from_user)
    editMessage(msg, message, button)

def leechSet(update, context):
    msg, button = getleechinfo(update.message.from_user)
    choose_msg = sendMarkup(msg, context.bot, update.message, button)
    Thread(args=(context.bot, update.message, choose_msg)).start()

def setLeechType(update, context):
    query = update.callback_query
    message = query.message
    user_id = query.from_user.id
    data = query.data
    data = data.split()
    if user_id != int(data[1]):
        query.answer(text="ɴᴏᴛ ʏᴏᴜʀs !", show_alert=True)
    elif data[2] == "doc":
        if user_id in AS_MEDIA_USERS:
            AS_MEDIA_USERS.remove(user_id)
        AS_DOC_USERS.add(user_id)
        if DB_URI is not None:
            DbManger().user_doc(user_id)
        query.answer(text="ʏᴏᴜ ғɪʟᴇ ғɪʟᴇ ᴡɪʟʟ ᴅᴇʟɪᴠᴇʀ ᴀs ᴅᴏᴄᴜᴍᴇɴᴛ !", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "med":
        if user_id in AS_DOC_USERS:
            AS_DOC_USERS.remove(user_id)
        AS_MEDIA_USERS.add(user_id)
        if DB_URI is not None:
            DbManger().user_media(user_id)
        query.answer(text="ʏᴏᴜ ғɪʟᴇ ғɪʟᴇ ᴡɪʟʟ ᴅᴇʟɪᴠᴇʀ ᴀs ᴍᴇᴅɪᴀ !", show_alert=True)
        editLeechType(message, query)

    elif data[2] == "thumb":
        path = f"Thumbnails/{user_id}.jpg"
        if ospath.lexists(path):
            osremove(path)
            if DB_URI is not None:
                DbManger().user_rm_thumb(user_id, path)
            query.answer(text="ᴛʜᴜᴍʙɴᴀɪʟ ʀᴇᴍᴏᴠᴇᴅ !", show_alert=True)
            editLeechType(message, query)
        else:
            query.answer(text="ᴏʟɪᴅ sᴇᴛᴛɪɴɢs", show_alert=True)
    elif data[2] == "showthumb":
        path = f"Thumbnails/{user_id}.jpg"
        if ospath.lexists(path):
            msg = f"Thumbnail for: {query.from_user.mention_html()} (<code>{str(user_id)}</code>)"
            delo = sendPhoto(text=msg, bot=context.bot, message=message, photo=open(path, 'rb'))
            Thread(args=(context.bot, update.message, delo)).start()
        else: query.answer(text=" sᴇɴᴅ ɴᴇᴡ sᴇᴛᴛɪɴɢs ᴄᴏᴍᴍᴀɴᴅ")
    elif data[2] == "prename":
        PRE_DICT.pop(user_id)
        if DB_URI: 
            DbManger().user_pre(user_id, '')
        query.answer(text="Your Prename is Successfully Deleted!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "suffix":
        SUF_DICT.pop(user_id)
        if DB_URI: 
            DbManger().user_suf(user_id, '')
        query.answer(text="Your Suffix is Successfully Deleted!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "cap":
        CAP_DICT.pop(user_id)
        if DB_URI:
            DbManger().user_cap(user_id, None)
        query.answer(text="Your Caption is Successfully Deleted!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "rem":
        REM_DICT.pop(user_id)
        if DB_URI:
            DbManger().user_rem(user_id, None)
        query.answer(text="Your Remname is Successfully Deleted!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "dump":
        LEECH_DICT.pop(user_id)
        if DB_URI:
            DbManger().user_dump(user_id, None)
        query.answer(text="Your Dump ID is Successfully Deleted!", show_alert=True)
        editLeechType(message, query)
    elif data[2] == "cfont":
        CFONT_DICT.pop(user_id)
        if DB_URI:
            DbManger().user_cfont(user_id, None)
        query.answer(text="Your CapFont is Successfully Deleted!", show_alert=True)
        editLeechType(message, query)
    else:
        query.answer()
        try:
            query.message.delete()
            query.message.reply_to_message.delete()
        except:
            pass

def setThumb(update, context):
    user_id = update.message.from_user.id
    reply_to = update.message.reply_to_message
    if reply_to is not None and reply_to.photo:
        path = "Thumbnails/"
        if not ospath.isdir(path):
            mkdir(path)
        photo_dir = reply_to.photo[-1].get_file().download()
        des_dir = ospath.join(path, f'{user_id}.jpg')
        Image.open(photo_dir).convert("RGB").save(des_dir, "JPEG")
        osremove(photo_dir)
        if DB_URI is not None:
            DbManger().user_save_thumb(user_id, des_dir)
        msg = f"ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ sᴀᴠᴇᴅ ғᴏʀ {update.message.from_user.mention_html(update.message.from_user.first_name)}."
        sendMessage(msg, context.bot, update.message)
    else:
        sendMessage("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴛᴏ sᴀᴠᴇ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ", context.bot, update.message)

leech_set_handler = CommandHandler(BotCommands.LeechSetCommand, leechSet, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
set_thumbnail_handler = CommandHandler(BotCommands.SetThumbCommand, setThumb, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
but_set_handler = CallbackQueryHandler(setLeechType, pattern="leechset", run_async=True)

dispatcher.add_handler(leech_set_handler)
dispatcher.add_handler(but_set_handler)
dispatcher.add_handler(set_thumbnail_handler)
