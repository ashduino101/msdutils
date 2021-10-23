import datetime

import io
import json
import csv

import os
import pathlib

import time

from PIL import Image, ImageDraw, ImageFont
import numpy as np

import urllib
from urllib.request import urlretrieve
import requests
import urllib.request

from discord.ext import commands
from discord.ext.commands import MissingPermissions
import discord

from mcstatus import MinecraftBedrockServer
from mcstatus import MinecraftServer
import mcrcon

import asyncio
import asyncpraw

import random

from termcolor import colored as col

from urllib.request import urlopen
import urllib.request
from urllib.error import *
import validators

import contextlib

import youtube_dl

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '/youtube/song.webm',
}

with open("config.json") as f:
    configfile = json.load(f)
    token = configfile["token"]
    rcon_password = configfile['rcon_password']

rconhost = '10.0.0.78'
rconport = 25560

channels = []
channelnames = []

hosts = ['https://www.mukilteoschools.org',
         'http://www.mukilteo.wednet.edu',
         'http://mail.mukilteo.wednet.edu',
         'http://camano.mukilteo.wednet.edu',
         'http://ckf01.mukilteo.wednet.edu',
         'http://ckf02.mukilteo.wednet.edu',
         'http://staff.mukilteo.wednet.edu',
         'http://library.mukilteo.wednet.edu',
         'http://printcenter.mukilteo.wednet.edu',
         'http://busroutes.mukilteo.wednet.edu',
         'http://sts.mukilteo.wednet.edu',
         'https://mediaportal.mukilteo.wednet.edu',
         'http://da.mukilteo.wednet.edu',
         'http://autodiscover.mukilteo.wednet.edu',
         'http://clipper.mukilteo.wednet.edu',
         'http://edger.mukilteo.wednet.edu',
         'http://info.mukilteo.wednet.edu'
         ]

intents = discord.Intents.all()
client = commands.Bot(command_prefix='?', intents=intents)
client.remove_command('help')


@client.event
async def on_ready():
    print('The bot is now online as {0.user}.'.format(client))
    for guild in client.guilds:
        for channel in guild.text_channels:
            channels.append(channel.id)
            channelnames.append(channel)
    with open('server_index.txt', 'w+') as index:
        index.writelines(str(channels))
        index.close()
    with io.open('server_index_names.txt', mode='w+', encoding='utf-8') as cnames:
        cnames.writelines(str(channelnames))
        cnames.close()
    client.loop.create_task(status())


@client.event
async def on_message(ctx):
    # mainly for future message statistics, I should really optimize this shouldn't I
    if ctx.attachments:
        log = io.open('message_data.csv', mode='a+', encoding='utf-8')
        writer = csv.writer(log)
        writer.writerow([ctx.content, ctx.id, ctx.channel, ctx.channel.id, time.time()])
        log.close()
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        ext = ctx.attachments[0].url.split('.')[(len(ctx.attachments[0].url.split('.'))) - 1]
        if not os.path.isdir(os.path.join('D:\Programming Stuff\MSD Bot\media\%s' % ctx.channel)):
            os.makedirs(os.path.join('D:\Programming Stuff\MSD Bot\media\%s' % ctx.channel))
        urlretrieve(ctx.attachments[0].url,
                    os.path.join('D:\Programming Stuff\MSD Bot\media\%s' % ctx.channel, (str(ctx.id) + '.' + ext)))
    else:
        log = io.open('message_data.csv', mode='a+', encoding='utf-8')
        writer = csv.writer(log)
        writer.writerow([ctx.content, ctx.id, ctx.channel, ctx.channel.id, time.time()])
        log.close()
    global removemode, op

    if ctx.channel.id != 837392579884482601:
        # print(ctx.content)
        if 'discord.gg' in ctx.content and ctx.author.id != 650900479663931413:
            await ctx.delete()
            embed = discord.Embed(title='Link Remover',
                                  description=(
                                          'A link by %s was removed for containing a Discord server invite.' % ctx.author),
                                  color=0xFF0000)
            embed.set_footer(text='Bot made by ashduino101')
            await ctx.channel.send(embed=embed)
            logchannel = client.get_channel(888941416921829426)
            logembed = discord.Embed(title='Link Removed', description=(
                    'A message by %s was removed from %s for containing a Discord server invite.' % (
                ctx.author, ('<#' + str(ctx.channel.id) + '>'))), color=0xFF0000)
            logembed.add_field(name='Offending Message:', value=ctx.content)
            logembed.set_footer(text='Bot made by ashduino101')
            await logchannel.send(embed=logembed)
    await client.process_commands(ctx)


# Modified version of https://stackoverflow.com/questions/32504246/draw-ellipse-in-python-pil-with-line-thickness
def draw_ellipse(image, bounds, width=1, outline='white', antialias=4):
    mask = Image.new(
        size=[int(dim * antialias) for dim in image.size],
        mode='L', color='black')
    draw = ImageDraw.Draw(mask)
    for offset, fill in (width / -2.0, 'white'), (width / 2.0, 'black'):
        left, top = [(value + offset) * antialias for value in bounds[:2]]
        right, bottom = [(value - offset) * antialias for value in bounds[2:]]
        draw.ellipse([left, top, right, bottom], fill=fill)
    mask = mask.resize(image.size, Image.LANCZOS)
    image.paste(outline, mask=mask)


@client.event
async def on_member_join(member):
    await member.avatar_url_as(format="png").save(fp=(".\\avatars\\%s.png" % member.id))
    img = Image.open(".\\avatars\\%s.png" % member.id).convert('RGB')
    npImage = np.array(img)
    h, w = img.size
    alpha = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(alpha)
    draw.pieslice([0, 0, h, w], 0, 360, fill=255)
    npAlpha = np.array(alpha)
    npImage = np.dstack((npImage, npAlpha))
    newsize = 240, 240
    background = Image.open('.\\assets\\banner%d.jpg' % random.randint(1, 11))
    foreground = (Image.fromarray(npImage)).resize(newsize)
    foreground.save('.\\avatars\\%s.png' % member.id)
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype(".\\font.ttf", 64)
    draw.text((260, 0), ('Welcome, ' + member.name), (255, 255, 255), font=font)
    draw.text((260, 70), ('Member #' + str((client.get_guild(836698659071590452)).member_count)), (255, 255, 255),
              font=font)
    background.paste(foreground, (0, 0), foreground)
    ellipse_box = [0, 0, 240, 240]
    draw_ellipse(background, ellipse_box, width=10, outline='gray')
    background.save('.\\banners\\%s.png' % member.id)
    with open('.\\banners\\%s.png' % member.id, 'rb') as b:
        with open('./config/%s.json' % member.guild.id, 'r') as c:
            banner = discord.File(b)
            channel = (json.load(c))['welcome']
            print(channel)
            wc = client.get_channel(int(channel))
            await wc.send(f'Hey <@{member.id}>, welcome to **{member.guild.name}**!', file=banner)


@client.event
async def on_member_leave(member):
    with open('./config/%s.json' % member.guild.id, 'r') as c:
        channel = (json.load(c))['welcome']
        wc = client.get_channel(int(channel))
        await wc.send(f'Goodbye, {member.id}!')


@client.command(name='help')
async def help(ctx):
    helpembed = discord.Embed(title='Help', description='Help for MSD Utilities', color=0x005780)
    helpembed.add_field(name='?help <command>', value='Shows the usage of a command.')
    helpembed.add_field(name='?commands', value='Lists all commands.')
    helpembed.set_footer(text='Bot made by ashduino101 (HPMS)')
    await ctx.message.channel.send(embed=helpembed)
    if ctx.message.content.endswith('config'):
        usageembed = discord.Embed(title='Help', description='Help for MSD Utilities', color=0x005780)
        usageembed.add_field(name='?config <command> <params>',
                             value='Configures a command. Use ?configs to display list of configurable commands.')
        usageembed.set_footer(text='Bot made by ashduino101')
        await ctx.message.channel.send(embed=usageembed)
    if ctx.message.content.endswith('configs'):
        usageembed = discord.Embed(title='Help', description='Help for MSD Utilities', color=0x005780)
        usageembed.add_field(name='?config <command> <params>',
                             value='Displays list of configurable commands and their parameters.')
        usageembed.set_footer(text='Bot made by ashduino101')
        await ctx.message.channel.send(embed=usageembed)
    if ctx.message.content.endswith('commands'):
        cmdembed = discord.Embed(title='Commands', description='List of commands.', color=0x005780)
        cmdembed.add_field(name='?config', value='Configures a command.')
        cmdembed.add_field(name='?help [command]', value='Displays usage of command, leave empty for base commands.',
                           inline=True)
        cmdembed.add_field(name='?membercount', value='Displays amount of users in server.')
        cmdembed.set_footer(text='Bot made by ashduino101')
        await ctx.message.channel.send(embed=cmdembed)


@client.command(name='config')
async def config(ctx, command, arg3, arg4=None):
    if command == 'linkremover':
        lremove_conf = str(arg3)
        try:
            with open(f'./config/{ctx.guild.id}.json', 'a+') as lc:
                if lremove_conf[2].isdigit():
                    lc.writelines(lremove_conf[2] + ' ')
                elif lremove_conf[2] == 'whitelist':
                    await ctx.message.channel.send('Link removal channel mode changed to whitelist.')
                elif lremove_conf[2] == 'blacklist':
                    await ctx.message.channel.send('Link removal channel mode changed to blacklist.')
                    removemode = 'blacklist'
                else:
                    await ctx.message.channel.send('Invalid parameter! (%s)' % lremove_conf[2])
                lc.close()
        except IndexError:
            await ctx.message.channel.send('Missing parameter in %s!' % ctx.message.content)
    if command == 'welcomes':
        with open('./config/%s.json' % ctx.message.guild.id, 'w+') as c:
            cf = json.load(c)
            for element in cf:
                if 'welcome' in element:
                    del element['welcome']
            json.dump({'welcome': arg3}, cf)
            await ctx.send('Configuration successfully updated.')


@client.command(name='membercount')
async def membercount(ctx):
    await ctx.message.channel.send(
        'There are %d members in this server.' % (client.get_guild(ctx.guild.id)).member_count)


@client.command(name='mc')
async def mc(ctx):
    mcembed = discord.Embed(title='Minecraft Server Status',
                            description='Status for the unofficial MSD Minecraft servers', color=0x11FF08)
    server = MinecraftServer.lookup('73.193.8.144:25565')
    server2 = MinecraftServer.lookup('73.193.8.144:25564')
    server3 = MinecraftServer.lookup('73.193.8.144:25563')
    status = None
    status2 = None
    status3 = None
    try:
        status = server.status()
    except:
        await ctx.send("Error getting status of vanilla server.")
    try:
        status2 = server2.status()
    except:
        await ctx.send("Error getting status of creative server.")
    try:
        status3 = server3.status()
    except:
        await ctx.send("Error getting status of custom terrain server.")
    try:
        mcembed.add_field(name='**Vanilla Server**', value="Status of the vanilla survival server.", inline=False)
        mcembed.add_field(name='Ping', value=str(server.ping()))
        mcembed.add_field(name='Online Players', value=status.players.online)
        mcembed.add_field(name='Max Players', value=status.players.max)
        mcembed.add_field(name='IP', value=server.host)
        mcembed.add_field(name='Port', value=str(server.port))
        mcembed.add_field(name='Version', value=status.version.name)
        mcembed.add_field(name='Latency', value=str(status.latency))
    except:
        await ctx.message.channel.send('Timed out while pinging vanilla server.')
    try:
        mcembed.add_field(name='**Creative Server**', value="Status of the creative testing server.", inline=False)
        mcembed.add_field(name='Ping', value=str(server2.ping()))
        mcembed.add_field(name='Online Players', value=status2.players.online)
        mcembed.add_field(name='Max Players', value=status2.players.max)
        mcembed.add_field(name='IP', value=server2.host)
        mcembed.add_field(name='Port', value=str(server2.port))
        mcembed.add_field(name='Version', value=status2.version.name)
        mcembed.add_field(name='Latency', value=str(status2.latency))
    except:
        await ctx.message.channel.send('Timed out while pinging creative server.')
    try:
        mcembed.add_field(name='**Custom Terrain Server**', value="Status of the custom terrain survival server.",
                          inline=False)
        mcembed.add_field(name='Ping', value=str(server3.ping()))
        mcembed.add_field(name='Online Players', value=status3.players.online)
        mcembed.add_field(name='Max Players', value=status3.players.max)
        mcembed.add_field(name='IP', value=server3.host)
        mcembed.add_field(name='Port', value=str(server3.port))

        mcembed.add_field(name='Version', value=status3.version.name)
        mcembed.add_field(name='Latency', value=str(status3.latency))
    except:
        await ctx.message.channel.send('Timed out while pinging custom terrain server.')
    try:
        await ctx.message.channel.send(embed=mcembed)
    except:
        await ctx.message.channel.send("There was an error getting the statuses. This could mean all servers are down.")


@client.command(name='eval')
async def pyeval(ctx):
    if ctx.message.author.id == 650900479663931413:
        print(col('An eval task was attempted by', 'cyan'), col(ctx.message.author, 'magenta') + col('.', 'cyan'))
        try:
            await ctx.message.channel.send('Eval job started...')
            with contextlib.redirect_stdout(io.StringIO()) as out:
                exec(ctx.message.content.replace('?eval ', ''))
                await ctx.message.channel.send(out.getvalue())
        except BaseException as err:
            await ctx.message.channel.send('An error occurred during eval job: ' + str(err))
        await ctx.message.channel.send('Eval job completed.')


@client.command(name='channelcount')
async def channelcount(ctx):
    guild = client.get_guild(ctx.guild.id)
    count = 0
    for _ in guild.channels:
        count += 1
    # print(count)
    await ctx.message.channel.send('This server has %d channels.' % count)


@client.command(name='reddit')
async def reddit(ctx, subreddit):
    with open("config.json") as f:
        configfile = json.load(f)
        secret = configfile["reddit_secret"]
        f.close()
    reddit = asyncpraw.Reddit(
        client_id="u0gfGRNvbT3TFRb_3I4lKw",
        client_secret=secret,
        user_agent="Subreddit Post Fetcher",
    )
    realsub = await reddit.subreddit(subreddit)
    submission = await realsub.random()
    if submission.is_self:
        reddit_embed = discord.Embed(title=('Reddit Post (r/%s)' % subreddit),
                                     description=('Reddit post requested by %s.' % ctx.author), color=0xfa6b11)
        if ((len(submission.selftext)) > 1024) or ((len(submission.selftext)) == 0):
            reddit_embed.add_field(name=submission.title, value=(((submission.selftext)[:1020]) + '...'))
        else:
            reddit_embed.add_field(name=submission.title, value=submission.selftext)
        reddit_embed.set_footer(text=submission.shortlink)
        await ctx.message.channel.send(embed=reddit_embed)
    else:
        if submission.over_18 and not ctx.message.channel.is_nsfw():
            nsfw_warning = discord.Embed(title='Warning',
                                         description='This post is marked as NSFW and is only available in NSFW channels.',
                                         color=0xFF0000)
            await ctx.message.channel.send(embed=nsfw_warning)
        else:
            reddit_embed = discord.Embed(title=('Reddit Post (r/%s)' % subreddit),
                                         description=('Reddit post requested by %s.' % ctx.author), color=0xfa6b11)
            reddit_embed.add_field(name=submission.title, value=submission.shortlink)
            reddit_embed.set_image(url=submission.preview['images'][0]['resolutions'][
                (len(submission.preview['images'][0]['resolutions']) - 1)]['url'])
            reddit_embed.set_footer(text=submission.shortlink)
            await ctx.message.channel.send(embed=reddit_embed)


async def status():
    with open('config.json') as cfg:
        statuses = json.load(cfg)
        while True:
            i = random.randint(0, 1)
            # print(i)
            if i == 0:
                await client.change_presence(activity=discord.Game(name=((statuses["playing"])[random.randint(0, 11)])))
            if i == 1:
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=(
                (statuses["watching"])[random.randint(0, 7)])))
            print(col('The status has been updated.', 'cyan'))
            await asyncio.sleep(60)


@client.command(name='info')
async def info(ctx, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None, arg8=None, arg9=None,
               arg10=None):
    d = open('userdata.csv', 'r+')
    writer = csv.writer(d, delimiter=',', quotechar='!', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10, ctx.message.author.id])
    d.close()


@client.command(name='msdstatus')
async def msdstatus(ctx):
    print(ctx)
    msd_embed = discord.Embed(title='MSD Domain Statuses', description='Status for all MSD domains.',
                              timestamp=(datetime.datetime.now()), color=0x005780)
    m_id = await ctx.message.channel.send('Scan started...')
    print(m_id.id)
    msg = await ctx.message.channel.fetch_message(m_id.id)
    for iteration, item in enumerate(hosts):
        await m_id.edit(content=('Scanning %s... (Item %s of %s)' % (item, iteration + 1, len(hosts) + 1)))
        try:
            html = urlopen(item)
        except HTTPError as e:
            page_status = ':yellow_circle: Likely Online (%s)' % e
        except URLError:
            page_status = ':red_circle: Offline'
        except ValueError as e:
            page_status = ':black_circle: N/A: Host not found (%s)' % e
        else:
            page_status = ':green_circle: Online'
        await m_id.edit(content=('Scanned ' + item))
        msd_embed.add_field(name=item, value=page_status)
    msd_embed.set_footer(text='Subdomain missing? DM this bot with the URL of the missing page.')
    await msg.delete()
    await ctx.message.channel.send(embed=msd_embed)


"""
@client.command(name='activitygraph')
async def graph():
    with open('message_data.csv', 'r') as c:
        reader = csv.reader(c)
        c.
        """


@client.command(name='rcon')
@commands.has_any_role('moderator', 'Admin', 'tech support')
async def rcon(ctx, action=None, args=None, args2=None):
    if action == 'command':
        with mcrcon.MCRcon(host=rconhost, port=25560, password=rcon_password) as mcr:
            resp = mcr.command(args)
            try:
                await ctx.send(resp)
            except discord.HTTPException:
                await ctx.send("Operation completed successfully.")
    else:
        if action is not None:
            await ctx.message.channel.send('Specified arguments are not valid. Please use "rcon <action> [args]".')
        else:
            await ctx.message.channel.send('Please provide one or more arguments.')


"""
@rcon.error
async def rcon_permission_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.message.channel.send('You do not have required permission to run this command!')
"""

global vc


@client.command(name='play')
async def play_song(ctx, url):
    global vc_client
    voice_state = ctx.message.author.voice
    if voice_state is None:
        return await ctx.message.channel.send('You must be in a voice channel to use this command!')
    user = ctx.message.author
    voice_channel = user.voice.channel
    if not ctx.voice_client:
        vc = await voice_channel.connect()
    if validators.url(url):
        try:
            os.remove('./youtube/song.webm')
        except:
            pass
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    vc_client = vc.play(discord.FFmpegPCMAudio(executable='C:/ffmpeg/bin/ffmpeg.exe',
                                               source='./youtube/song.webm'),
                        after=lambda e: print('done', e))
    print(vc_client)
    if vc.is_playing():
        await ctx.message.channel.send('Now playing %s as requested by %s.' % (url, ctx.message.author))


@client.command(name='stop')
async def stopplayer(ctx):
    await ctx.voice_client.stop()


@client.command(name='disconnect')
async def disconnect(ctx):
    await ctx.voice_client.disconnect()


@client.command(name='meme')
async def meme(ctx):
    await reddit(ctx, 'memes')


client.run(token)
