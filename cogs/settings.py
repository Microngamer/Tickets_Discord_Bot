import discord, os, os.path, json, asyncio
from discord.ext import commands
from discord.utils import get, find
from discord.ext.commands import has_permissions
import datetime as datetime
from discord_components import (DiscordComponents, Button, ButtonStyle, Select, SelectOption)


class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client




    # Setting up the JSON File for the server and ticket
    @commands.command()
    @has_permissions(administrator=True)
    async def setup(self, ctx, modRole : discord.Role):
        with open(os.path.dirname(__file__) + '\\..\\json\\data.json','r+') as f:
            data=json.load(f)
            if str(ctx.message.guild.id) not in data:
                data.update({str(ctx.message.guild.id) : {"mod_roles" : int(modRole.id)}}); f.seek(0); json.dump(data, f, indent=4); f.truncate(); f.close()
            
            if not get(ctx.message.guild.categories, name='Tickets'):
                category = await ctx.message.guild.create_category('Tickets')
                await category.set_permissions(ctx.guild.default_role, send_messages=False, view_channel=False)
                await category.set_permissions(modRole, send_messages=True, view_channel=True)
                ticket_logs = await ctx.message.guild.create_text_channel('ticket_logs', category=category, sync_permissions=True)
                await ticket_logs.set_permissions(modRole, send_messages=False, view_channel=True)

            await ctx.send(
            embed=discord.Embed(title='New Ticket', description='Click here to create a new support ticket!', color=65535),
            components=[Button(style=ButtonStyle.grey, label="📩 NEW TICKET")])

            while True:
                res = await self.client.wait_for("button_click"); category = get(res.guild.categories, name='Tickets')

                if res.component.label == "📩 NEW TICKET":
                    channel = await res.guild.create_text_channel(f'{res.author}', topic=f'{res.author.id}', category=category)
                    await channel.set_permissions(res.author, send_messages=True, view_channel=True)
                    embed = discord.Embed(title='New Support Ticket', color=65535, timestamp=datetime.datetime.utcnow())
                    embed.set_footer(icon_url= f'{res.author.avatar_url}', text=f'{res.author}')

                    await channel.send(f'{res.author.mention}', delete_after=1)
                    await channel.send(f'<@&{data[str(res.guild.id)]["mod_roles"]}>', delete_after=1)
                    
                    await channel.send(embed=embed, components=[[
                        Button(style=ButtonStyle.grey, label="🔒 CLOSE TICKET"),
                        Button(style=ButtonStyle.grey, label="❌ DELETE TICKET"),
                        Button(style=ButtonStyle.grey, label='✅ CLAIM TICKET')
                    ]])
                    close_res = await self.client.wait_for("button_click")


                    if close_res.component.label == '✅ CLAIM TICKET':
                        modRole=close_res.guild.get_role(int(data[str(close_res.guild.id)]["mod_roles"]))
                        await close_res.channel.set_permissions(modRole, send_messages=False, view_channel=True)
                        await close_res.channel.set_permissions(close_res.author, send_messages=True, view_channel=True)

                        embed=discord.Embed(title='Ticket Claimed', timestamp=datetime.datetime.utcnow(), color=65535)
                        embed.set_footer(icon_url= f'{close_res.author.avatar_url}', text=f'{close_res.author}')
                        await close_res.channel.send(embed=embed); f.close()


                    elif close_res.component.label == "🔒 CLOSE TICKET":
                        await channel.edit(name=f'closed-{channel.name}')
                        await channel.set_permissions(close_res.guild.get_member(int(close_res.channel.topic)), send_messages=False, view_channel=False)
                        
                        embed=discord.Embed(title='Ticket Closed', timestamp=datetime.datetime.utcnow(), color=65535)
                        embed.set_footer(icon_url= f'{close_res.author.avatar_url}', text=f'{close_res.author}')
                        await channel.send(embed=embed,components=[[
                        Button(style=ButtonStyle.grey, label="✉️ SAVE TRANSCRIPT"),
                        Button(style=ButtonStyle.grey, label="❌ DELETE TICKET"),
                        Button(style=ButtonStyle.grey, label="🔓 REOPEN TICKET")
                        ]])
                        res2 = await self.client.wait_for("button_click")
                        if res2.component.label == "✉️ SAVE TRANSCRIPT":
                            with open(os.path.dirname(__file__) + f'\\..\\transcripts\\{close_res.channel.name}.txt', 'a') as f:
                                messages = await close_res.channel.history(limit=200).flatten()
                                for i in messages:
                                    f.write(f'{i}\n')
                                f.close
                            await res2.author.send(file=discord.File(os.path.dirname(__file__) + f'\\..\\transcripts\\{res2.channel.name}.txt'))
                            os.remove(os.path.dirname(__file__) + f'\\..\\transcripts\\{res2.channel.name}.txt')
                        
                        elif res2.component.label == '🔓 REOPEN TICKET':
                            embed=discord.Embed(title='Ticket Reopened', timestamp=datetime.datetime.utcnow(), color=65535)
                            embed.set_footer(icon_url= f'{res2.author.avatar_url}', text=f'{res2.author}')
                            await res2.channel.send(embed=embed)
                            await channel.edit(name=f'{ctx.message.guild.get_member(int(res2.channel.topic))}')
                            await channel.set_permissions(close_res.guild.get_member(int(close_res.channel.topic)), send_messages=True, view_channel=True)
                        
                        elif res2.component.label == "❌ DELETE TICKET":
                            first = await channel.send(embed=discord.Embed(description=f'Deleting this ticket in **5 seconds**', color=65535))
                            await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **4 seconds**', color=65535))
                            await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **3 seconds**', color=65535))
                            await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **2 seconds**', color=65535))
                            await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **1 seconds**', color=65535))
                            await close_res.channel.delete()

                    elif close_res.component.label == "❌ DELETE TICKET":
                        first = await channel.send(embed=discord.Embed(description=f'Deleting this ticket in **5 seconds**', color=65535))
                        await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **4 seconds**', color=65535))
                        await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **3 seconds**', color=65535))
                        await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **2 seconds**', color=65535))
                        await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **1 seconds**', color=65535))
                        await close_res.channel.delete()




    # Adding a role that can view tickets to the JSON File
    @commands.command()
    @has_permissions(administrator=True)
    async def setrole(self, ctx, role : discord.Role):
        with open(os.path.dirname(__file__) + '\\..\\json\\data.json','r+') as f:
            data=json.load(f)
            data[str(ctx.message.guild.id)]["mod_roles"] = role.id

            category = get(ctx.message.guild.categories, name='Tickets')
            await category.set_permissions(role, send_messages=True, view_channel=True)
            f.seek(0); json.dump(data, f, indent=4); f.truncate(); f.close()
            await ctx.message.delete()
            await ctx.send(embed=discord.Embed(description=f'{ctx.author.mention} set the ticket mod role to {role.mention}', color=65535, delete_after=2))





    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.category.name == 'Tickets' and message.author.id != self.client.user.id:
            channel = get(message.guild.channels, name='ticket_logs')
            embed=discord.Embed(title=f'Ticket: {message.channel.name}', description=f'{message.content}', color=65535, timestamp=datetime.datetime.utcnow())
            embed.set_footer(icon_url= f'{message.author.avatar_url}', text=f'{message.author}')
            await channel.send(embed=embed)






def setup(client):
    client.add_cog(Settings(client))
