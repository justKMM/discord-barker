import discord
from discord.ext import commands
import os

from music_cog import music_cog
from help_cog import help_cog



bot = commands.Bot(command_prefix="*", intents=discord.Intents.all())


bot.remove_command("help")


@bot.event
async def on_ready():
    
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog(bot))
    print("ok")
    
with open('token.txt') as token_file:
    token = token_file.readline() #Your personal application token here

bot.run(token)
 
