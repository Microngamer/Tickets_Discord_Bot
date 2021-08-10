import discord, os, json
from discord.ext import commands
from discord.ext.commands import CommandNotFound, CommandInvokeError
import datetime as datetime
from discord_components import *

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix='=', intents=intents)
client.remove_command('help')


@client.event
async def on_ready():
    DiscordComponents(client)
    print(f'Launched: {client.user.name} // {client.user.id}')

@client.command(description="Loads an extention")
@commands.has_permissions(administrator=True)
async def load(ctx, extention):
    client.load_extension(f'cogs.{extention}')
    await ctx.send(f"**Loaded {extention}**", delete_after=2)

@client.command(description="Unloads an extention")
@commands.has_permissions(administrator=True)
async def unload(ctx, extention):
    client.unload_extension(f'cogs.{extention}')
    await ctx.send(f"**Unloaded {extention}**", delete_after=2)

@client.command(description="Reloads an extention")
@commands.has_permissions(administrator=True)
async def reload(ctx, extention):
    client.unload_extension(f'cogs.{extention}')
    client.load_extension(f'cogs.{extention}')
    await ctx.send(f"**Reloaded {extention}**", delete_after=2)

for filename in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cogs')):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(f'Loaded: cog.{filename[:-3]}')



@client.command()
async def help(ctx):
    embed=discord.Embed(title='Ticket Commands', color=65535, timestamp=datetime.datetime.utcnow())
    embed.add_field(name='Save Transcript', value='Saves the ticket transcript\n*=save*', inline=True)
    embed.add_field(name='Claim Ticket [Mod+]', value='Claims the ticket\n*=claim*', inline=True)
    embed.add_field(name='Close Ticket [Mod+]', value='Closes the ticket\n*=close*', inline=True)
    embed.add_field(name='‏‏‎ ‎\nDelete Ticket [Mod+]', value='Deletes the ticket\n*=delete*', inline=True)
    embed.add_field(name=' ‎\nAdd User [Mod+]', value='Adds an user to the ticket\n*=add @user*', inline=True)
    embed.add_field(name=' ‎\nRemove User [Mod+]', value='Removes an user from the ticket\n*=remove @user*', inline=True)
    embed.add_field(name=' ‎\nSet Mod Role [Admin+]', value='Sets the ticket mod role\n*=modrole @role*', inline=True)
    embed.add_field(name=' ‎\nSetup [Admin+]', value='Sets up the bot\n*=setup @role*', inline=True)
    embed.set_footer(icon_url= f'{ctx.author.avatar_url}', text=f'{ctx.author}')
    await ctx.send(embed=embed)




client.run('YOUR TOKEN')
