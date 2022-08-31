import json
import requests
from lxml import html
import discord
import logging
from pprint import pprint
import aiohttp

client = discord.Client(command_prefix='!')
skillmap = {'1': 'Q', '2': 'W', '3': 'E', '4': 'R'}


@client.event
async def on_ready():
    logging.info('Logged in and ready to go!')
    logging.info('Running as {} ({})'.format(client.user.name, client.user.id))


@client.event
async def on_message(message):
    if message.content.startswith('!help'):
        em = discord.Embed()
        em.set_author(name="Champion GG Builds Bot", url="https://discordapp.com", icon_url="http://ddragon.leagueoflegends.com/cdn/8.11.1/img/item/3153.png")
        em.set_footer(text="Champion GG Bot - Type !help for commands", icon_url="http://ddragon.leagueoflegends.com/cdn/8.11.1/img/item/3153.png")
        
        msg = '```!Build <Champion> <Role> \n!Build <Champion>\n!winrate <Champion>\n!info```'
        em.add_field(name="Commands", value=msg)
        await client.send_message(message.channel, embed = em)


    if message.content.startswith('!build'):
        logging.info('Received request from {} on {}:{}'.format(message.author.name, message.server.name, message.channel.name))
        k = len(message.content)
        print(k)
        print(len(message.content.split(' ')[1:][0])+7)
        if(k == len(message.content.split(' ')[1:][0])+7):
            champion = message.content.split(' ')[1:][0]
            role = 'x'
        else:
            champion, role = message.content.split(' ')[1:]
        logging.info('Looking up build for {}/{}'.format(champion, role))
        try:
            rawData = fetch_rawData(champion,role)
            print(rawData)
            games, winrate, itemlist, itemcodes = fetch_build(champion, role, rawData)
            skillorder = fetch_skillorder(champion,role, rawData)
            primaryrunes, secondaryrunes = fetch_runes(champion,role, rawData)
        except Exception as e:
            logging.info('Problem fetching build: {}'.format(e))
            client.send_message('Unknown build combination or error fetching request.')

        games = 'The number of games played: ' + games
        winrate = 'The winrate of this build: ' + winrate + '%'
        skillorder = 'Most Freqeuent Skill Order: ' + skillorder

        buildinfo = games + '\n' + winrate
        itemlist = itemlist + '\n' + '\n'
        skillorder = skillorder + '\n' + '\n'
        runes = primaryrunes + '\n' + secondaryrunes
        em = discord.Embed()

        em.set_author(name="Champion GG Builds Bot", url="https://discordapp.com", icon_url="http://ddragon.leagueoflegends.com/cdn/8.11.1/img/item/3153.png")
        em.set_footer(text="Champion GG Bot - Type !help for commands", icon_url="http://ddragon.leagueoflegends.com/cdn/8.11.1/img/item/3153.png")

        em.add_field(name="Build Info", value=buildinfo)
        em.add_field(name="Build Order", value=itemlist)
        em.add_field(name="Skill Order", value=skillorder)
        em.add_field(name="Rune Order", value=runes)

        await client.send_message(message.channel, embed = em)

    if message.content.startswith('!winrate'):
        logging.info('Received request from {} on {}:{}'.format(message.author.name, message.server.name, message.channel.name))
        k = len(message.content)
        if(k == len(message.content.split(' ')[1:][0])+9):
            champion = message.content.split(' ')[1:][0]
            role = 'x'
        else:
            champion, role = message.content.split(' ')[1:]
        try:
            rawData = fetch_rawData(champion,role)
            print(role)
            print(champion)
            wr = fetch_winrate(rawData)
        except Exception as e:
            logging.info('Problem fetching build: {}'.format(e))
            client.send_message('Unknown build combination or error fetching request.')


        wr = 'The winrate of ' + champion + ' is ' + wr + '% ' + '\n'
        em = discord.Embed()

        em.set_author(name="Champion GG Builds Bot", url="https://discordapp.com", icon_url="http://ddragon.leagueoflegends.com/cdn/8.11.1/img/item/3153.png")
        em.set_footer(text="Champion GG Bot - Type !help for commands", icon_url="http://ddragon.leagueoflegends.com/cdn/8.11.1/img/item/3153.png")

        em.add_field(name="Winrate", value=wr)
        
        await client.send_message(message.channel, embed = em)

    if message.content.startswith('!bestchamp'):
        role = message.content.split(' ')[1:]
        bestchamp = fetch_bestChamp(role)

    if message.content.startswith('!info'):
        currentpatch = fetch_info()
        em = discord.Embed()

        em.set_author(name="Champion GG Builds Bot", url="https://discordapp.com", icon_url="http://ddragon.leagueoflegends.com/cdn/8.11.1/img/item/3153.png")
        em.set_footer(text="Champion GG Bot - Type !help for commands", icon_url="http://ddragon.leagueoflegends.com/cdn/8.11.1/img/item/3153.png")

        em.add_field(name="Current Patch", value=currentpatch)

        await client.send_message(message.channel, embed = em)

        
def fetch_info():
    try:
        r = requests.get('http://api.champion.gg/v2/general?&api_key=29368f56077e425ad68d2bec94a2a4c3')
    except Exception as e:
            logging.info('Problem fetching build: {}'.format(e))
            client.send_message('Unknown build combination or error fetching request.')
    data = r.text
    startingpoint = data.find('"patch":"')
    endingpoint = data.find('","', startingpoint)
    currpatch = data[startingpoint + 9 : endingpoint]
    return currpatch


def fetch_bestChamp(role):
    if role == 'mid':
        role = 'middle'
    if role == 'supp':
        role = 'support'
    if role == 'jung':
        role == 'jungle'
    try:
        r = requests.get('http://champion.gg/')
    except Exception as e:
            logging.info('Problem fetching build: {}'.format(e))
            client.send_message('Unknown build combination or error fetching request.')

    


def fetch_winrate(rawData):
    msg1 = '"winRate":'
    msg2 = ',"play'
    startingindex = rawData.find(msg1)
    endingindex = rawData.find(msg2, startingindex)
    wr = rawData[startingindex + len(msg1) : endingindex]
    wr = wr[2 : 4]
    return wr

def fetch_rawData(champion, role):
    if role == 'mid':
        role = 'middle'
    if role == 'supp':
        role = 'support'
    try:
        if (role != 'middle') or (role != 'top') or (role != 'adc') or (role != 'support') or (role != 'jungle'):
            r = requests.get('http://champion.gg/champion/{}'.format(champion))
        else:
            r = requests.get('http://champion.gg/champion/{}/{}'.format(champion, role))
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        return None

    tree = html.fromstring(r.content)
    elements = tree.xpath('//script')
    build_script = ''
    for element in elements:
        if element.text is not None:
            if 'matchupData.championData' in element.text:
                build_script = element.text.split(';')

    full_stats = json.dumps(build_script)
    data = json.loads(full_stats)
    
    rawData = data[0]
    return rawData

def fetch_build(champion, role, rawData):
    # Finding location of highest win rate items
    str1 = '"items":{"mostGames":{"items":'
    str2 = '"highestWinPercent":{"items":[{'
    str3 = '}]'
    str4 = '"id":"'

    # Number of Games
    str5 = '"games":'
    # Winrate
    str6 = ',"winPercent":'
    

    
    # Finding location of mostplayed items
    startingpoint = rawData.find(str1)
    endingpoint = rawData.find(str3, startingpoint)
    items = rawData[startingpoint + len(str1) : endingpoint]

    # Number of Games
    startingpointgames = rawData.find(str5, endingpoint)
    endingpointgames = rawData.find(',"' , startingpointgames)
    games = rawData[startingpointgames + len(str5) : endingpointgames]

    # Winrate
    startingpointwinrate = rawData.find(str6, endingpointgames)
    endingpointwinrate = rawData.find('}', startingpointwinrate)
    winrate = rawData[startingpointwinrate + len(str6) : endingpointwinrate]
    winratestartingpoint = winrate.find('.')
    winrate = winrate[winratestartingpoint + 1 : winratestartingpoint + 3]

    listofitems2 = []
    for x in range(6):
        starting = items.find(str4)
        item = items[starting + len(str4) : starting + len(str4) + 4]
        listofitems2.append(item)
        items = items[13 : len(items)]

    itemcodes = {'3001': 'Abyssal Mask', '3194': 'Adapative Helm', '3187': 'Arcane Sweeper (item)', '3003': 'Archangels Staff', '3504': 'Ardent Censer', '3174': 'Athenes Unholy Grail', '3102': 'Banshees Veil', '3117': 'Boots of Mobility', '3009': 'Boots of Swiftness', '2033': 'Corrupting Potion', '3742': 'Dead Mans Plate', '3812': 'Deaths Dance', '3147': 'Duskblade of Draktharr', '3814': 'Edge of Night', '3508':'Essence Reaver', '3110':'Frozen Heart', '3022': 'Frozen Mallet', '3193': 'Gargoyle Stoneplate', '3030':'Hextech GLP-800', '3146':'Hextech Gunblade', '3152':'Hextech Protobelt-01', '2032':'Hunters Potion', '3025':'Iceborn Gauntlet', '3158':'Ionian Boots of Lucidity', '3109':'Knights Vow', '3151':'Liandrys Torment', '3100':'Lich Bane', '3190':'Locket of the Iron Solari', '3036':'Lord Dominiks Regards', '3104':'Lord Van Damms Pillager', '3285':'Ludens Echo', '3004':'Manamune', '3156': 'Maw of Malmortius', '3041': 'Mejais Soulstealer', '3139': 'Mercurial Scimitar', '3111':'Mercurys Treads', '3222':'Mikaels Crucible', '3170':'Moonflair Spellblade', '3165':'Morellonomicon', '3033':'Mortal Reminder', '3115': 'Nashors Tooth', '3047':'Ninja Tabi', '3056':'Ohmwrecker','3198': 'Perfect Hex Core','3046': 'Phantom Dancer','3089': 'Rabadons Deathcap','3143': 'Randuins Omen','3094': 'Rapid Firecannon','3074': 'Ravenous Hydra','3107': 'Redemption','3069': 'Remnant of the Ascended','3401': 'Remnant of the Aspect','3092': 'Remnant of the Watchers','3800': 'Righteous Glory','3027': 'Rod of Ages','3085': 'Runaans Hurricane', '3116': 'Rylais Crystal Scepter','3040': 'Seraphs Embrace','3069': 'Shurelyas Reverie','3020': 'Sorcerers Shoes','3907': 'Spellbinder','3065': 'Spirit Visage','3087': 'Statikk Shiv','3053': 'Steraks Gage','3068': 'Sunfire Cape','3071': 'The Black Cleaver','3072': 'The Bloodthirster','3185': 'The Lightbringer','3075': 'Thornmail','3309': 'Timeworn Face of the Mountain','3312': 'Timeworn Frost Queens Claim','3306': 'Timeworn Talisman of Ascension','3748': 'Titanic Hydra','3078': 'Trinity Force','3905': 'Twin Shadows','3135': 'Void Staff','3083': 'Warmogs Armor','3091': 'Wits End', '3090': 'Wooglets Witchcap','3142': 'Youmuus Ghostblade','3050': 'Zekes Convergence','3157': 'Zhonyas Hourglass','3512': 'Zz Rot Portal', '3153': 'Blade of the Ruined King', '3124': 'Guinsoos Rageblade', '3006': 'Berserkers Greaves', '3046': 'Phantom Dancer', '3031': 'Infinity Edge', '3026': 'Guardian Angel', '3060': 'Banner of Command', '3095': 'Stormrazor', '3383': 'Locket of the Iron Solari', '1402':'Runic Echoes', '1412': 'Jungle: Warrior', '1401': 'Cinderhulk', '1416': 'Bloodrazor', '1400': 'Jungle: Warrior', '1413':'Cinderhulk', '1419': 'Bloodrazor'}
    itemnames2 = []
    string2 = ''
    for x in range(6):
        itemnames2.append(itemcodes[listofitems2[x]])
        if x != 5:
            string2 = string2 + itemnames2[x] + ' -> '
        if x == 5:
            string2 = string2 + itemnames2[x]
    
    itemlist = string2
    return games, winrate, itemlist, listofitems2

def fetch_skillorder(champion, role, rawData):
    skillmap = {'1': 'Q', '2': 'W', '3': 'E', '4': 'R'}
    skillordermsg1 = '"mostGames":{"order":['
    skillordermsg2 = '"],'
    startingSkillOrderPoint = rawData.find(skillordermsg1)
    endingSkillOrderPoint = rawData.find(skillordermsg2, startingSkillOrderPoint)
    skillOrder = rawData[startingSkillOrderPoint + len(skillordermsg1) : endingSkillOrderPoint]
    
    listSkillOrder = []
    startingpoint = skillOrder.find('"')
    endingpoint = skillOrder.find('"', startingpoint + 1)
    listSkillOrder.append(skillOrder[startingpoint+ 1 : endingpoint])
    initial = startingpoint
    toFind = '","'
    for x in range(16):
        startingpoint = skillOrder.find(toFind, initial)
        endingpoint = startingpoint + len(toFind) + 1
        listSkillOrder.append(skillOrder[startingpoint + len(toFind) : endingpoint])
        skillOrder = skillOrder[len(toFind) + 1: ]        
    
    toFind = '"]'
    endingpoint = skillOrder.find(toFind)
    listSkillOrder.append(skillOrder[1 : endingpoint - 3])
    print(listSkillOrder)
    skillOrderNames = []
    skillOrderString = ''
    for x in range(18):
        skillOrderNames.append(skillmap[listSkillOrder[x]])
        if x != 17:
            skillOrderString = skillOrderString + skillOrderNames[x] + ' -> '
        if x == 17:
            skillOrderString = skillOrderString + skillOrderNames[x]
    print(skillOrderString)
    return skillOrderString

def fetch_runes(champion, roles, rawData):
    runesmsg1 = '"newRunes":{"mostGames":{"runes":{'
    runesmsg2 = '"name":"'
    runesmsg3 = '","description":'
    runesmsg5 = '"text2":{"name":"'
    runesmsg4 = '","location":'
    startingpoint = rawData.find(runesmsg1)
    endingpoint = rawData.find(runesmsg2, startingpoint)

    runelist = []
    firstindex = rawData.find(runesmsg2, startingpoint)
    secondindex = rawData.find(runesmsg3, firstindex)
    runelist.append(rawData[firstindex + len(runesmsg2) : secondindex])
    print(runelist)
    startingpoint = startingpoint + len(runesmsg1) + len(runesmsg2) + len(runesmsg3) + len(runelist[0])
    print(startingpoint)
    runeListString = runelist[0]
    for x in range(4):
        firstindex = rawData.find(runesmsg2, startingpoint)
        secondindex = rawData.find(runesmsg4, firstindex)
        runelist.append(rawData[firstindex + len(runesmsg2) : secondindex])
        startingpoint = secondindex
        runeListString = runeListString + ' -> ' + runelist[x+1] 
    
    print(runeListString)
    startingpoint = rawData.find(runesmsg5, startingpoint)
    endingpoint = rawData.find(runesmsg2, startingpoint)
    firstindex = endingpoint
    runelist2 = []
    secondindex = rawData.find(runesmsg3, firstindex)
    runelist2.append(rawData[firstindex + len(runesmsg2) : secondindex ])
    startingpoint = startingpoint + len(runesmsg5) + len(runesmsg2) + len(runesmsg3) + len(runelist2[0])
    runeList2String = runelist2[0]
    
    for x in range(2):
        firstindex = rawData.find(runesmsg2, startingpoint)
        secondindex = rawData.find(runesmsg4, firstindex)
        runelist2.append(rawData[firstindex + len(runesmsg2) : secondindex])
        startingpoint = secondindex
        runeList2String = runeList2String + ' -> ' + runelist2[x+1]
    
    return runeListString, runeList2String
        


