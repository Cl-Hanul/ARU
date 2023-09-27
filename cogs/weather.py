import discord as ds
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select, Button

import json

class Weather(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot
        
    @app_commands.command(name="위치설정",description="아르가 날씨를 알려줄 때 참고할 정보")
    @app_commands.describe(rlg="광역자치단체(Regional Local Government)")
    @app_commands.choices(rlg=[app_commands.Choice(name=pos,value=pos) for pos in ["서울특별시","부산광역시","대구광역시","인천광역시","광주광역시","대전광역시","울산광역시","세종특별자치시","경기도","충청북도","충청남도","전라북도","전라남도","경상북도","경상남도","제주특별자치도","이어도","강원특별자치도"]])
    async def setposition(self, interaction:ds.Interaction, rlg:app_commands.Choice[str]):
        with open('info\\kor_position.json','r') as file:
            kor_position = json.load(file)
        show_position = kor_position[rlg.value]
        print(show_position)
        res = False
        page = 0
        pageend = (len(show_position)//10)
        
        numemotes = ['','one','two',"three",'four','five','six','seven','eight','nine','keycap_ten']
        
        async def makeview(res,interaction:ds.Interaction,number, page):
            page += number
            position_list = show_position[10*page:10*page+10] if len(show_position[10*page:]) >= 10 else show_position[10*page:]
            view = View()
            rev = Button(label="⬅️",disabled=True if page == 0 else False)
            nev = Button(label="➡️",disabled=True if page == pageend else False)
            def embed() -> ds.Embed:
                embed = ds.Embed(title="지역을 선택해주세요",description="날씨정보를 알아볼 수 있습니다")
                for position,num in zip(position_list,range(1,11)):
                    embed.add_field(name=f":{numemotes[num]}:{position['name']}",value="---",inline=False)
                return embed
            selections = Select(options=[ds.SelectOption(label=f"{position['name']}",value=f"{position['name']}||{position['coord']['x']}||{position['coord']['y']}") for position in position_list])
            async def select_callback(interaction:ds.Interaction):
                with open("data\\weather.json","r",encoding="UTF-8") as file:
                    weatherdata = json.load(file)
                weatherdata['positions'][str(interaction.user.id)] = {
                    "name":selections.values[0].split('||')[0],
                    "coord":{"x":selections.values[0].split('||')[1],"y":selections.values[0].split('||')[2]}
                }
                with open('data\\weather.json',"w",encoding="UTF-8") as file:
                    json.dump(weatherdata,file)
                await interaction.response.edit_message(content="이제 닫으셔도 돼요!",embed=None,view=None)
            selections.callback = select_callback
            async def rev_callback(interaction:ds.Interaction):
                view = await makeview(res,interaction,-1,page)
            rev.callback = rev_callback
            async def nev_callback(interaction:ds.Interaction):
                view = await makeview(res,interaction,1,page)
            nev.callback = nev_callback
            view.add_item(selections)
            view.add_item(rev)
            view.add_item(nev)
            
            if not res:
                await interaction.response.send_message(view=view,embed=embed(),ephemeral=True)
                res = True
            else:
                await interaction.response.edit_message(view=view,embed=embed())
        await makeview(res,interaction, 0, page)