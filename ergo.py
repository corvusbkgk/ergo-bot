#!/usr/bin/python
# -*- coding: utf-8 -*-

import discord
import json
import os

client = discord.Client()
Users = {}
Channels = {}

TOKEN = os.environ['token'] # The token is also substituted for security reasons

def _get_server():
    return client.get_server("557978932687667201")
    
def _get_channel(name):
    for c in _get_server().channels:
        if c.name == name:
            return c
    print("Channel #"+name+" not found")
    
async def get_message_history(cid):
    log = ""
    async for old_msg in client.logs_from(client.get_channel(cid), 25):
        if old_msg.content == "!clear":
            break
        else:
            log = old_msg.content + "\n" + log
    return log

async def lookup_user(id):
#    logs = yield from client.logs_from(_get_channel("whoiswho"))
#    for message in logs:
    if id in Users:
        return Users[id]
    return None

async def delete_user(id):
#    logs = yield from client.logs_from(_get_channel("whoiswho"))
    async for user in client.logs_from(_get_channel("whoiswho")):
        uinfo = json.loads(user.content)
        if uinfo["id"] == id:
            await client.delete_message(user)
            del Users[id]
            return uinfo
    return None
    
async def add_user(id, nickname, channel, connected):
    uinfo = {"id":id,"nickname":nickname,"channel":channel,"connected":connected}
    await client.send_message(_get_channel("whoiswho"), json.dumps(uinfo))
    Users[id] = uinfo
    
async def broadcast(channel_id, message, exclude):
    async for user in client.logs_from(_get_channel("whoiswho")):
        uinfo = json.loads(user.content)
        if uinfo["channel"] == channel_id and uinfo["id"] != exclude and uinfo["connected"] == "TRUE":
            user_ref = await client.get_user_info(uinfo["id"])
            await client.send_message(user_ref, message)
    
    
async def command_process(message):
    if message.content == "!hookmeup":
        await delete_user(message.author.id)
        await add_user(message.author.id, "Anonymous", "560194340870291466", "FALSE")
        await client.send_message(message.channel, "Добро пожаловать в прекрасный мир анонимности!\n\nErgo Proxy - режим инкогнито для всего земного шара! Помните, что ложное чувство безопасности приведет к большей беде, чем если бы вы сидели голым задом в муравейнике. Паранойя это нормально в наше время (к сожалению). Проверяйте стены на жучки, компьютеры на вирусы, не смотрите порно с животными в рабочей сети и, боже упаси, не пользуйтесь роутерами от Huawei - они так и не закрыли ту дыру, что мы нашли два года назад.\n\nМы никак не можем вас остановить, но пожалуйста не используйте наше творение во зло людям, не организовывайте тут убийств и торговли органами.\n\nИначе вам пиздец.\n\nИскренне ваши, Digital Revolt: Arch, Gaya, Gpia, Lanz, S@turn, T0lk (RIP :frowning2:).\nCopyleft DR 2022-2025 and counting")
    elif message.content == "!help":
        await client.send_message(message.channel, "Добро пожаловать в прекрасный мир анонимности! \nErgo Proxy - режим инкогнито для всего земного шара!\n\n!help - вот эта вот пурга\n!hookmeup - зарегистрироваться как пользователь даркнета\n!nick _Nickname_ - изменить свой ник\n!connect - подключиться\n!disconnect - отключиться\n!status - проверить свои настройки\n!here - посмотреть кто есть в канале\n!clear - очистить историю для новых пользователей\n!channel-list - список каналов\n!channel-switch - перейти на другой канал")
        if (message.author.id == "181707141231411200") or (message.author.id == "558014190829174809"):
            await client.send_message(message.channel, "Привилегированные команды:\n!channel-register - добавить *существующий* паблик канал\n!shutdown - вырубить к херам")
    elif not message.author.id in Users:
        await client.send_message(message.channel, "Вы не зарегистрированы, используйте **!help** чтобы узнать как это сделать")
    elif message.content.startswith("!nick"):
        uinfo = await delete_user(message.author.id)
        await add_user(message.author.id, message.content[6:], uinfo["channel"], uinfo["connected"])
        await client.send_message(message.channel, "Ник изменен на **"+message.content[6:]+"**")
    elif message.content == "!connect":
        uinfo = await lookup_user(message.author.id)
        if uinfo["connected"] == "FALSE":
            await delete_user(message.author.id)
            await add_user(message.author.id, uinfo["nickname"], uinfo["channel"], "TRUE")
            log = await get_message_history(uinfo["channel"])
            log = log + "\n *Подключен к " + client.get_channel(uinfo["channel"]).name + "*"
            await client.send_message(message.channel, log)
        else:
            await client.send_message(message.channel, "*Вы все еще подключены к " + client.get_channel(uinfo["channel"]).name + "*")
    elif message.content == "!status":
        uinfo = await lookup_user(message.author.id)
        if uinfo == None:
            await client.send_message("Вы не зарегистрированы")
        else:
            msg = "**Ник:** "+uinfo["nickname"] + "\n"
            msg = msg + "**Канал:** " + client.get_channel(uinfo["channel"]).name + "\n"
            if uinfo["connected"] == "TRUE":
                msg = msg + "**Подключено**"
            else:
                msg = msg + "**Не подключено**"
            await client.send_message(message.channel, msg)
    elif message.content == "!shutdown":
        if (message.author.id == "181707141231411200") or (message.author.id == "558014190829174809"):
            print("Shutting down...")
            await client.close()
        else:
            await client.send_message(message.channel, "Недостаточно прав, ковбой")
    elif message.content.startswith("!channel-register"):
        if (message.author.id == "181707141231411200") or (message.author.id == "558014190829174809"):
            chan = _get_channel(message.content[18:])
            if chan == None:
                await client.send_message(message.channel, "Канал **" + message.content[18:] + "** не найден")
            elif chan.id in Channels:
                await client.send_message(message.channel, "Канал **" + message.content[18:] + "** уже зарегистрирован")
            else:
                cinfo = {"id":chan.id, "name":chan.name, "access":"public"}
                msg = json.dumps(cinfo)
                Channels[chan.id] = cinfo
                await client.send_message(_get_channel("darknet-map"), msg)
                await client.send_message(message.channel, "Канал **" + message.content[18:] + "** успешно добавлен")
        else:
            await client.send_message(message.channel, "Недостаточно прав, ковбой")
    elif message.content == "!channel-list":
        clist = []
        for cid in Channels:
            if Channels[cid]["access"] == "public":
                topic = client.get_channel(cid).topic
                if topic == None:
                    topic = "*Пурга какая-то (канал без описания)*"
                clist.append("**"+Channels[cid]["name"]+"** - "+topic+"\n")
        clist.sort()
        msg = "**Доступные каналы:**\n"
        for cname in clist:
            msg = msg + cname
        await client.send_message(message.channel, msg)
    elif message.content.startswith("!channel-switch"):
        cname = message.content[16:]
        for cid in Channels:
            if (Channels[cid]["name"] == cname) and (Channels[cid]["access"] == "public"):
                if cid == Users[message.author.id]["channel"]:
                    await client.send_message(message.channel, "*А вы собственно уже на канале " + client.get_channel(cid).name + "*")
                    return
                uinfo = await delete_user(message.author.id)
                await add_user(message.author.id, uinfo["nickname"], Channels[cid]["id"], uinfo["connected"])
                uinfo = Users[message.author.id]
                if uinfo["connected"] == "TRUE":
                    log = await get_message_history(uinfo["channel"])
                    log = log + "\n *Подключен к " + client.get_channel(uinfo["channel"]).name + "*"
                else:
                    log = "*Переключение на " + client.get_channel(uinfo["channel"]).name + " прошло успешно*"
                await client.send_message(message.channel, log)
                return
        await client.send_message(message.channel, "Канал **" + cname + "** не найден")       
    elif Users[message.author.id]["connected"] == "FALSE":
        await client.send_message(message.channel, "Вы отключены от каналов, используйте **!connect** чтобы подключиться к " + client.get_channel(Users[message.author.id]["channel"]).name)
    elif message.content == "!disconnect":
        uinfo = await delete_user(message.author.id)
        await add_user(message.author.id, uinfo["nickname"], uinfo["channel"], "FALSE")
        await client.send_message(message.channel, "*Отключен от " + client.get_channel(uinfo["channel"]).name + "*")
    elif message.content == "!here":
        ulist = []
        uinfo = Users[message.author.id]
        for uid in Users:
            if Users[uid]["channel"] == uinfo["channel"]:
                ulist.append(Users[uid]["nickname"])
        ulist.sort()
        msg = "**Users in channel** " + client.get_channel(uinfo["channel"]).name + ": "
        for uname in ulist:
            msg = msg + "\n" + uname
        await client.send_message(message.channel, msg)
    elif message.content == "!clear":
        uinfo = Users[message.author.id]
        await client.send_message(client.get_channel(uinfo["channel"]), "!clear")
        await client.send_message(message.channel, "История канала " + client.get_channel(uinfo["channel"]).name + " очищена")

@client.event
async def on_ready():
    print("The bot is ready!")
    await client.change_presence(game=discord.Game(name="Darknet monitor"))
    async for user in client.logs_from(_get_channel("whoiswho")):
        uinfo = json.loads(user.content)
        Users[uinfo["id"]] = uinfo
    async for channel in client.logs_from(_get_channel("darknet-map")):
        cinfo = json.loads(channel.content)
        Channels[cinfo["id"]] = cinfo

@client.event
async def on_message(message):
    if message.author == client.user:
        return
#   if message.content == "Hello":
#       await client.send_message(message.channel, "World")
#   if message.content == "!proxy":
#        role = message.server.get(message.server.roles, name='Darknet')
#        await client.add_roles(message.author, role)
#   if not message.channel.is_private:
#       uinfo = await lookup_user(message.author.id)
#       if uinfo == None:
#           await add_user(message.author.id, "Anonymous", "560012502037954562")
#           uinfo = await lookup_user(message.author.id)
#       await client.send_message(client.get_channel(uinfo["channel"]), "**"+uinfo["nickname"]+":** "+message.content)
#       await broadcast(uinfo["channel"], "**"+uinfo["nickname"]+":** "+message.content, uinfo["id"])
#       await client.delete_message(message)
    if message.channel.is_private:
        if message.content.startswith("!"):
            await command_process(message)
        else:
            uinfo = await lookup_user(message.author.id)
            if uinfo == None:
                await client.send_message(message.channel, "Вы не зарегистрированы, используйте **!help**, чтобы узнать как все работает. (Пссст: **!hookmeup**)")
            elif uinfo["connected"] == "FALSE":
                await client.send_message(message.channel, "Вы не подключены, используйте **!help**, чтобы узнать какие есть команды или **!connect** чтобы подключиться")
            else:
                await client.send_message(client.get_channel(uinfo["channel"]), "**"+uinfo["nickname"]+":** "+message.content)
                await broadcast(uinfo["channel"], "**"+uinfo["nickname"]+":** "+message.content, uinfo["id"])
            
            
client.run(TOKEN)