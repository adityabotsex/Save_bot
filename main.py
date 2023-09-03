import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired
from pyrogram.types import Message

import time
import os
import threading

bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "")
ss = os.environ.get("STRING", "")
bot = Client("mybot",api_id=api_id,api_hash=api_hash,bot_token=bot_token)
acc = Client("myacc",api_id=api_id,api_hash=api_hash,session_string=ss)

# download status
def downstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# upload status
def upstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text("**I am a simple save restricted bot**.\n\nSend message link to clone/download here\n Must join:- @Bypass_restricted")

@bot.on_message(filters.command(["bulk"]))
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text("**I am not an advanced bot")

@bot.on_message(filters.command(["batch"]))
async def batch_forward(bot: Client, m: Message):
    if len(m.command) < 2:
        await m.reply_text("Please provide a list of message links to batch forward.")
        return
    
    message_links = m.command[1:]
    for link in message_links[:100]:  # Limit to the first 100 links for batch forwarding
        if "https://t.me/" in link:
            await forward_message(link, m)
        else:
            await m.reply_text(f"Invalid link: {link}")

async def forward_message(link, m):
    datas = link.split("/")
    msgid = int(datas[-1])

    # Check if the link is for a private chat or public chat
    if "https://t.me/c/" in link:
        chatid = int("-100" + datas[-2])
        with acc:
            msg = acc.get_messages(chatid, msgid)

        # Forward the message to the current chat
        await bot.forward_messages(m.chat.id, chatid, msgid)

    else:
        username = datas[-2]
        msg = await bot.get_messages(username, msgid)

        # Forward the message to the current chat
        await bot.forward_messages(m.chat.id, username, msgid)

@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):

    # joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:

        try:
            with acc:
                acc.join_chat(message.text)
            bot.send_message(message.chat.id,"**successfully join the chat**", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            bot.send_message(message.chat.id,"**successfully join the chat**", reply_to_message_id=message.id)
        except InviteHashExpired:
            bot.send_message(message.chat.id,"**link has expired.**", reply_to_message_id=message.id)
    
    # getting message
    elif "https://t.me/" in message.text:

        datas = message.text.split("/")
        msgid = int(datas[-1])

        # private
        if "https://t.me/c/" in message.text:
            chatid = int("-100" + datas[-2])

            with acc:
                msg  = acc.get_messages(chatid,msgid)

                if "text" in str(msg):
                    bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
                    return

                smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
                dosta = threading.Thread(target=lambda:downstatus(f'{message.id}downstatus.txt',smsg),daemon=True)
                dosta.start()
                file = acc.download_media(msg, progress=progress, progress_args=[message,"down"])
                os.remove(f'{message.id}downstatus.txt')

                upsta = threading.Thread(target=lambda:upstatus(f'{message.id}upstatus.txt',smsg),daemon=True)
                upsta.start()

            if "Document" in str(msg):
                try:
                    with acc:
                        thumb = acc.download_media(msg.document.thumbs[0].file_id)
                except:
                    thumb = None
                bot.send_document(message.chat.id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
                if thumb != None:
                    os.remove(thumb)

            elif "Video" in str(msg):
                try:
                    with acc:
                        thumb = acc.download_media(msg.video.thumbs[0].file_id)
                except:
                    thumb = None
                bot.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
                if thumb != None:
                    os.remove(thumb)

            elif "Animation" in str(msg):
                bot.send_animation(message.chat.id, file, reply_to_message_id=message.id)
               
            elif "Sticker" in str(msg):
                bot.send_sticker(message.chat.id, file, reply_to_message_id=message.id)

            elif "Voice" in str(msg):
                bot.send_voice(message.chat.id, file, caption=msg.caption, thumb=thumb, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])

            elif "Audio" in str(msg):
                try:
                    with acc:
                        thumb = acc.download_media(msg.audio.thumbs[0].file_id)
                except:
                    thumb = None
                bot.send_audio(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])   
                if thumb != None:
                    os.remove(thumb)

            elif "Photo" in str(msg):
                bot.send_photo(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id)

            os.remove(file)
            if os.path.exists(f'{message.id}upstatus.txt'):
                os.remove(f'{message.id}upstatus.txt')
            bot.delete_messages(message.chat.id,[smsg.id])

        # public
        else:
            username = datas[-2]
            msg  = bot.get_messages(username,msgid)
    
            if "Document" in str(msg):
                bot.send_document(message.chat.id, msg.document.file_id, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id)

            elif "Video" in str(msg):
                bot.send_video(message.chat.id, msg.video.file_id, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id)
            
            elif "Animation" in str(msg):
                bot.send_animation(message.chat.id, msg.animation.file_id, reply_to_message_id=message.id)

            elif "Sticker" in str(msg):
                bot.send_sticker(message.chat.id, msg.sticker.file_id, reply_to_message_id=message.id)

            elif "Voice" in str(msg):
                bot.send_voice(message.chat.id, msg.voice.file_id, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id)    

            elif "Audio" in str(msg):
                bot.send_audio(message.chat.id, msg.audio.file_id, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id)    

            elif "text" in str(msg):
                bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)

            elif "Photo" in str(msg):
                bot.send_photo(message.chat.id, msg.photo.file_id, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id)

# infinty polling
bot.run()
