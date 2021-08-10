import discord, os, os.path, json, asyncio
from discord.ext import commands
from discord.utils import get, find
from discord.ext.commands import has_permissions
import datetime as datetime
from discord_components import *


class Ticket(commands.Cog):
    def __init__(self, client):
        self.client = client


    # Adds an user to the current ticket
    @commands.command()
    @has_permissions(manage_messages=True)
    async def add(self, ctx, user : discord.Member):
        with open(os.path.dirname(__file__) + '\\..\\json\\data.json','r+') as f:
            data=json.load(f)
            if ctx.message.guild.get_role(int(data[str(ctx.message.guild.id)]["mod_roles"])) in ctx.author.roles and ctx.message.channel.category.name == 'Tickets':
                await ctx.message.channel.set_permissions(user, send_messages=True, view_channel=True)
                await ctx.send(embed=discord.Embed(description=f'{ctx.author.mention} added {user.mention} to the ticket', color=65535))
            f.close()


    # Removes an user from the current ticket
    @commands.command()
    @has_permissions(manage_messages=True)
    async def remove(self, ctx, user : discord.Member):
        with open(os.path.dirname(__file__) + '\\..\\json\\data.json','r+') as f:
            data=json.load(f)
            if ctx.message.guild.get_role(int(data[str(ctx.message.guild.id)]["mod_roles"])) in ctx.author.roles and ctx.message.channel.category.name == 'Tickets':
                await ctx.message.channel.set_permissions(user, send_messages=False, view_channel=False)
                await ctx.send(embed=discord.Embed(description=f'{ctx.author.mention} removed {user.mention} from the ticket', color=65535))
            f.close()


    # Deletes the current ticket
    @commands.command()
    @has_permissions(manage_messages=True)
    async def delete(self, ctx):
        with open(os.path.dirname(__file__) + '\\..\\json\\data.json','r+') as f:
            data=json.load(f)
            if ctx.message.guild.get_role(int(data[str(ctx.message.guild.id)]["mod_roles"])) in ctx.author.roles and ctx.message.channel.category.name == 'Tickets':
                first = await ctx.send(embed=discord.Embed(description=f'Deleting this ticket in **5 seconds**', color=65535))
                await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **4 seconds**', color=65535))
                await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **3 seconds**', color=65535))
                await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **2 seconds**', color=65535))
                await asyncio.sleep(1); await first.edit(embed=discord.Embed(description=f'Deleting this ticket in **1 seconds**', color=65535))
                await ctx.message.channel.delete()
            f.close()


    # Closes the current ticket
    @commands.command()
    async def close(self, ctx):
        if ctx.message.channel.category.name == 'Tickets':
            await ctx.message.channel.set_permissions(ctx.message.guild.get_member(int(ctx.message.channel.topic)), send_messages=False, view_channel=False)
            
            embed=discord.Embed(title='Ticket Closed', timestamp=datetime.datetime.utcnow(), color=65535)
            embed.set_footer(icon_url= f'{ctx.author.avatar_url}', text=f'{ctx.author}')
            await ctx.send(embed=embed,components=[[
            Button(style=ButtonStyle.grey, label="✉️ Save Transcript", custom_id='save_transcript'),
            Button(style=ButtonStyle.grey, label="🔓 Reopen", custom_id='reopen_ticket'),
            Button(style=ButtonStyle.grey, label="❌ Delete", custom_id='delete_ticket')]])
            await ctx.message.channel.edit(name=f'closed-{ctx.message.channel.name}')


    #Claiming the current ticket
    @commands.command()
    async def claim(self, ctx):
        with open(os.path.dirname(__file__) + '\\..\\json\\data.json','r+') as f:
            data=json.load(f)
            if ctx.message.guild.get_role(int(data[str(ctx.message.guild.id)]["mod_roles"])) in ctx.author.roles and ctx.message.channel.category.name == 'Tickets':
                modRole=ctx.message.guild.get_role(int(data[str(ctx.message.guild.id)]["mod_roles"]))
                await ctx.message.channel.set_permissions(modRole, send_messages=False, view_channel=True)
                await ctx.message.channel.set_permissions(ctx.author, send_messages=True, view_channel=True)

                embed=discord.Embed(title='Ticket Claimed', timestamp=datetime.datetime.utcnow(), color=65535)
                embed.set_footer(icon_url= f'{ctx.author.avatar_url}', text=f'{ctx.author}')
                await ctx.send(embed=embed); f.close()
            f.close()


    # Saves a tickets transcript
    @commands.command()
    async def save(self, ctx):
        if ctx.message.channel.category.name == 'Tickets':
            with open(os.path.dirname(__file__) + f'\\..\\transcripts\\{ctx.message.channel.name}.txt', 'a') as f:
                messages = await ctx.message.channel.history().flatten()
                for msg in messages:
                    f.write(f'{msg.author}: {msg.content}  |  Sent: {msg.created_at}, Edited: {msg.edited_at}, Reactions: {msg.reactions}, ID {msg.id}, Attachments: {msg.attachments}, URL: {msg.jump_url}, Activity: {msg.activity}, Type: {msg.type}, Reference: {msg.refereence}, Guild_ID: {msg.guild.id}, Guild: {msg.guild}\n')
                f.close
            await ctx.author.send(file=discord.File(os.path.dirname(__file__) + f'\\..\\transcripts\\{ctx.message.channel.name}.txt'))
            os.remove(os.path.dirname(__file__) + f'\\..\\transcripts\\{ctx.message.channel.name}.txt')
            await ctx.respond(type=InteractionType.ChannelMessageWithSource, content=f'**Transcript Saved** {ctx.message.channel.mention}')



    # Adding a role that can view tickets to the JSON File
    @commands.command()
    @has_permissions(administrator=True)
    async def modrole(self, ctx, role : discord.Role):
        with open(os.path.dirname(__file__) + '\\..\\json\\data.json','r+') as f:
            data=json.load(f); await ctx.message.delete()
            data[str(ctx.message.guild.id)]["mod_roles"] = role.id

            category = get(ctx.message.guild.categories, name='Tickets')
            await category.set_permissions(role, send_messages=True, view_channel=True)
            f.seek(0); json.dump(data, f, indent=4); f.truncate(); f.close()
            await ctx.send(embed=discord.Embed(description=f'{ctx.author.mention} set the ticket mod role to {role.mention}', color=65535, delete_after=2))







def setup(client):
    client.add_cog(Ticket(client))
