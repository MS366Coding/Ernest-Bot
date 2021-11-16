# bot.py
import asyncio
import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
import json
import requests
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.environ['BOT_TOKEN']
GUILD = os.environ['GUILD_NAME']

client = commands.Bot(command_prefix='!')

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to: \n'
        f'{guild.name}(id: {guild.id})'
        )

    await client.change_presence(activity= discord.Game("Fortnite"))

@client.event
async def on_member_join(member):
  await member.create_dm()
  await member.dm_channel.send(f"Hello {member.name}, welcome to {guild.name}!")

@client.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@client.command(name='inspire', help='Will inspire with a quote.')
async def inspire(ctx):
    response = get_quote()
    await ctx.send(response)

@client.command(name='create_channel', help='Creates a text channel.')
@commands.has_role('Admin')
async def create_channel(ctx, channel_name: str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        await ctx.send(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@client.command(name='tempmute', help='Mutes a specified member.')
@commands.has_permissions(manage_messages=True)
async def tempmute(ctx, member: discord.Member, time: int, unit: str):
    if not member:
        await ctx.send("You must mention a member to mute.")
    elif not time:
        await ctx.send("You must mention a time.")
    elif not unit:
        await ctx.send("You must mention a unit.")
    try:
        seconds = time
        duration = unit
        if duration == 's':
            seconds = seconds * 1
        elif duration == 'm':
            seconds = seconds * 60
        elif duration == 'h':
            seconds = seconds * 60 * 60
        elif duration == 'd':
            seconds = seconds * 60 * 60 * 24
        else:
            await ctx.send("Invalid time input!")
            return
    except Exception as e:
        print(e)
        await ctx.send("Invalid time input!")
        return
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name='Muted')
    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
    await member.add_roles(mutedRole)
    muted_embed = discord.Embed(title='Muted a user!', description=f'{member.mention} was muted by {ctx.author.mention} for {time}{unit}.', colour=discord.Colour.red())
    await ctx.send(embed=muted_embed)
    await asyncio.sleep(seconds)
    await member.remove_roles(mutedRole)
    unmute_embed = discord.Embed(title='Mute over!', description=f'Mute for {member.mention} by {ctx.author.mention} for {time}{unit} is over now.', colour=discord.Colour.green())
    await ctx.send(embed=unmute_embed)

@client.command(name='unmute', help="Unmutes a specified user.")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
   mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

   await member.remove_roles(mutedRole)
   await member.send(f"You have been unmuted from: - {ctx.guild.name}")
   embed = discord.Embed(title="Unmuted", description=f"{ctx.author.mention} unmuted {member.mention}.",colour=discord.Colour.green())
   await ctx.send(embed=embed)

@client.command(name='mute', description='Mutes the specified user.')
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member):
  guild = ctx.guild
  mutedRole = discord.utils.get(guild.roles, name='Muted')

  if not mutedRole:
    mutedRole = await guild.create_role(name="Muted")
    for channel in guild.channels:
      await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
  embed = discord.Embed(title="Muted", description=f"{member.mention} was muted. ", colour=discord.Colour.red())
  await ctx.send(embed=embed)
  await member.add_roles(mutedRole)
  await member.send(f" You have been muted from: {guild.name}")

keep_alive()
client.run(TOKEN)
