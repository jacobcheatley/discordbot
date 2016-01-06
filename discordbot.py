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
        self.active = True
        self.limited_users = set()

    async def on_message(self, message):
        author_id = message.author.id
        admin = author_id in config.admins

        if author_id == self.user.id or (not admin and not self.active) or author_id in self.limited_users:
            return

        if message.content.startswith(config.prefix):
            await botcommands.command(message, admin)
        elif author_id in self.conversations and self.conversations[author_id].channel == message.channel:
            if self.conversations[author_id].last_message_time + config.convo_time_out < time.time():
                # Timed out
                self.conversations.pop(author_id)
            else:
                # Not timed out
                self.conversations[author_id].last_message_time = time.time()
                await self.send_message(message.channel, self.conversations[author_id].session.think(message.content))

    async def on_member_join(self, member):
        server = member.server
        self.send_message(server, 'Welcome {0} to {1.name}!'.format(member.mention, server))


if __name__ == '__main__':
    # Run:
    bot = DankBot()
    botcommands.bot = bot
    bot.run(os.environ['DISCORD_BOT_USER'], os.environ['DISCORD_BOT_PASS'])
