import time
import requests
import datetime
import discord
from discord.ext import tasks
from discord import app_commands

## --!! SETTINGS !!-- ############################################################################################################
token = "YOUR TOKEN HERE" # bot token
themeColor = 0x32a852 #Hex color code for embed color theme
logging_channel = 1210744928527847446 # Channel that logs each ban/unban
permission_role = 1211325255906365531 # Role that is able to use commands
ban_payload = {
    'delete_message_days': 7  # Replace with the number of days of messages you want to delete of the banned user (max is 7)
}
##################################################################################################################################

headers = {
    'Authorization': f'Bot {token}',
    'Content-Type': 'application/json',
}



intents = discord.Intents.default()

Client = discord.AutoShardedClient(intents=intents)
tree = app_commands.CommandTree(Client)


async def logger(moderator: discord.User, user: discord.User, ban, reason=None):
    log = discord.Embed(title=f"GLOBAL {'BAN' if ban else 'UNBAN'}", color=themeColor)
    log.set_thumbnail(url=(user.avatar.url if user.avatar else "https://www.google.com/url?sa=i&url=https%3A%2F%2Ftwitter.com%2FWeedleTwineedle%2Fstatus%2F1655708119987638272&psig=AOvVaw2sSG69R5l25ukxKDZlszw2&ust=1717629672300000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCKCU56WLw4YDFQAAAAAdAAAAABAE"))
    if ban:
        log.description = f"USER: {user.name}({user.id})\nMOD: {moderator.name}({moderator.id})\nREASON: {reason}\nDATE: <t:{round(datetime.datetime.now().timestamp())}>"
    else:
        log.description = f"USER: {user.name}({user.id})\nMOD: {moderator.name}({moderator.id})\nDATE: <t:{round(datetime.datetime.now().timestamp())}>"

    channel = Client.get_channel(logging_channel)
    await channel.send(embed=log)

def WideBan(user, guilds, reason=None):
    waitTime = 1/(len(guilds))
    errors = ""
    if reason:
        headers["X-Audit-Log-Reason"] = f"[GLOBAL BAN]: {reason}"
    else:
        headers["X-Audit-Log-Reason"] = f"[GLOBAL BAN]"
    for guild in guilds:
        time.sleep(waitTime) # Avoid discord rate limit since the bot is not verified.
        url = f'https://discord.com/api/v10/guilds/{guild.id}/bans/{user.id}'
        response = requests.put(url, headers=headers, json=ban_payload)
        if response.status_code == 204:
            print("Ban was successful.")
        else:
            print(f"Failed to ban user: {response.status_code}")
            errors += f"\n{guild.name}: {response.text}"
    headers["X-Audit-Log-Reason"] = None
    return errors

def WideUnban(user,guilds):
    errors = ""
    for guild in guilds:
        url = f'https://discord.com/api/v8/guilds/{guild.id}/bans/{user.id}'
        response = requests.delete(url, headers=headers, json=ban_payload)
        if response.status_code == 204:
            print("UnBan was successful.")
        else:
            print(f"Failed to Unban user: {response.status_code}")
            errors += f"\n{guild.name}: {response.text}"
    return errors


async def roleCheck(roles: list[discord.Role]):
    for role in roles:
        if role.id == permission_role:
            return True
    return False

@Client.event
async def on_ready():
    await tree.sync()
    print("ToadBot Online")

@tree.command(name="global-ban",description="Bans user across all servers.")
async def globalBan(inter: discord.Interaction, user:discord.User, reason:str):
    if await roleCheck(inter.user.roles):
        await inter.response.defer()
        err = WideBan(user=user, guilds=Client.guilds, reason=reason)

        ## EMBED STYLE ##
        resp = discord.Embed(title="Global Ban", color=themeColor)
        resp.description = f"`{user.name} ({user.id})` was just banned globally. \n\nReason: {reason}"
        if user.avatar:
            resp.set_thumbnail(url=user.avatar.url)

        if err != "":
            resp.add_field(name="Errors", value=err)
        #################
        await logger(moderator=inter.user, user=user, ban=True, reason=reason)
        await inter.followup.send(embed=resp)

@tree.command(name="global-unban",description="UnBans user across all servers.")
async def globalUnBan(inter: discord.Interaction, user:discord.User):
    if await roleCheck(inter.user.roles):
        await inter.response.defer()
        err = WideUnban(user=user, guilds=Client.guilds)

        ## EMBED STYLE ##
        resp = discord.Embed(title="Global UnBan", color=themeColor)
        resp.description = f"`{user.name} ({user.id})` was just Unbanned globally."
        if user.avatar:
            resp.set_thumbnail(url=user.avatar.url)
        if err != "":
            resp.add_field(name="Errors", value=err)
        #################
        await logger(moderator=inter.user, user=user, ban=False)
        await inter.followup.send(embed=resp)

Client.run(token)
