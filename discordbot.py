import discord
import os
import botcommands
import config
import time


class DankBot(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.conversations = {}
        self.start_time = time.time()

    async def on_message(self, message):
        author_id = message.author.id

        if author_id == self.user.id:
            return

        if message.content.startswith(config.prefix):
            admin = author_id in config.admins
            await botcommands.command(self, message, admin)
        elif author_id in self.conversations and self.conversations[author_id].channel == message.channel:
            await self.send_message(message.channel, self.conversations[author_id].session.think(message.content))

    async def on_member_join(self, member):
        server = member.server
        self.send_message(server, 'Welcome {0} to {1.name}!'.format(member.mention, server))


if __name__ == '__main__':
    # Run:
    bot = DankBot()
    bot.run(os.environ['DISCORD_BOT_USER'], os.environ['DISCORD_BOT_PASS'])
