import discord
import os

# Constants:
valid_commands = [
    '!help - Displays this help.',
    '!echo {message} - Echoes the message back.'
]

help_text = ', it seems you need help.\nFor now, these are the chat commands:\n```\n{}```'.format('\n'.join(valid_commands))

client = discord.Client()
client.login(os.environ['DISCORD_BOT_USER'], os.environ['DISCORD_BOT_PASS'])


@client.event
def on_ready():
    print('Connected!')
    print(client.user.name, client.user.id)


@client.event
def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!echo'):
        client.send_message(message.channel, message.content[6:])

    if message.content.startswith('!help'):
        client.send_message(message.channel, message.author.mention() + help_text)


@client.event
def on_member_join(member):
    server = member.server
    client.send_message(server, 'Welcome {0} to {1.name}!'.format(member.mention(), server))


client.run()
