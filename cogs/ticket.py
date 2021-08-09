import discord, os, os.path, json, asyncio
from discord.ext import commands
from discord.utils import get, find
from discord.ext.commands import has_permissions
import datetime as datetime
from discord_components import (DiscordComponents, Button, ButtonStyle, Select, SelectOption)


class Ticket(commands.Cog):
    def __init__(self, client):
        self.client = client


    # Adds an user to the current ticket
    @commands.command()
    @has_permissions(manage_messages=True)
    async def add(self, ctx, user : discord.Member):
        if ctx.message.channel.category.name == 'Tickets':
            await ctx.message.channel.set_permissions(user, send_messages=True, view_channel=True)
            await ctx.send(embed=discord.Embed(description=f'{ctx.author.mention} added {user.mention} to the ticket', color=65535))


    # Removes an user from the current ticket
    @commands.command()
    @has_permissions(manage_messages=True)
    async def remove(self, ctx, user : discord.Member):
        if ctx.message.channel.category.name == 'Tickets':
            await ctx.message.channel.set_permissions(user, send_messages=False, view_channel=False)
            await ctx.send(embed=discord.Embed(description=f'{ctx.author.mention} removed {user.mention} from the ticket', color=65535))



    # Deletes the current ticket
    @commands.command()
    @has_permissions(manage_messages=True)
    async def delete(self, ctx):
        if ctx.message.channel.category.name == 'Tickets':
            first = await ctx.send(embed=discord.Embed(description=f'Deleting this ticket in **5 seconds**', color=65535))
            await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **4 seconds**', color=65535))
            await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **3 seconds**', color=65535))
            await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **2 seconds**', color=65535))
            await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **1 seconds**', color=65535))
            await ctx.message.channel.delete()
            


    # Closes the current ticket
    @commands.command()
    async def close(self, ctx):
        if ctx.message.channel.category.name == 'Tickets':
            await ctx.message.channel.edit(name=f'closed-{ctx.message.channel.name}')
            await ctx.message.channel.set_permissions(ctx.message.guild.get_member(int(ctx.message.channel.topic)), send_messages=False, view_channel=False)
            
            embed=discord.Embed(title='Ticket Closed', timestamp=datetime.datetime.utcnow(), color=65535)
            embed.set_footer(icon_url= f'{ctx.author.avatar_url}', text=f'{ctx.author}')
            await ctx.send(embed=embed,components=[[
            Button(style=ButtonStyle.grey, label="✉️ SAVE TRANSCRIPT"),
            Button(style=ButtonStyle.grey, label="🔓 REOPEN TICKET"),
            Button(style=ButtonStyle.grey, label="❌ DELETE TICKET")
            ]])

            while True:
                res3 = await self.client.wait_for("button_click")
                if res3.component.label == "✉️ SAVE TRANSCRIPT":
                    with open(os.path.dirname(__file__) + f'\\..\\transcripts\\{res3.channel.name}.txt', 'a') as f:
                        messages = await ctx.message.channel.history(limit=200).flatten()
                        for i in messages:
                            f.write(f'{i}\n')
                        f.close
                    await res3.author.send(file=discord.File(os.path.dirname(__file__) + f'\\..\\transcripts\\{res3.channel.name}.txt'))
                    os.remove(os.path.dirname(__file__) + f'\\..\\transcripts\\{res3.channel.name}.txt')
                
                elif res3.component.label == '🔓 REOPEN TICKET':
                    embed=discord.Embed(title='Ticket Reopened', timestamp=datetime.datetime.utcnow(), color=65535)
                    embed.set_footer(icon_url= f'{res3.author.avatar_url}', text=f'{res3.author}')
                    await res3.channel.send(embed=embed)
                    await ctx.message.channel.edit(name=f'{ctx.message.guild.get_member(int(ctx.message.channel.topic))}')
                    await ctx.message.channel.set_permissions(ctx.message.guild.get_member(int(ctx.message.channel.topic)), send_messages=True, view_channel=True)
                
                elif res3.component.label == "❌ DELETE TICKET":
                    first = await ctx.send(embed=discord.Embed(description=f'Deleting this ticket in **5 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **4 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **3 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **2 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **1 seconds**', color=65535))
                    await ctx.message.channel.delete()



    @commands.command()
    async def claim(self, ctx):
        with open(os.path.dirname(__file__) + '\\..\\json\\data.json','r+') as f:
            data=json.load(f)
            modRole=ctx.message.guild.get_role(int(data[str(ctx.message.guild.id)]["mod_roles"]))
            await ctx.message.channel.set_permissions(modRole, send_messages=False, view_channel=True)
            await ctx.message.channel.set_permissions(ctx.author, send_messages=True, view_channel=True)

            embed=discord.Embed(title='Ticket Claimed', timestamp=datetime.datetime.utcnow(), color=65535)
            embed.set_footer(icon_url= f'{ctx.author.avatar_url}', text=f'{ctx.author}')
            await ctx.send(embed=embed); f.close()





def setup(client):
    client.add_cog(Ticket(client))
