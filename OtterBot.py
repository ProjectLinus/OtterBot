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
import random


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


bot = Bot(command_prefix='???')

serverDocsDict={}
lastMessage = {}
indexingCount = 0
serverTermsIndex = {}



@bot.event
async def on_ready():
    for server in bot.servers:
        serverQueryMap = []
        termIndex = {}
        if(os.path.isfile(str(server.id)+'.txt')):
            with open(str(server.id)+'.txt','r+',encoding='utf8') as serverCorpus:
                data = json.load(serverCorpus)
                for element in data['pairs']:
                    terms = Lab2.cleanPhrase(element['query'])
                    checkQuery = await messageCheck(element['query'])
                    checkAnswer = await messageCheck(element['answer'])
                    if(checkQuery and checkAnswer and ('otterbot' not in element['query'].lower()) and ('belmiro' not in element['answer'].lower())):
                        if(len(terms) == 0):
                            serverQueryMap.append([element['query'],element['answer'],1])
                        else:
                            serverQueryMap.append([element['query'],element['answer'],len(terms)])
                        termIndex = Lab2.createIndex(terms,len(serverQueryMap)-1,termIndex)
                        serverTermsIndex[server.id] = termIndex
            serverDocsDict[server.id] = serverQueryMap
            lastMessage[server.id] = serverQueryMap[-1][1]

        else:
            f = open(str(server.id)+'.txt','w',encoding='utf8')
            f.write('{\"pairs\": [{\"query\": \"Are you cutebot?\", \"answer\": \":mothyes:\"}]}')
            f.close()
            serverDocsDict[server.id] = [['Are you cutebot?',':mothyes:',3]]
            lastMessage[server.id] = ':mothyes:'

@bot.event
async def on_server_join(server):
    if(server.id not in serverDocsDict.keys()):
        f = open(str(server.id)+'.txt','w',encoding='utf8')
        f.write('{\"pairs\": [{\"query\": \"Are you cutebot?\", \"answer\": \":mothyes:\"}]}')
        f.close()
        serverDocsDict[server.id] = [['Are you cutebot?',':mothyes:',3]]
        lastMessage[server.id] = ':mothyes:'



@bot.event
async def on_message(message):
    checkNewMessage = await messageCheck(message.content.lower())
    if(checkNewMessage and not message.author.bot):
        global indexingCount
        serverId = message.server.id
        queryToAnswer = lastMessage[serverId]
        tokenizedMessage = Lab2.cleanPhrase(message.content)
        terms = Lab2.cleanPhrase(queryToAnswer)
        await channelAllowed(message.channel.id)
		
		
        if('otterbot' in tokenizedMessage or 'belmiro' in tokenizedMessage and await channelAllowed(message.channel.id)):
            if(len(tokenizedMessage) > 1):
                if('otterbot' in tokenizedMessage):
                    tokenizedMessage.remove('otterbot')
                if('belmiro' in tokenizedMessage):
                    tokenizedMessage.remove('belmiro')
            print('USER INPUT: ',tokenizedMessage)
            similPars = Lab2.prodSimilarityOtter(tokenizedMessage,serverDocsDict[serverId],serverTermsIndex[serverId])
            if(len(similPars) > 0):
                sortedPairs = sorted( ((v,k) for k,v in similPars.items()), reverse=True)
                sortedJaccardList = await generateListByJaccard(tokenizedMessage,sortedPairs,serverId)
                if(len(sortedPairs)>4):
                    sortedPairs = sortedPairs[0:4]
                    sortedJaccardList = sortedJaccardList[0:4]
                for pair in sortedPairs:
                    print('PROPOSAL: ' + str(serverDocsDict[serverId][pair[1]][1]) + '    [' + str(serverDocsDict[serverId][pair[1]][0]) + ']')
                for pair in sortedJaccardList:                 
                    print('PROPOSAL: ' + str(serverDocsDict[serverId][pair[0][1]][1]) + '    [' + str(serverDocsDict[serverId][pair[0][1]][0]) + ']')
                    sortedPairs.append(pair[0])
                #choice = random.randrange(math.ceil(len(sortedJaccardList)))
                choice = random.randrange(math.ceil(len(sortedPairs)))
                #await bot.send_message(message.channel,str(serverDocsDict[serverId][sortedJaccardList[choice][0][1]][1]))
                await bot.send_message(message.channel,str(serverDocsDict[serverId][sortedPairs[choice][1]][1]))
            else:
                await bot.send_message(message.channel,'<:sadotter:509261369493946369>')
        else:
            if(len(terms) == 0):
                serverDocsDict[serverId].append([queryToAnswer,message.content,1])
            else:
                serverDocsDict[serverId].append([queryToAnswer,message.content,len(terms)])
            await createTermEntry(terms,len(serverDocsDict[serverId]),serverId)
            print('Query: ' + queryToAnswer)
            print('Answer: ' + message.content)
            
            lastMessage[serverId] = message.content
            if(random.random() < 0.002):
                similPars = Lab2.prodSimilarityOtter(tokenizedMessage,serverDocsDict[serverId],serverTermsIndex[serverId])
                if(len(similPars) > 0):
                    sortedPairs = sorted( ((v,k) for k,v in similPars.items()), reverse=True)
                    if(len(sortedPairs)>5):
                        sortedPairs = sortedPairs[0:5]
                    for pair in sortedPairs:
                        print('PROPOSAL: ' + str(serverDocsDict[serverId][pair[1]][1]) + '    [' + str(serverDocsDict[serverId][pair[1]][0]) + ']')
                    choice = random.randrange(math.ceil(len(sortedPairs)))
                    await bot.send_message(message.channel,str(serverDocsDict[serverId][sortedPairs[choice][1]][1]))
            indexingCount += 1
            if(indexingCount > 10):
                indexingCount = 0
                await saveCurrentData()
    elif(message.author.id == bot.user.id):
        await bot.add_reaction(message,'✅')
        await bot.add_reaction(message,'❌')
        await bot.add_reaction(message,'❔')




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


@bot.event
async def channelAllowed(channelId):
    return channelId not in ['486239015767375891']

@bot.event
async def createTermEntry(terms,docPosition,serverId):
    global serverTermsIndex

    for term in terms:
        if(term in serverTermsIndex[serverId].keys()):
            if(serverTermsIndex[serverId][term][-1][0] != docPosition-1):
                serverTermsIndex[serverId][term].append([docPosition-1,1])
            else:
                serverTermsIndex[serverId][term][-1][1] += 1
        else:
            serverTermsIndex[serverId][term] = [[docPosition-1,1]]

@bot.event
async def messageCheck(message):
    return message != "" and len(message)<160 and len(message)>5 and '@' not in message and 'nsfw' not in message and 'left for this hour' not in message and 'are now married' not in message and message[0] != '$' and 'to reset the timer' not in message and 'p!catch' not in message


@bot.event
async def birthdayMessage():
    userId = '<@244278043588165632>'
    message = 'Happy birthday, ' + userId + '! I hope you have a great day, and I apologize for all the times I said mean stuff to you ❤️'
    await bot.send_message(discord.Object(id='509192905139683330'),message)


@bot.event
async def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection / union)


@bot.event
async def generateListByJaccard(queryTokens,sortedPairs,serverId):
    jaccardList = []
    for pair in sortedPairs:
        answerString = str(serverDocsDict[serverId][pair[1]][1])
        answerTokens = Lab2.cleanPhrase(answerString)
        score = await jaccard_similarity(queryTokens,answerTokens)
        jaccardList.append((pair,score))
    sortedList = sorted(jaccardList, key=lambda x: x[1], reverse=True)
    return sortedList

bot.run(Token.token)