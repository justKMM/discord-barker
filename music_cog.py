import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    #Constructor
    def __init__(self, bot):
        #The damn bot
        commands = bot
        #Booleans for bot's current state
        self.is_playing = False
        self.is_paused = False
        #Queue of selected songs
        self.music_queue = []
        #YouTube DL Options
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        #FFMPEG Options
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        #Current voice channel of the bot
        self.vc = None

    #Function to search song on youtube (using Youtube DL API)
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False
        return {'source': info['formats'][0]['url'], 'title': info['title']}

    
    #Function to play next song
    def play_next(self):
        #If queue still has songs left
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        #Queue empty
        else:
            self.is_playing = False

    #Function to check if bot is in a voice channel && play the music in that channel
    async def play_music(self, ctx):
        #If songs queue is not empty
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            #If bot is not yet in a voice channel
            if self.vc == None or not self.vc.is_connected():
                self.vc = await ctx.author.voice.channel.connect()
                #If bot failed to connect to a voice channel
                if self.vc == None:
                    await ctx.send("Could not connect to voice channel")
                    return
            #If bot is in another voice channel -> move to user's current channel
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        #Queue empty
        else:
            self.is_playing = False


    #Command available to users - check if user is in a voice channel && play the music
    @commands.command(name="play", aliases=["p"], help="Play the selected song")
    async def play(self, ctx, *args):
        #(Argument from user) Keywords of the song
        query = " ".join(args)
        #Variable holding information about current voice channel
        voice_channel = ctx.author.voice.channel
        #Check if user is in a voice channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel")
        #Check if music is currently paused
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download song, try a different keyword")
            else:
                await ctx.send("Song added to queue")
                self.music_queue.append([song, voice_channel])

            if self.is_playing == False:
                await self.play_music(ctx)
                self.is_playing = True
                self.is_paused = False

    #Command - pause/resume the music
    @commands.command(name="pause", aliases=["."], help="Pause the music")
    async def pause(self, ctx):
        """if self.vc == None or not self.vc.is_connected():
            self.vc = await ctx.author.voice.channel.connect()
            self.is_playing = False
            self.is_paused = True"""
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            await ctx.send("Music paused")

    @commands.command(name="resume", aliases=["r"])
    async def resume(self, ctx):
        """if self.vc == None or not self.vc.is_connected():
            self.vc = await ctx.author.voice.channel.connect()
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()"""
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
        elif self.is_playing:
            await ctx.send("Music playing")
            

    #Command - skip song
    @commands.command(name="skip", aliases=["s"], help="Skip the music")
    async def skip(self, ctx, *args):
        """if self.vc == None or not self.vc.is_connected():
            self.vc = await ctx.author.voice.channel.connect()
            self.is_playing = True"""
        if self.vc != None and self.is_playing:
            self.vc.stop()
            self.is_playing = False
            await self.play_music(ctx)


    #Command - display songs in queue
    @commands.command(name="queue", aliases=["q"], help="Display songs in queue")
    async def queue(self, ctx):
        queue = ""

        for i in range(0, len(self.music_queue)):
            queue += self.music_queue[i][0]['title'] + '\n'

        if queue != "": 
            await ctx.send(queue)
        else:
            await ctx.send("Queue empty")

    #Command - stop music && clear queue
    @commands.command(name="clear", aliases=["c"], help="Stop music, clear queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared")

    #Command - stop music && leave voice channel
    @commands.command(name="leave", aliases=["l"], help="Stop music, leave voice channel")
    async def leave(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
        await ctx.send("Left voice channel, queue cleared. Use commands *p again to re-add songs")

    #Test commands
    @commands.command(name="test")
    async def test(self, ctx, args):
        await ctx.send(args)


