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


            
                
    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        with open(os.path.dirname(__file__) + '\\..\\json\\data.json','r+') as f:
            data=json.load(f); category = get(interaction.guild.categories, name='Tickets')
            if interaction.component.id == "new_ticket":
                if not get(interaction.guild.channels, name=f'{interaction.author}'):

                    channel = await interaction.guild.create_text_channel(f'{interaction.author}', topic=f'{interaction.author.id}', category=category)
                    await channel.set_permissions(interaction.author, send_messages=True, view_channel=True)
                    embed = discord.Embed(title='New Support Ticket', color=65535, timestamp=datetime.datetime.utcnow())
                    embed.set_footer(icon_url= f'{interaction.author.avatar_url}', text=f'{interaction.author}')

                    await channel.send(f'{interaction.author.mention}', delete_after=1)
                    await channel.send(f'<@&{data[str(interaction.guild.id)]["mod_roles"]}>', delete_after=1)
                    await interaction.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Ticket Created** {channel.mention}')
                
                    await channel.send(embed=embed, components=[[
                        Button(style=ButtonStyle.grey, label='✅ Claim', custom_id='claim_ticket'),
                        Button(style=ButtonStyle.grey, label="📃 Save", custom_id='save_transcript'),
                        Button(style=ButtonStyle.grey, label="🔒 Close", custom_id='close_ticket')
                        ]])
                


            #Claiming a ticket button
            if interaction.component.id == 'claim_ticket':
                user = interaction.guild.get_member(int(interaction.author.id))
                if interaction.guild.get_role(int(data[str(interaction.guild.id)]["mod_roles"])) in user.roles:
                    modRole=interaction.guild.get_role(int(data[str(interaction.guild.id)]["mod_roles"]))
                    await interaction.channel.set_permissions(modRole, send_messages=False, view_channel=True)
                    await interaction.channel.set_permissions(interaction.author, send_messages=True, view_channel=True)

                    embed=discord.Embed(title='Ticket Claimed', timestamp=datetime.datetime.utcnow(), color=65535)
                    embed.set_footer(icon_url= f'{interaction.author.avatar_url}', text=f'{interaction.author}')
                    await interaction.channel.send(embed=embed)
                    await interaction.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Ticket Claimed** {interaction.channel.mention}')



            # Closing a ticket button
            if interaction.component.id == "close_ticket":
                await interaction.channel.edit(name=f'closed-{interaction.channel.name}')
                await interaction.channel.set_permissions(interaction.guild.get_member(int(interaction.channel.topic)), send_messages=False, view_channel=False)
                
                embed=discord.Embed(title='Ticket Closed', timestamp=datetime.datetime.utcnow(), color=65535)
                embed.set_footer(icon_url= f'{interaction.author.avatar_url}', text=f'{interaction.author}')
                await interaction.channel.send(embed=embed, components=[[
                Button(style=ButtonStyle.grey, label="🔓 Reopen", custom_id='reopen_ticket'),
                Button(style=ButtonStyle.grey, label="📃 Save", custom_id='save_transcript'),
                Button(style=ButtonStyle.grey, label="❌ Delete", custom_id='delete_ticket')]])
                await interaction.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Ticket Closed** {interaction.channel.mention}')

                

            # Saving text transcript button
            if interaction.component.id == "save_transcript":
                with open(os.path.dirname(__file__) + f'\\..\\transcripts\\{interaction.channel.name}.txt', 'a') as f:
                    messages = await interaction.channel.history().flatten()
                    for msg in messages:
                        f.write(f'{msg.author}: {msg.content}  |  Sent: {msg.created_at}, Edited: {msg.edited_at}, Reactions: {msg.reactions}, ID {msg.id}, Attachments: {msg.attachments}, URL: {msg.jump_url}, Activity: {msg.activity}, Type: {msg.type}, Reference: {msg.reference}, Guild_ID: {msg.guild.id}, Guild: {msg.guild}\n')
                    f.close
                await interaction.author.send(file=discord.File(os.path.dirname(__file__) + f'\\..\\transcripts\\{interaction.channel.name}.txt'))
                os.remove(os.path.dirname(__file__) + f'\\..\\transcripts\\{interaction.channel.name}.txt')
                await interaction.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Transcript Saved** {interaction.channel.mention}')
                


            # Reopening a ticket button
            if interaction.component.id == 'reopen_ticket':
                user = interaction.guild.get_member(int(interaction.author.id))
                if interaction.guild.get_role(int(data[str(interaction.guild.id)]["mod_roles"])) in user.roles:
                    embed=discord.Embed(title='Ticket Reopened', timestamp=datetime.datetime.utcnow(), color=65535)
                    embed.set_footer(icon_url= f'{interaction.author.avatar_url}', text=f'{interaction.author}')
                    await interaction.channel.send(embed=embed)
                    await interaction.channel.edit(name=f'{interaction.guild.get_member(int(interaction.channel.topic))}')
                    await interaction.channel.set_permissions(interaction.guild.get_member(int(interaction.channel.topic)), send_messages=True, view_channel=True)
                    await interaction.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Ticket Reopened** {interaction.channel.mention}')



            # Deleting a ticket button
            if interaction.component.id == "delete_ticket":
                user = interaction.guild.get_member(int(interaction.author.id))
                if interaction.guild.get_role(int(data[str(interaction.guild.id)]["mod_roles"])) in user.roles:
                    first = await interaction.channel.send(embed=discord.Embed(description=f'Deleting this ticket in **5 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **4 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **3 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **2 seconds**', color=65535))
                    await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **1 seconds**', color=65535))
                    await interaction.channel.delete()










    # Sending ticket messages to the ticket_logs channel
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.category.name == 'Tickets' and message.author.id != self.client.user.id:
            log_channel = get(message.guild.channels, name='ticket_logs')
            embed=discord.Embed(title=f'Ticket: {message.channel.name}', description=f'{message.content}', color=65535, timestamp=datetime.datetime.utcnow())
            embed.set_footer(icon_url= f'{message.author.avatar_url}', text=f'{message.author}')
            await log_channel.send(embed=embed)








def setup(client):
    client.add_cog(Settings(client))
