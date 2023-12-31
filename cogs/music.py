import discord as ds
from discord import app_commands
from discord.ext import commands
import yt_dlp as youtube_dl 

ydl_options = {'format': 'bestaudio'}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class Music(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot
        self.nowvoice = {}
        self.playing = {"serverid":[]}
        
    @app_commands.command(name="재생",description="링크를 주면 아르가 노래를 들려줘!")
    async def musicplay(self,interaction:ds.Interaction,link:str):
        if not interaction.user.voice:
            await interaction.response.send_message("`보이스채널`에 들어간 뒤에 사용해줘!")
            return

        await interaction.response.defer()
        if str(interaction.guild.id) not in self.playing:
            self.playing[str(interaction.guild.id)] = []
        if str(interaction.guild.id) not in self.nowvoice:
            self.nowvoice[str(interaction.guild.id)] = voice = await interaction.user.voice.channel.connect()
            if type(voice.channel) == ds.StageChannel:
                await interaction.guild.me.edit(suppress=False)
        else:
            voice:ds.VoiceClient = self.nowvoice[str(interaction.guild.id)]
            if voice.channel != interaction.user.voice.channel:
                await voice.disconnect()
                await voice.move_to(interaction.user.voice.channel)
                self.nowvoice[str(interaction.guild.id)] = voice = await interaction.user.voice.channel.connect()
                if type(voice.channel) == ds.StageChannel:
                    await interaction.guild.me.edit(suppress=False)
        
        def play_music(voice:ds.VoiceClient,looping:bool):
            del self.playing[str(interaction.guild.id)][0]
            if len(self.playing[str(interaction.guild.id)]) == 0:
                voice.stop()
                voice.loop.create_task(voice.disconnect())
                voice.loop.create_task(interaction.channel.send("노래가 모두 끝났습니다"))
                del self.nowvoice[str(interaction.guild.id)]
                return
            with youtube_dl.YoutubeDL(ydl_options) as ydls:
                try:
                    info = ydls.extract_info(self.playing[str(interaction.guild.id)][0],download=False)
                except youtube_dl.DownloadError:
                    play_music(voice)
                    return
            URL = info['url']
            embed = ds.Embed(title=info['title'],description=info['uploader'],url=info['original_url'])
            embed.set_thumbnail(url=info['thumbnail'])
            embed.set_author(name="현재 재생중..!!",url=f"https://discord.com/channels/{voice.guild.id}/{voice.channel.id}")
            if looping:
                voice.loop.create_task(interaction.channel.send(embed=embed))
            voice.play(ds.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS),after=lambda I: play_music(voice,True))
            return embed

        self.playing[str(interaction.guild.id)].append(link)
        if not voice.is_playing():
            self.playing[str(interaction.guild.id)].insert(0,None)
            await voice.voice_connect(True,False)
            await interaction.followup.send("노래를 재생합니다",embed=play_music(voice,False))
        else:
            await interaction.followup.send("노래가 재생중이라 대기열에 추가됩니다")
    
    @app_commands.command(name="일시정지",description="노래를 잠깐 멈춰줄게!")
    async def musicpause(self,interaction:ds.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("`보이스채널`에 들어간 뒤에 사용해줘!")
            return
        
        if str(interaction.guild.id) not in self.nowvoice:
            await interaction.response.send_message("노래를 `재생` 한 뒤에 사용해줘!")
            return
        
        voice:ds.VoiceClient = self.nowvoice[str(interaction.guild.id)]
        
        voice.pause()
        await interaction.response.send_message("지금 노래는 멈춰있어!")
    
    @app_commands.command(name="다시재생",description="일시정지한 노래를 다시 재생해줘!")
    async def musicresume(self,interaction:ds.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("`보이스채널`에 들어간 뒤에 사용해줘!")
            return
        if str(interaction.guild.id) not in self.nowvoice:
            await interaction.response.send_message("노래를 `재생` 한 뒤에 사용해줘!")
            return
        
        voice:ds.VoiceClient = self.nowvoice[str(interaction.guild.id)]
        
        voice.resume()
        await interaction.response.send_message("노래를 다시 재생해줄게!")
    
    @app_commands.command(name="다음노래",description="재생중인 노래를 건너 뛰어!")
    async def skipmusic(self,interaction:ds.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("`보이스채널`에 들어간 뒤에 사용해줘!")
            return
        if str(interaction.guild.id) not in self.nowvoice:
            await interaction.response.send_message("노래를 `재생` 한 뒤에 사용해줘!")
            return
        
        await interaction.response.send_message("현재 노래를 건너뛰고 다음 노래를 재생합니다")
        voice:ds.VoiceClient = self.nowvoice[str(interaction.guild.id)]
        voice.stop()
    
    @app_commands.command(name="노래멈춰",description="노래.. 그만들을꺼야..?") 
    async def musicstop(self,interaction:ds.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("`보이스채널`에 들어간 뒤에 사용해줘!")
            return
        if str(interaction.guild.id) not in self.nowvoice:
            await interaction.response.send_message("노래를 `재생` 한 뒤에 사용해줘!")
            return
        
        voice:ds.VoiceClient = self.nowvoice[str(interaction.guild.id)]
        
        voice.stop()
        await voice.disconnect()
        await interaction.response.send_message("그만 불러줄게!")
    
    @app_commands.command(name="일로와",description="아르라는 가수를 납치합니다")
    async def movehere(self,interaction:ds.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("`보이스채널`에 들어간 뒤에 사용해줘!")
            return
        
        voice:ds.VoiceClient = self.nowvoice[str(interaction.guild.id)]
        await voice.disconnect()
        await voice.move_to(interaction.user.voice.channel)
        self.nowvoice[str(interaction.guild.id)] = voice = await interaction.user.voice.channel.connect()
        if type(voice.channel) == ds.StageChannel:
            await interaction.guild.me.edit(suppress=False)
        await interaction.response.send_message(f"아르는 {interaction.user.voice.channel.mention} 여기로 잡혀갔어..")