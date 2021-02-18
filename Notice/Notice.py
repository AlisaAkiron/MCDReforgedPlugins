import json
import re
import os

from typing import Union, Dict, Any

from mcdreforged.plugin.server_interface import ServerInterface, CommandSource
from mcdreforged.api.all import *

PLUGIN_METADATA = {
    'id': 'notice',
    'version': '1.0.0',
    'name': 'Notice',
    'description': 'Just a easy to use notice system.',
    'author': 'LiamSho',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
        'online_player_api': '*'
    }
}

PREFIX = '!!notice'
DATA_FILE = os.path.join('config', PLUGIN_METADATA['id'], 'data.json')
CONFIG_FILE = os.path.join('config', PLUGIN_METADATA['id'], 'config.json')

HelpMessage = '''
------ {1} v{2} ------
简易的公告插件
§7{0}§r 显示公告
§7{0} help§r 显示帮助
§7{0} add §6[<title>]§r §6[<content>]§r §c添加§r一条公告
§7{0} del §6[<title>]§r §c删除§r一条公告
§7{0} setheader §6[<header>]§r §c修改§r标题
§7{0} autosend §6[<True/False>]§r 是否在玩家加入服务器时自动发送
§7{0} reload§r 重载公告和配置文件（直接修改配置文件请用这条指令重载）
§7{0} broadcast§r 向所有在服务器内的玩家广播
注1：title, header和content必须用引号括起，引号内可使用转义字符
注2：建议配合 §7joinMOTDR§r 插件使用
'''.strip().format(PREFIX, PLUGIN_METADATA['name'], PLUGIN_METADATA['version'])

default_notices = {
    '公告1': '欢迎使用Notice插件，输入!!notice help查看帮助',
    'Notice1': 'Welcome to use Notice plugin, for help message, type !!notice help',
}

default_config = {
    'NoticeHeader': 'Notice',
    'AutoSend': True,
    'MinimumPermissionLevel': 3,
}

notices = dict()

config = dict()

def get_notice_rtext():
    global notices
    notice_rtext = RTextList()
    for key, val in notices.items():
        notice_rtext.append('§6' + key + ': §r' + val + '\n')
    return notice_rtext

def get_notice_data(server):
    global notices
    try:
        with open(DATA_FILE, 'r') as file:
            notices = json.load(file)
    except:
        server.logger.info('No data file found, use default config.')
        notices = default_notices
        save_json_file('data')

def get_config(server):
    global config
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
    except:
        server.logger.info('No config file found, use default config.')
        config = default_config
        save_json_file('config')

def save_json_file(filetype):
    global config
    global notices
    check_conf_folder()
    if filetype == 'config':
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    elif filetype == 'data':
        with open(DATA_FILE, 'w') as f:
            json.dump(notices, f, indent=2)

def check_conf_folder():
    folder = os.path.dirname(DATA_FILE)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    folder = os.path.dirname(CONFIG_FILE)
    if not os.path.isdir(folder):
        os.makedirs(folder)

def print_notice(src: CommandSource):
    src.reply(get_output_rtext())

def get_output_rtext():
    output_rtext = RTextList()
    output_rtext.append(config['NoticeHeader'] + '\n\n')
    output_rtext.append(get_notice_rtext())
    return output_rtext

def print_help_message(source: CommandSource):
    if source.is_player:
        source.reply('')
    for line in HelpMessage.splitlines():
        prefix = re.search(r'(?<=§7){}[\w ]*(?=§)'.format(PREFIX), line)
        if prefix is not None:
            print_message(source, RText(line).set_click_event(RAction.suggest_command, prefix.group()), prefix='')
        else:
            print_message(source, line, prefix='')

def print_message(source: CommandSource, msg, tell=True, prefix='[NOTICE] '):
    msg = prefix + msg
    if source.is_player and not tell:
        source.get_server().say(msg)
    else:
        source.reply(msg)

def command_run(message, text, command):
    return RText(message).set_hover_text(text).set_click_event(RAction.run_command, command)
    
def print_unknown_argument_message(source: CommandSource, error: UnknownArgument):
    print_message(source, command_run(
        '参数错误！请输入§7{}§r以获取插件信息'.format(PREFIX + ' help'),
        '点击查看帮助',
        PREFIX + ' help'
    ))

def add_notice(source: CommandSource, title, content):
    global notices
    try:
        notices[title] = content
        print_message(source, '添加项目§6' + title +'§r成功')
    except:
        print_message(source, '添加失败，请确认title是否重复')
    save_json_file('data')

def del_notice(source: CommandSource, title):
    global notices
    for key, val in notices.items():
        if title == key:
            notices.pop(key)
            print_message(source, '已删除项目§6 ' + key + '§r')
            break
    save_json_file('data')

def reload_notice_data(server: ServerInterface, source: CommandSource):
    get_notice_data(server)
    get_config(server)
    print_message(source, '重载成功')

def broadcast_notice(server: ServerInterface):
    player_list = server.get_plugin_instance('online_player_api').get_player_list()
    output_notice = get_output_rtext()
    for player in player_list:
        server.tell(player, output_notice)
        server.logger.info('Send notice to {} successfully.'.format(player))

def set_header(server: ServerInterface, source: CommandSource, header):
    global config
    config['NoticeHeader'] = header
    print_message(source, '已设置标题为 \n§6' + header + '§r')
    server.logger.info('Set notice header to "' + header + '"')
    save_json_file('config')

def set_autosend(server: ServerInterface, source: CommandSource, switch):
    global config
    if switch == 'True':
        config['AutoSend'] = True
    elif switch == 'False':
        config['AutoSend'] = False
    else:
        print_unknown_argument_message(source, UnknownArgument)
        return
    print_message(source, '已设置自动发送为 \n§6' + switch + '§r')
    server.logger.info('Set auto send function to "' + switch + '"')
    save_json_file('config')

def command_register(server: ServerInterface):
    global config
    def get_literal_node(literal):
        return Literal(literal).requires(lambda src: src.has_permission(config['MinimumPermissionLevel']), failure_message_getter=lambda: '权限不足')

    server.register_command(
        Literal(PREFIX)
            .runs(print_notice)
            .on_error(UnknownArgument, print_unknown_argument_message, handled=True)
        .then(
            get_literal_node('help')
            .runs(lambda src: print_help_message(src))
        )
        .then(
            get_literal_node('add')
            .then(
                QuotableText('title')
                .then(
                    QuotableText('content')
                    .runs(lambda src, ctx: add_notice(src, ctx['title'], ctx['content']))
                )
            )
        )
        .then(
            get_literal_node('del')
            .then(
                QuotableText('title')
                .runs(lambda src, ctx: del_notice(src, ctx['title']))
            )
        )
        .then(
            get_literal_node('reload')
            .runs(lambda src: reload_notice_data(server, src))
        )
        .then(
            get_literal_node('broadcast')
            .runs(lambda src: broadcast_notice(server))
        )
        .then(
            get_literal_node('setheader')
            .then(
                QuotableText('header')
                .runs(lambda src, ctx: set_header(server, src, ctx['header']))
            )
        )
        .then(
            get_literal_node('autosend')
            .then(
                Text('switch')
                .runs(lambda src, ctx: set_autosend(server, src, ctx['switch']))
            )
        )
    )

def on_player_joined(server: ServerInterface, player: str, info: Info):
    if config['AutoSend'] == True:
        server.tell(player, get_output_rtext())

def on_load(server: ServerInterface, prev):
    get_notice_data(server)
    get_config(server)
    server.register_help_message('!!notice', RText('简易公告插件，!!notice help查看帮助'))
    command_register(server)
