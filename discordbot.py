import discord
import os
import random
import asyncio
import youtube_dl


# Set up downloader and opus
def ydl_hook(d):
    if d['status'] == 'finished':
        print('Downloaded')

if not discord.opus.is_loaded():
    if os.name != 'nt':
        discord.opus.load_opus('/app/lib/opus/lib/libopus.so.0.5.1')
        os.environ['PATH'] = '/app'
    else:
        discord.opus.load_opus('opus.dll')


ydl_options = {'buffer_size': 4096,
               'socket_timeout': 3,
               'retries': 20,
               'format': 'bestaudio/best',
               'postprocessors': [{
                   'key': 'FFmpegExtractAudio',
                   'preferredcodec': 'mp3'
               }],
               'progress_hooks': [ydl_hook],
               'outtmpl': '%(id)s.%(ext)s',
               'restrict_filenames': True,
               'get_filename': True
               }

yt_downloader = youtube_dl.YoutubeDL(ydl_options)

# Constants:
valid_commands = [
    '!help - Displays this help.',
    '!echo {message} - Echoes the message back.',
    '!roll {number} - Rolls an n sided dice (default 6).',
    '!flip - Flips a coin.',
    '!queue {youtube url} - Adds a youtube song to the jukebox queue.'
]

help_text = 'it seems you need help.\nFor now, these are the chat commands:\n```\n{}```'.format(
    '\n'.join(valid_commands))
coin_flips = ['Heads', 'Tails']

next_song_format = 'Now playing {0.title} from {0.requester.mention}'


# Classes:
class SongEntry:
    def __init__(self, filename, title, requester):
        self.filename = filename
        self.title = title
        self.requester = requester


class DankBot(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.song_queue = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.current = None
        self.player = None
        self.jukebox_text_channel = None
        self.setup = False

    async def song_loop(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.song_queue.get()
            try:
                self.player = self.voice.create_ffmpeg_player(self.current.filename)
                self.player.start()
                await self.send_message(self.jukebox_text_channel, next_song_format.format(self.current))
            except:  # TODO: MAKE THIS NOT STUPID
                self.goto_next_song()
                await self.send_message(self.jukebox_text_channel, 'Woops I can\'t play this song lmao.')
            await self.play_next_song.wait()

    def goto_next_song(self):
        self.loop.call_soon_threadsafe(self.play_next_song.set)

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!echo'):
            await self.send_message(message.channel, message.content[5:].strip())

        if message.content.startswith('!help'):
            await self.send_message(message.channel, '{0}, {1}'.format(message.author.mention, help_text))

        if message.content.startswith('!roll'):
            try:
                n = int(message.content[5:].strip())
            except:  # ayy lmao general exception
                n = 6
            if n > 0:
                roll = random.randint(1, n)
                await self.send_message(message.channel, 'Rolled {0}'.format(roll))

        if message.content.startswith('!flip'):
            await self.send_message(message.channel, random.choice(coin_flips))

        if message.content.startswith('!setup') and not self.setup:
            self.setup = True
            self.jukebox_text_channel = message.channel
            await self.join_voice_channel(message.author.voice_channel)
            await self.song_loop()

        if message.content.startswith('!queue') and self.setup and message.channel == self.jukebox_text_channel:
            url = message.content[6:].strip()
            with yt_downloader:
                try:
                    await self.send_message(message.channel, 'Adding song to queue.')
                    info = yt_downloader.extract_info(url, download=False)
                    filename = '{0}.mp3'.format(info.get('id', None))
                    title = info.get('title', None)
                    if not os.path.isfile(filename):
                        yt_downloader.download([url])
                    await self.song_queue.put(SongEntry(filename, title, message.author))
                except youtube_dl.DownloadError:
                    await self.send_message(message.channel, 'Failed to download song.')
                # except:
                #     raise
                #     await self.send_message(message.channel, 'Invalid URL.')

    async def on_member_join(self, member):
        server = member.server
        self.send_message(server, 'Welcome {0} to {1.name}!'.format(member.mention, server))


# Run:
bot = DankBot()
bot.run(os.environ['DISCORD_BOT_USER'], os.environ['DISCORD_BOT_PASS'])
