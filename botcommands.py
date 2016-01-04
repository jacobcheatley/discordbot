import random
import os
import youtube_dl
import config
from collections import OrderedDict
from chatterbotapi import ChatterBotFactory, ChatterBotType
import time
import discord.utils

# Constants:
ydl_options = {'buffer_size': 4096,
               'socket_timeout': 3,
               'retries': 20,
               'format': 'bestaudio/best',
               'postprocessors': [{
                   'key': 'FFmpegExtractAudio',
                   'preferredcodec': 'mp3'
               }],
               'outtmpl': '%(id)s.%(ext)s',
               'restrict_filenames': True,
               'get_filename': True
               }
yt_downloader = youtube_dl.YoutubeDL(ydl_options)
next_song_format = 'Now playing {0.title} from {0.requester.mention}'
factory = ChatterBotFactory()


class CommandInfo:
    def __init__(self, func, args, docs):
        self.func = func
        self.args = args
        self.docs = docs

    def __str__(self):
        return '{0}- {1}'.format('' if self.args == '' else self.args + ' ', self.docs)


class BotConversationInfo:
    def __init__(self, session, channel):
        self.session = session
        self.channel = channel


def help_text(author):
    commands_display = '\n'.join(
        ['{0}{1} {2}'.format(config.prefix, key, str(value)) for (key, value) in commands.items()])
    return '{0}, it seems you need help.\nFor now, these are the chat commands:\n```\n{1}```'.format(author.mention,
                                                                                                     commands_display)


async def help_disp(bot=None, message=None, args=None):
    await bot.send_message(message.channel, help_text(message.author))


async def whomai(bot=None, message=None, args=None):
    await bot.send_message(message.channel, message.author.id)


async def echo(bot=None, message=None, args=None):
    try:
        await bot.send_message(message.channel, ' '.join(args[1:]))
    except IndexError:
        pass


async def roll(bot=None, message=None, args=None):
    try:
        n = int(args[1])
    except:  # ayy lmao general exception
        n = 6
    if n > 0:
        roll = random.randint(1, n)
        await bot.send_message(message.channel, 'Rolled {0}'.format(roll))


async def flip(bot=None, message=None, args=None):
    await bot.send_message(message.channel, random.choice(['Heads', 'Tails']))


async def eightball(bot=None, message=None, args=None):
    await bot.send_message(message.channel, random.choice([
        'It is certain',
        'It is decidedly so',
        'Without a doubt',
        'Yes, definitely',
        'You may rely on it',
        'As I see it, yes',
        'Most likely',
        'Outlook good',
        'Yes',
        'Signs point to yes',
        'Reply hazy try again',
        'Ask again later',
        'Better not tell you now',
        'Cannot predict now',
        'Concentrate and ask again',
        'Don\'t count on it',
        'My reply is no',
        'My sources say no',
        'Outlook not so good',
        'Very doubtful'
    ]))


async def start_convo(bot=None, message=None, args=None):
    if message.author.id in bot.conversations:
        return
    await bot.send_message(message.channel, 'Starting a conversation with {}.'.format(message.author.mention))
    chatter_bot = factory.create(ChatterBotType.CLEVERBOT)
    chatter_bot_session = chatter_bot.create_session()
    bot.conversations[message.author.id] = BotConversationInfo(chatter_bot_session, message.channel)


async def end_convo(bot=None, message=None, args=None):
    if message.author.id not in bot.conversations:
        return
    await bot.send_message(message.channel, 'Ending a conversation with {}.'.format(message.author.mention))
    bot.conversations.pop(message.author.id)


async def uptime(bot=None, message=None, args=None):
    seconds = int(time.time() - bot.start_time)
    days = seconds // 86400
    seconds -= days * 86400
    hours = seconds // 3600
    seconds -= hours * 3600
    minutes = seconds // 60
    seconds -= minutes * 60
    time_display = '{0}{1}{2}{3}'.format('' if days == 0 else str(days) + ' days, ',
                                         '' if hours == 0 else str(hours) + ' hours, ',
                                         '' if minutes == 0 else str(minutes) + ' minutes, ',
                                         str(seconds) + ' seconds.')
    await bot.send_message(message.channel, 'Bot has been up for ' + time_display)


async def clear(bot=None, message=None, args=None):
    try:
        n = int(args[1])
    except:
        n = 10
    logs = await bot.logs_from(message.channel)
    deleted = 0
    for message in logs:
        if deleted > n:
            return
        if message.author.id == bot.user.id:
            deleted += 1
            await bot.delete_message(message)

# region Old Audio
# class SongEntry:
#     def __init__(self, filename, title, requester):
#         self.filename = filename
#         self.title = title
#         self.requester = requester
#
#
# async def setup(bot=None, message=None, admin=False, args=None):
#     if admin and not bot.setup_done:
#         bot.setup_done = True
#         bot.jukebox_text_channel = message.channel
#         await bot.join_voice_channel(message.author.voice_channel)
#         await song_loop(bot)
#
#
# async def queue(bot=None, message=None, admin=False, args=None):
#     if not bot.setup_done:
#         return
#
#     try:
#         url = args[1].split('&')[0]
#         with yt_downloader:
#             try:
#                 await bot.send_message(message.channel, 'Adding song to queue.')
#                 info = yt_downloader.extract_info(url, download=False)
#                 filename = '{0}.mp3'.format(info.get('id', None))
#                 title = info.get('title', None)
#                 if not os.path.isfile(filename):
#                     yt_downloader.download([url])
#                 await bot.song_queue.put(SongEntry(filename, title, message.author))
#             except youtube_dl.DownloadError:
#                 await bot.send_message(message.channel, 'Failed to download song.')
#     except IndexError:
#         pass
#
#
# async def song_loop(bot):
#     while True:
#         bot.play_next_song.clear()
#         bot.current = await bot.song_queue.get()
#         try:
#             bot.player = bot.voice.create_ffmpeg_player(bot.current.filename, after=goto_next_song(bot))
#             await bot.send_message(bot.jukebox_text_channel, next_song_format.format(bot.current))
#             bot.player.start()
#         except:  # TODO: MAKE THIS NOT STUPID
#             goto_next_song(bot)
#             await bot.send_message(bot.jukebox_text_channel, 'Woops I can\'t play this song lmao.')
#         await bot.play_next_song.wait()
#
#
# def goto_next_song(bot):
#     bot.loop.call_soon_threadsafe(bot.play_next_song.set)
# endregion

commands = OrderedDict([
    ('help', CommandInfo(help_disp, '', 'Displays this help text.')),
    ('whoami', CommandInfo(whomai, '', 'Gives your user ID.')),
    ('echo', CommandInfo(echo, '{message}', 'Echoes the message back.')),
    ('roll', CommandInfo(roll, '{number}', 'Rolls an n sided die (default 6).')),
    ('flip', CommandInfo(flip, '', 'Flips a coin.')),
    ('8ball', CommandInfo(eightball, '{query}', 'The Magic 8 Ball has the answers to all questions.')),
    ('uptime', CommandInfo(uptime, '', 'Displays bot uptime.')),
    ('startconversation', CommandInfo(start_convo, '', 'Starts a conversation with the bot.')),
    ('endconversation', CommandInfo(end_convo, '', 'Ends your conversation with the bot.')),
    # ('queue', CommandInfo(queue, '{youtube url}', 'Adds a YouTube song to the Jukebox queue.')),
    # ('setup', CommandInfo(setup, '', 'Sets up the Jukebox, admin only.'))
])

admin_commands = OrderedDict([
    ('clear', CommandInfo(clear, '{number}', 'Clears n bot messages in channel.')),
])

async def command(bot, message, admin):
    args = message.content.replace(config.prefix, '', 1).split(' ')
    admin_command_info = admin_commands.get(args[0], None) if admin else None
    command_info = commands.get(args[0], None)

    if admin_command_info is not None:
        await admin_command_info.func(bot=bot, message=message, args=args)
    elif command_info is not None:
        await command_info.func(bot=bot, message=message, args=args)
