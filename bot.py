import discord
from discord.ext import commands
import asyncio

TOKEN = "MTUzMDIwMDA5NDA3NzYxNjE5OA.G_cV2d.EV9m-ws6bUG7VMI9wmJWnY5mttMihrbJe0Uk4g"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

JOIN_ROLE = 1530203932247326730
ZL_ROLE = 1530203888895000748
ZL_CHANNEL = 1530204285130903705

CLAN_ROLE = 1530203925460946984
CLAN_CHANNEL = 1530204491805233172

ADMIN_ROLES = [1530203849506164736, 1465419376546287689]
SEND_ADMIN_ROLES = [1407440283444056125, 1407440283444056126, 1407440283444056127]

FRAKCII = {
    "сбу": 1530203904946606110,
    "зсу": 1530203895979049011,
    "дквс": 1530203898269139064,
    "моз": 1530203900475605002,
    "дснс": 1530203902622957759,
    "нпу": 1530203907240755312,
    "змі": 1530203913498788011,
    "вру": 1530203909392437249,
    "уз": 1530203915889545328,
}

async def send_ban_dm(user, reason):
    try:
        embed = discord.Embed(
            title="Patriot GTA",
            description=f"Вас заблоковано на сервері Patriot GTA по причині {reason}",
            color=discord.Color.red()
        )
        await user.send(embed=embed)
    except:
        pass

def has_role(member, role_id):
    return any(r.id == role_id for r in member.roles)

def is_send_admin(member):
    if member.guild_permissions.administrator:
        return True
    return any(r.id in SEND_ADMIN_ROLES for r in member.roles)

def role_position(guild, role_id):
    role = guild.get_role(role_id)
    return role.position if role else -1

def author_can_zl(member, guild):
    zl_pos = role_position(guild, ZL_ROLE)
    max_pos = max((r.position for r in member.roles), default=-1)
    return max_pos >= zl_pos

async def toggle_role(target, role, channel, action_name):
    if role in target.roles:
        try:
            await target.remove_roles(role)
        except:
            pass
    else:
        try:
            await target.add_roles(role)
        except:
            pass

@bot.event
async def on_ready():
    print(f"Бот запущено як {bot.user}")

def extract_id(token):
    token = token.strip().strip("<#@!>")
    try:
        return int(token)
    except:
        return None

async def resolve_channel(guild, message, token):
    if message.channel_mentions:
        return message.channel_mentions[0]
    cid = extract_id(token)
    if cid:
        return guild.get_channel(cid)
    return None

async def resolve_member(guild, message, token):
    if message.mentions:
        return message.mentions[0]
    uid = extract_id(token)
    if uid:
        member = guild.get_member(uid)
        if member:
            return member
        try:
            return await guild.fetch_member(uid)
        except:
            return None
    return None

@bot.event
async def on_member_join(member):
    if member.bot:
        await asyncio.sleep(1)
        async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.bot_add):
            if entry.target.id == member.id:
                inviter = entry.user
                if not (has_role(inviter, ADMIN_ROLES[0]) or has_role(inviter, ADMIN_ROLES[1])):
                    try:
                        await member.guild.ban(member, reason="Несанкціоноване додавання бота")
                    except:
                        pass
                    await send_ban_dm(inviter, "ИДИ НАХУЙ")
                    try:
                        await member.guild.ban(inviter, reason="ИДИ НАХУЙ")
                    except:
                        pass
                break
        return

    role = member.guild.get_role(JOIN_ROLE)
    if role:
        try:
            await member.add_roles(role)
        except:
            pass

@bot.event
async def on_guild_channel_delete(channel):
    guild = channel.guild
    await asyncio.sleep(1)
    async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_delete):
        if entry.target.id == channel.id:
            user = entry.user
            member = guild.get_member(user.id)
            if member:
                if not (has_role(member, ADMIN_ROLES[0]) or has_role(member, ADMIN_ROLES[1])):
                    await send_ban_dm(member, "видалення каналу")
                    try:
                        await guild.ban(member, reason="видалення каналу")
                    except:
                        pass
            break

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip().lower()

    if content.startswith("www") or content.startswith("http://") or content.startswith("https://") or content.startswith("www."):
        try:
            await message.delete()
        except:
            pass
        await send_ban_dm(message.author, "4.3 Оскарження блокування пишіть на форум")
        try:
            await message.guild.ban(message.author, reason="4.3 Посилання")
        except:
            pass
        return

    if message.content.startswith("!зл"):
        if message.channel.id != ZL_CHANNEL:
            return
        if not message.mentions:
            return
        if not author_can_zl(message.author, message.guild):
            return
        target = message.mentions[0]
        role = message.guild.get_role(ZL_ROLE)
        if role:
            await toggle_role(target, role, message.channel, "звільнення")
        return

    for cmd, role_id in FRAKCII.items():
        if message.content.startswith(f"!{cmd}"):
            if message.channel.id != ZL_CHANNEL:
                return
            if not message.mentions:
                return
            if not author_can_zl(message.author, message.guild):
                return
            target = message.mentions[0]
            role = message.guild.get_role(role_id)
            if role:
                await toggle_role(target, role, message.channel, cmd.upper())
            return

    if message.content.startswith("!клан"):
        if message.channel.id != CLAN_CHANNEL:
            return
        if not message.mentions:
            return
        if not author_can_zl(message.author, message.guild):
            return
        target = message.mentions[0]
        role = message.guild.get_role(CLAN_ROLE)
        if role:
            await toggle_role(target, role, message.channel, "клану")
        return

    parts = message.content.split(maxsplit=2)
    cmd_word = parts[0].lower() if parts else ""

    if cmd_word == "!send":
        if not is_send_admin(message.author):
            try:
                await message.author.send("У тебе немає прав на !send (немає потрібної ролі і ти не адміністратор).")
            except:
                pass
            return
        try:
            await message.delete()
        except:
            pass
        if len(parts) < 3:
            try:
                await message.author.send("Формат: !send #канал текст  (або !send ID_каналу текст)")
            except:
                pass
            return
        channel = await resolve_channel(message.guild, message, parts[1])
        if channel:
            try:
                await channel.send(parts[2])
            except:
                pass
        else:
            try:
                await message.author.send("Канал не знайдено. Використай згадку #канал або правильний ID каналу.")
            except:
                pass
        return

    if cmd_word == "!sendls":
        if not is_send_admin(message.author):
            try:
                await message.author.send("У тебе немає прав на !sendls (немає потрібної ролі і ти не адміністратор).")
            except:
                pass
            return
        try:
            await message.delete()
        except:
            pass
        if len(parts) < 3:
            try:
                await message.author.send("Формат: !sendls @юзер текст  (або !sendls ID_юзера текст)")
            except:
                pass
            return
        member = await resolve_member(message.guild, message, parts[1])
        if member:
            try:
                await member.send(parts[2])
            except:
                pass
        else:
            try:
                await message.author.send("Користувача не знайдено. Використай згадку @юзер або правильний ID.")
            except:
                pass
        return

    if content == "!пінг":
        await message.channel.send(f"Понг! {round(bot.latency*1000)}мс")
        return

    if content == "!сервер":
        embed = discord.Embed(title="Patriot GTA", description=f"Учасників: {message.guild.member_count}", color=discord.Color.blue())
        await message.channel.send(embed=embed)
        return

    await bot.process_commands(message)

bot.run(TOKEN)