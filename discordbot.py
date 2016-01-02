import discord
import os
import goslate

gs = goslate.Goslate()
langs = sorted(gs.get_languages().items(), key=lambda t: t[1])

# Constants:
valid_commands = [
    '!help - Displays this help.',
    '!echo {message} - Echoes the message back.',
    '!translate {to} - Translates the message in whatever language to the chosen language.',
    '!languages - See a list of languages '
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

    if message.content.startswith('!translate'):
        parts = message.content.split(' ')
        lang = parts[1]
        content = ' '.join(parts[2:])
        client.send_message(message.channel, gs.translate(content, lang))

    if message.content.startswith('!languages'):
        client.send_message(message.channel, ', '.join(['{}: {}'.format(k, v) for (k, v) in langs]))


@client.event
def on_member_join(member):
    server = member.server
    client.send_message(server, 'Welcome {0} to {1.name}!'.format(member.mention(), server))


client.run()
