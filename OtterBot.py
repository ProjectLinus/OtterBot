import discord
from discord.ext import commands
from discord.ext.commands import Bot
import logging
from discord import utils
import asyncio
import Token
import nltk
import re
import sys
import math
import Lab2
import os.path
import json


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


bot = Bot(command_prefix='')

serverDocsDict={}
lastMessage = {}
indexingCount = 0





@bot.event
async def on_ready():
    for server in bot.servers:
        serverQueryMap = []
        if(os.path.isfile(str(server.id)+'.txt')):
            with open(str(server.id)+'.txt','rw',encoding='utf8') as serverCorpus:
                data = json.load(serverCorpus)
                for element in data['pairs']:
                    serverQueryMap.append([element['query'],element['answer']])
            serverDocsDict[server.id] = serverQueryMap
            lastMessage[server.id] = serverQueryMap[:-1][1]

        else:
            f = open(str(server.id)+'.txt','w',encoding='utf8')
            f.write('{\'pairs\': [{\'query\': \'Are you cutebot?\', \'answer\': \':mothyes:\'}]}')
            f.close()
            serverDocsDict[server.id] = ['Are you cutebot?',':mothyes:']
            lastMessage[server.id] = ':mothyes:'


@bot.event
async def on_server_join(server):
    if(server.id not in serverDocsDict.keys()):
        f = open(str(server.id)+'.txt','w',encoding='utf8')
        f.write('{\'pairs\': [{\'query\': \'Are you cutebot?\', \'answer\': \':mothyes:\'}]}')
        f.close()
        serverDocsDict[server.id] = ['Are you cutebot?',':mothyes:']
        lastMessage[server.id] = ':mothyes:'



@bot.event
async def on_message(message):
    global indexingCount
    serverId = message.server.id
    queryToAnswer = lastMessage[serverId]
    serverDocsDict[serverId].append([queryToAnswer,message.content])
    lastMessage[serverId] = message.content
    indexingCount += 1
    if(indexingCount > 3000):
        indexingCount = 0
        saveCurrentData()

@bot.event
async def saveCurrentData():
    for serverId in serverDocsDict.keys():
        data = {}
        data['pairs'] = []
        for pair in range(len(serverDocsDict[serverId])):
            data['pairs'].append({
                'query': serverDocsDict[serverId][pair][0],
                'answer': serverDocsDict[serverId][pair][1]
            })
        with open(serverId + '.txt', 'w') as output:
            json.dump(data,output)