import random
import config
from collections import OrderedDict
from chatterbotapi import ChatterBotFactory, ChatterBotType
import time
import re
import wolframalpha
import os

factory = ChatterBotFactory()
wolfram_client = wolframalpha.Client(os.environ['WOLFRAM_ID'])
bot = None


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
        self.last_message_time = time.time()


# region User
def help_text(author, command_dict):
    commands_display = '\n'.join(
        ['{0}{1} {2}'.format(config.prefix, key, str(value)) for (key, value) in command_dict.items()])
    return '{0}, it seems you need help.\nFor now, these are the chat commands:\n```\n{1}```'.format(author.mention,
                                                                                                     commands_display)


async def help_disp(message=None, args=None):
    await bot.send_message(message.channel, help_text(message.author, commands))


def user_info(member):
    return 'Info about {0.name} ({0.status}):\n' \
           'ID: {0.id}\n' \
           'Joined at: {0.joined_at}\n' \
           'Roles: {1}'.format(member, ', '.join(str(role) for role in member.roles[1:]))


async def whoami(message=None, args=None):
    await bot.send_message(message.channel, user_info(message.author))


async def whois(message=None, args=None):
    await bot.send_message(message.channel, user_info(message.mentions[0]))


async def echo(message=None, args=None):
    try:
        await bot.send_message(message.channel, ' '.join(args[1:]))
    except IndexError:
        pass


async def roll(message=None, args=None):
    dice_string = message.content[6:].replace(' ', '')
    dice_pattern = r"^(\d*)d(\d+)(?:(\+|-)(\d+))?"
    try:
        num_dice, size, sign, mod = re.findall(dice_pattern, dice_string)[0]
        dice_roll = sum((random.randint(1 if int(size) else 0, int(size)) for _ in range(int(num_dice or 1))))
        constant = eval('{}{}'.format(sign, mod)) if mod else 0
        await bot.send_message(message.channel, 'Rolled {} = {}'.format(num_dice + 'd' + size + sign + mod, dice_roll + constant))
    except Exception as e:
        print(e)
        await bot.send_message(message.channel, 'Invalid dice format (NdX+C)')


async def flip(message=None, args=None):
    await bot.send_message(message.channel, random.choice(['Heads', 'Tails']))


async def eightball(message=None, args=None):
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


async def start_convo(message=None, args=None):
    if message.author.id in bot.conversations:
        return
    await bot.send_message(message.channel, 'Starting a conversation with {}.'.format(message.author.mention))
    chatter_bot = factory.create(ChatterBotType.CLEVERBOT)
    chatter_bot_session = chatter_bot.create_session()
    bot.conversations[message.author.id] = BotConversationInfo(chatter_bot_session, message.channel)


async def end_convo(message=None, args=None):
    if message.author.id not in bot.conversations:
        return
    await bot.send_message(message.channel, 'Ending a conversation with {}.'.format(message.author.mention))
    bot.conversations.pop(message.author.id)


async def uptime(message=None, args=None):
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


async def lenny(message=None, args=None):
    lennies = ['( ͡° ͜ʖ ͡°)', '\\\\(ꗞ ͟ʖꗞ)/', '(ง⍤□⍤)ง', '[x╭╮x]', '(⚆ ͜ʖ⚆)', '\\\\( º  ͟ʖ º )/', '(  つ ಠ ڡ ಠ C )',
               '( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)', '┬┴┬┴┤ ͜ʖ ͡°) ├┬┴┬┴', '( ͡°╭͜ʖ╮͡° )',
               '[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]', '/╲/\\\\╭( ͡° ͡° ͜ʖ ͡° ͡°)╮/\\\\╱\\\\', '༼ つ  ͡° ͜ʖ ͡° ༽つ', '( ͡ᵔ ͜ʖ ͡ᵔ )',
               '( ಠ ͜ʖರೃ)', '\\\\( ͠°ᗝ °)/', '( ͠°╭͜ʖ╮ °)', '\\\\( ͠° ͜ʖ °)/', '( ͡°ᴥ ͡°)', '( ͡° ͟ʖ ͡°)', '乁(૦ઁ╭͜ʖ╮૦ઁ)ㄏ',
               '乁(๏‿‿๏)ㄏ', '(⌐■ ͜ʖ■)', '($ ͜ʖ$)', '\\\\(ಠ_ಠ)/']
    try:
        lenny_num = int(args[1])
        try:
            await bot.send_message(message.channel, lennies[lenny_num - 1])
        except IndexError:
            await bot.send_message(message.channel, 'Number out of range (1-{}).'.format(len(lennies)))
    except IndexError:
        if random.random() < 0.25:
            await bot.send_message(message.channel, lennies[0])
        else:
            await bot.send_message(message.channel, random.choice(lennies[1:]))
    except ValueError:
        await bot.send_message(message.channel, 'Not a valid integer.')


async def wolfram(message=None, args=None):
    if message.channel.name in config.allowed_spam_channels:
        query_string = message.content[9:]
        result = wolfram_client.query(query_string)
        pod_texts = []
        for pod in result.pods:
            pod_texts.append('**{0.title}**\n{0.img}'.format(pod))
        await send_long(message.channel, '\n'.join(pod_texts))
    else:
        await bot.send_message(message.author, "Try {} for the Wolfram command.".format(' or '.join(('#' + chan for chan in config.allowed_spam_channels))))

# endregion

# region Admin
async def admin_help(message=None, args=None):
    await bot.send_message(message.channel, help_text(message.author, admin_commands))


async def clear(message=None, args=None):
    try:
        n = int(args[1])
    except:
        n = 10
    logs = await bot.logs_from(message.channel)
    deleted = 0
    for message in logs:
        if message.author.id == bot.user.id:
            deleted += 1
            await bot.delete_message(message)
        if deleted >= n:
            return


def segment_length(text):
    if len(text) < 2000:
        return len(text)

    for sep in '\n".':
        pos = text.rfind(sep, 0, 1995)
        if pos != -1:
            return pos
    return 2000


async def send_long(channel, text):
    text_blocks = text.split('```')
    in_code_block = True if text.startswith('```') else False
    for text_part in text_blocks:
        while text_part:
            length = segment_length(text_part)
            await bot.send_message(channel, '{0}{1}{0}'.format('```' if in_code_block else '', text_part[:length]))
            text_part = text_part[length:]
        in_code_block = not in_code_block


async def paste(message=None, args=None):
    import urllib.request
    from urllib.request import urlopen
    from urllib.parse import urlparse
    url = urlparse(args[1])
    new_url = ''.join(['http://' if url.scheme == '' else url.scheme + '://',
                       url.netloc,
                       '/raw' if not url.path.startswith('/raw') else '',
                       url.path])
    try:
        with urlopen(new_url) as response:
            html = response.read()
            await send_long(message.channel, html.decode('utf-8'))
    except urllib.request.URLError:
        pass


async def stop_all(message=None, args=None):
    await bot.send_message(message.channel, "Ending all conversations.")
    bot.conversations.clear()


async def deactivate(message=None, args=None):
    bot.active = False


async def activate(message=None, args=None):
    bot.active = True


async def limit(message=None, args=None):
    for member in message.mentions:
        print('Limited', member.name)
        bot.limited_users.add(member.id)


async def unlimit(message=None, args=None):
    for member in message.mentions:
        print('Unlimited', member.name)
        bot.limited_users.discard(member.id)


async def unlimit_all(message=None, args=None):
    bot.limited_users.clear()


async def eval_command(message=None, args=None):
    str_to_eval = ' '.join(args[1:]).replace('`', '')
    try:
        await bot.send_message(message.channel, eval(str_to_eval))
    except Exception as e:
        await bot.send_message(message.author, e)


# endregion


commands = OrderedDict([
    ('help', CommandInfo(help_disp, '', 'Displays this help text.')),
    ('whoami', CommandInfo(whoami, '', 'Gives some info about yourself.')),
    ('whois', CommandInfo(whois, '{user mention}', 'Gives some info about the user.')),
    ('echo', CommandInfo(echo, '{message}', 'Echoes the message back.')),
    ('roll', CommandInfo(roll, '{dice}', 'Rolls dice in the format NdX+C.')),
    ('flip', CommandInfo(flip, '', 'Flips a coin.')),
    ('8ball', CommandInfo(eightball, '{query}', 'The Magic 8 Ball has the answers to all questions.')),
    ('uptime', CommandInfo(uptime, '', 'Displays bot uptime.')),
    ('startconversation', CommandInfo(start_convo, '', 'Starts a conversation with the bot.')),
    ('endconversation', CommandInfo(end_convo, '', 'Ends your conversation with the bot.')),
    ('lenny', CommandInfo(lenny, '{number (optional)}', '( ͡° ͜ʖ ͡°)')),
    ('wolfram', CommandInfo(wolfram, '{query}', 'Queries Wolfram Alpha'))
])

admin_commands = OrderedDict([
    ('adminhelp', CommandInfo(admin_help, '', 'Displays this admin help text.')),
    ('clear', CommandInfo(clear, '{number}', 'Clears n bot messages in channel.')),
    ('paste', CommandInfo(paste, '{pastebin url}', 'Pastes the text of the pastebin.')),
    ('stopall', CommandInfo(stop_all, '', 'Stops all conversations.')),
    ('deactivate', CommandInfo(deactivate, '', 'Deactivates the bot.')),
    ('activate', CommandInfo(activate, '', 'Activates the bot.')),
    ('limit', CommandInfo(limit, '{user mentions...}', 'Disables the users from giving commands.')),
    ('unlimit', CommandInfo(unlimit, '{user mentions...}', 'Enables the users to get commands again.')),
    ('unlimitall', CommandInfo(unlimit_all, '', 'Enables all users to use commands again.')),
    ('eval', CommandInfo(eval_command, '{expression}', 'Evaluates a Python 3.5 expression.')),
])


async def command(message, admin):
    args = message.content.replace(config.prefix, '', 1).split(' ')
    admin_command_info = admin_commands.get(args[0], None) if admin else None
    command_info = commands.get(args[0], None)

    if admin_command_info is not None:
        await admin_command_info.func(message=message, args=args)
    elif command_info is not None:
        await command_info.func(message=message, args=args)
