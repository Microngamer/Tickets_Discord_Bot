import discord, os, os.path, json, asyncio
from discord.ext import commands
from discord.utils import get, find
from discord.ext.commands import has_permissions
import datetime as datetime
from discord_components import *


class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client




    # Setting up the JSON File for the server and ticket
    @commands.command()
    @has_permissions(administrator=True)
    async def setup(self, ctx, modRole : discord.Role):
        with open(os.path.dirname(__file__) + '\\..\\json\\data.json','r+') as f:
            data=json.load(f); await ctx.message.delete()
            if str(ctx.message.guild.id) not in data:
                data.update({str(ctx.message.guild.id) : {"mod_roles" : int(modRole.id)}})
                f.seek(0); json.dump(data, f, indent=4); f.truncate(); f.close()
            
            if not get(ctx.message.guild.categories, name='Tickets'):
                category = await ctx.message.guild.create_category('Tickets')
                await category.set_permissions(ctx.guild.default_role, send_messages=False, view_channel=False)
                await category.set_permissions(modRole, send_messages=True, view_channel=True)
                ticket_logs = await ctx.message.guild.create_text_channel('ticket_logs', category=category, sync_permissions=True)
                await ticket_logs.set_permissions(modRole, send_messages=False, view_channel=True)

        await ctx.send(
        embed=discord.Embed(title='New Ticket', description='Click here to create a new support ticket!', color=65535),
        components=[Button(style=ButtonStyle.grey, label="📩 Create Ticket", custom_id="new_ticket")])


        while True:
            res = await self.client.wait_for("button_click"); category = get(res.guild.categories, name='Tickets')

            # Creating a new ticket button
            if res.component.id == "new_ticket":
                if not get(res.guild.channels, name=f'{res.author}'):

                    channel = await res.guild.create_text_channel(f'{res.author}', topic=f'{res.author.id}', category=category)
                    await channel.set_permissions(res.author, send_messages=True, view_channel=True)
                    embed = discord.Embed(title='New Support Ticket', color=65535, timestamp=datetime.datetime.utcnow())
                    embed.set_footer(icon_url= f'{res.author.avatar_url}', text=f'{res.author}')

                    await channel.send(f'{res.author.mention}', delete_after=1)
                    await channel.send(f'<@&{data[str(res.guild.id)]["mod_roles"]}>', delete_after=1)
                    await res.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Ticket Created** {channel.mention}')
                
                    await channel.send(embed=embed, components=[[
                        Button(style=ButtonStyle.grey, label='✅ Claim', custom_id='claim_ticket'),
                        Button(style=ButtonStyle.grey, label="✉️ Save", custom_id='save_transcript'),
                        Button(style=ButtonStyle.grey, label="🔒 Close", custom_id='close_ticket')
                        
                    ]])
                


            #Claiming a ticket button
            if res.component.id == 'claim_ticket':
                user = res.guild.get_member(int(res.author.id))
                if res.guild.get_role(int(data[str(res.guild.id)]["mod_roles"])) in user.roles:
                    modRole=res.guild.get_role(int(data[str(res.guild.id)]["mod_roles"]))
                    await res.channel.set_permissions(modRole, send_messages=False, view_channel=True)
                    await res.channel.set_permissions(res.author, send_messages=True, view_channel=True)

                    embed=discord.Embed(title='Ticket Claimed', timestamp=datetime.datetime.utcnow(), color=65535)
                    embed.set_footer(icon_url= f'{res.author.avatar_url}', text=f'{res.author}')
                    await res.channel.send(embed=embed)
                    await res.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Ticket Claimed** {res.channel.mention}')



            # Closing a ticket button
            if res.component.id == "close_ticket":
                await channel.edit(name=f'closed-{channel.name}')
                await channel.set_permissions(res.guild.get_member(int(res.channel.topic)), send_messages=False, view_channel=False)
                
                embed=discord.Embed(title='Ticket Closed', timestamp=datetime.datetime.utcnow(), color=65535)
                embed.set_footer(icon_url= f'{res.author.avatar_url}', text=f'{res.author}')
                await channel.send(embed=embed,components=[[
                Button(style=ButtonStyle.grey, label="✉️ Save", custom_id='save_transcript'),
                Button(style=ButtonStyle.grey, label="🔓 Reopen", custom_id='reopen_ticket'),
                Button(style=ButtonStyle.grey, label="❌ Delete", custom_id='delete_ticket')]])
                await res.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Ticket Closed** {res.channel.mention}')

                

            # Saving text transcript button
            if res.component.id == "save_transcript":
                with open(os.path.dirname(__file__) + f'\\..\\transcripts\\{res.channel.name}.txt', 'a') as f:
                    messages = await res.channel.history().flatten()
                    for msg in messages:
                        f.write(f'{msg.author}: {msg.content}  |  Sent: {msg.created_at}, Edited: {msg.edited_at}, Reactions: {msg.reactions}, ID {msg.id}, Attachments: {msg.attachments}, URL: {msg.jump_url}\n')

                    for i in messages:
                        f.write(f'\n{i}')
                    f.close
                await res.author.send(file=discord.File(os.path.dirname(__file__) + f'\\..\\transcripts\\{res.channel.name}.txt'))
                os.remove(os.path.dirname(__file__) + f'\\..\\transcripts\\{res.channel.name}.txt')
                await res.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Transcript Saved** {res.channel.mention}')
                


            # Reopening a ticket button
            if res.component.id == 'reopen_ticket':
                user = res.guild.get_member(int(res.author.id))
                if res.guild.get_role(int(data[str(res.guild.id)]["mod_roles"])) in user.roles:
                    embed=discord.Embed(title='Ticket Reopened', timestamp=datetime.datetime.utcnow(), color=65535)
                    embed.set_footer(icon_url= f'{res.author.avatar_url}', text=f'{res.author}')
                    await res.channel.send(embed=embed)
                    await channel.edit(name=f'{ctx.message.guild.get_member(int(res.channel.topic))}')
                    await channel.set_permissions(res.guild.get_member(int(res.channel.topic)), send_messages=True, view_channel=True)
                    await res.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Ticket Reopened** {res.channel.mention}')



            # Deleting a ticket button
            if res.component.id == "delete_ticket":
                user = res.guild.get_member(int(res.author.id))
                if res.guild.get_role(int(data[str(res.guild.id)]["mod_roles"])) in user.roles:
                    first = await channel.send(embed=discord.Embed(description=f'Deleting this ticket in **5 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **4 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **3 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **2 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **1 seconds**', color=65535))
                    await res.channel.delete()
                




    # Sending ticket messages to the ticket_logs channel
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.category.name == 'Tickets' and message.author.id != self.client.user.id:
            channel = get(message.guild.channels, name='ticket_logs')
            embed=discord.Embed(title=f'Ticket: {message.channel.name}', description=f'{message.content}', color=65535, timestamp=datetime.datetime.utcnow())
            embed.set_footer(icon_url= f'{message.author.avatar_url}', text=f'{message.author}')
            await channel.send(embed=embed)




def setup(client):
    client.add_cog(Settings(client))
