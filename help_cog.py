import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
---
General commands:
*help [*h] - show available commands
*play [*p song_name] - play song (if queue empty && nothing's playing), add music to queue if other songs are available 
*queue [*q] - show current queue
*skip [*s] - skip current song
*clear [*c] - clear queue
*leave [*l] - kick bot out of voice channel, stop song, clear queue
*pause - pause the music
*resume [*r] - resume the music
---
"""
        self.text_channel_text = []

    @commands.Cog.listener()
    async def on_ready(self):
        
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_text.append(channel)

            await self.send_to_all(self.help_message)


    async def send_to_all(self, msg):
        for channel in self.text_channel_text:
            await channel.send(msg)

    @commands.command(name="help", aliases=["h"], help="Display available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)