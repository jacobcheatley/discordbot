import discord
import os
import asyncio
import botcommands
import config

# Set up downloader and opus
if not discord.opus.is_loaded():
    if os.name != 'nt':
        discord.opus.load_opus('/app/lib/opus/lib/libopus.so.0.5.1')
    else:
        discord.opus.load_opus('opus.dll')


class DankBot(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.song_queue = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.current = None
        self.player = None
        self.jukebox_text_channel = None
        self.setup_done = False

    async def on_message(self, message):
        if message.author.id == self.user.id or not message.content.startswith(config.prefix):
            return

        admin = message.author.id in config.admins

        await botcommands.command(self, message, admin)

    async def on_member_join(self, member):
        server = member.server
        self.send_message(server, 'Welcome {0} to {1.name}!'.format(member.mention, server))


# Run:
bot = DankBot()
bot.run(os.environ['DISCORD_BOT_USER'], os.environ['DISCORD_BOT_PASS'])
