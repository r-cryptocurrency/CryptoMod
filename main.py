# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
D1 = False 
import praw 
import string 
import pprint
from nltk.corpus import words
import re
import time
import json
import requests
from storage import SRC

BOT_START_TIME = 1521376589.2023768



settings = {'referrals':[], 'tempban': None, 'agemin': None, 'postmin': None, 'lastUpdated': 0, 'source':''}
settings['source'] = SRC
def containsReferral(text):
    return bool(re.search(settings['referrals'], text))

r = praw.Reddit()
                     

SUBREDDIT = 'CryptoCurrency' #subreddit to run in

referrals = ["etheress.net","eth2usd.com", "futurether.com", "flyether.com", "ethereumexchange.net", "ninether.com", "livecoinchart.net", "bitcoinlondon.org", "stratoon.net", "btclondon.org", "bitcoinat.co.uk", "bitcoinasia.net", "btccc.space", "bitcoina.pw", "asibit.space", "chintra.bid", "tradingchin.win", "cryptofi.cricket", "moneytrad.party", "ficrypto.science", "xchngch.men", "btctr.racing", "zonesbtc.info", "srbtc.info", "sbtc.world", "storeofvalue.github.io", "bitcoinatrade.com", "xtradechina.net", "changecrypto.info", "trkclck.rocks", "ethereumx.site", "tradeethereum.science", "standpointresearch.com", "CoinPump.Group", "palmbeachgroup.com", "hacked.com", "goldreward.io", "wixsite.com", "ethconnect.net", "bitrapidus.com", "71republic.com", "mycryptonews.info", "coincodex.com", "ltd0.com","coin7t.com","cryptoanalyst.co", "tangleblog.com", "actioncoin.io", "twitter.com/tangleblog", "emining.club", "sphere.social", "wcibtc.com", "twitter.com/officialmcafee", "kucoin.com", "dadi.cloud/r/", "travelflex.org/?ref=", "vrlps.co/", "upcoin.com/", "digitexfutures.com", "freedoge.co.in/", "https://www.hoqu.io/?ref_id=", "https://www.binance.com/?ref="]  #list of banned links 
hot_posts = {'EthTrader':[], 'CryptoCurrency':[]}

def checkHot(htps, LIMIT, token):
    all_hot = []
    for post in htps:
        if post.link_flair_text == 'COMEDY':
            all_hot.append(post.id) 
            if len(hot_posts[token]) < LIMIT:
                if post.id not in hot_posts[token]:
                    hot_posts[token].append(post.id)
            elif post.id not in hot_posts[token]:
                print('Removing ' + post.shortlink)
                post.mod.remove()
                c = post.reply('''Thank you for submitting to /r/{0},\n\nTo improve 
                the quality of content on the top page, rising comedy posts are occasionally removed if 
                the subreddit is already overpopulated with similar submissions. Please consider posting 
                comedy content to r/CryptoCurrencyMemes, r/CryptoHumor, or as a comment in the [daily thread]
                (https://www.reddit.com/r/CryptoCurrency/search?q=flair%3AGeneral+Discussion&restrict_sr=on&sort=new&t=all) 
                instead.\n\n*I am a bot, and this action was performed automatically. Please contact the [moderators of 
                this subreddit](https://www.reddit.com/message/compose?to=%2Fr%2F{0}) if you have any 
                questions or concerns.*'''.format(token))
                c.mod.distinguish(how='yes', sticky=True)
                all_hot.remove(post.id)
        hot_posts[token][:] = list(set(hot_posts[token]).intersection(all_hot))
            
def handleBan(datapt, user): 
    if not datapt.saved:
        datapt.save()
        datapt.mod.remove()
        prev_contributions = len([x for x in r.redditor(user).new(limit=300) if x.subreddit.display_name.lower() == 'cryptocurrency'])
        age = (float(time.time()) - float(datapt.author.created_utc)) / (60*60*24) #days 
        
        if age < settings['agemin'] or prev_contributions < settings['postmin']:
            r.subreddit(SUBREDDIT).banned.add(datapt.author, ban_message="Referral links are not allowed in /r/CryptoCurrency!", duration=30)
        else:
            r.subreddit(SUBREDDIT).banned.add(datapt.author, ban_message="Referral links are not allowed in /r/CryptoCurrency!", duration=settings['tempban'])

def banReferrals():
    for comment in r.subreddit(SUBREDDIT).comments(limit=100):
        if containsReferral(comment.body.lower()):
            handleBan(comment, comment.author.name)
    for post in r.subreddit(SUBREDDIT).new(limit=50):
        sftext = ''
        if hasattr(post, 'crosspost_parent'):
            sftext = post.crosspost_parent_list[0]['selftext']
        else:
            sftext = post.selftext
        if containsReferral(str(sftext)+str(post.title)+str(post.url)):
            handleBan(post, post.author.name)
            
def parseWikiPage(source):
    banned_links, ban_data = source.split('---')[1:]
    referrals = re.findall('\`.+?\`', banned_links)[0]
    agemin, postmin, tempban = re.findall('\d+', re.findall('(\$--(.|\s)+?--\$)', ban_data)[0][0])
    return referrals[1:-1], int(tempban), int(agemin), int(postmin)

def badUpdate(wikipage):
    prev_rev_auth = list(wikipage.revisions())[0]['author'].name 
    print("Invalid Update! Reverting & PM'ing {0}".format(prev_rev_auth))
    r.redditor(prev_rev_auth).message("Invalid wiki page update on /r/CryptoCurrency", "Your update to /r/CryptoCurrency/wiki/cryptomodbot was invalid; the changes have been reverted. Contact /u/ClearlyCoder for support.")
    wikipage.edit(settings['source'])
    
    

def updateSettings():
    if float(time.time()) - float(settings['lastUpdated']) > 300:
        wikipage = r.subreddit(SUBREDDIT).wiki['cryptomodbot']
        if wikipage.content_md != settings['source'] or not settings['tempban']:
            print("Updating local wiki!")
            try:
                source = wikipage.content_md 
                settings['referrals'], settings['tempban'], settings['agemin'], settings['postmin'] = parseWikiPage(source)
                settings['lastUpdated'] = time.time()
                settings['source'] = wikipage.content_md
                print("Valid Updated Completed")
            except:
                badUpdate(wikipage)
                
# print(r.submission(id='dnhkf4w').permalink())

def removeDuplicates(pposts):
    duplicates = [post for post in pposts if list(map(lambda x: x.url, pposts)).count(post.url) > 1]
    dsort = sorted(duplicates, key=lambda x: x.url)
    new_duplicates = dsort[::2]
    old_duplicates = dsort[1::2]
    for key, duplicate in enumerate(new_duplicates):
        original, duplicate = sorted([duplicate, old_duplicates[key]], key=lambda x: float(x.created_utc))
        duplicate.mod.remove()
        s = duplicate.reply('''Thank you for submitting to /r/CryptoCurrency,\n\nUnfortunately, your post has
        been removed because this link was already submitted [recently]({0}).\n\n*I am a bot, and this action was performed automatically. Please contact the [moderators of 
        this subreddit](https://www.reddit.com/message/compose?to=%2Fr%2F{0}) if you have any 
        questions or concerns.*'''.format( 'https://www.reddit.com' + original.permalink ) )
        s.mod.distinguish(how='yes', sticky=True)
        

def extractCoins(pst, ac):
    text_data = "".join(char for char in pst.title if char not in string.punctuation)
    text_data = " ".join(char for char in text_data.split(" ") if not (not char.isupper() and char.lower() in map(lambda x: x.lower(), words.words()) and len(char) <= 4))
    matches = list(set(text_data.lower().split(' ')).intersection(set(map(lambda x: x.lower(), ac))))
    matches = list(filter(lambda x: x.lower() != "crypto", matches))
    names = list(map(lambda x: x.lower(), ac[:len(ac)/2]))
    symbols = list(map(lambda x: x.lower(), ac[len(ac)/2:]))
    rmatches = [] 
    for item in matches:
        if item.lower() in symbols:
            rmatches.append(names[symbols.index(item.lower())])
        else:
            rmatches.append(item.lower())
    print(rmatches)
    return list(set(rmatches))
    
    
        
def limitCoins(hot_pts, all_coins):
    data = []
    for post in hot_pts:
        post.coindata = extractCoins(post, all_coins)
    for post in hot_pts:
        for item in post.coindata:
            data.append( (post, item) )
    all_mentioned = [x[1] for x in data]
    triples = [x for x in data if all_mentioned.count(x[1]) >= 3]
    sorted_triples = sorted(triples, key=lambda x: float(x[0].created_utc))
    if len(triples) == 0:
        return
    sorted_triples[-1][0].mod.remove()
    s = sorted_triples[-1][0].reply('''Thank you for submitting to /r/{0},\n\nYour post has been
    removed because there are already 2 posts about this coin on the front page.
    \n\n*I am a bot, and this action was performed automatically. Please contact the [moderators of 
            this subreddit](https://www.reddit.com/message/compose?to=%2Fr%2F{0}) if you have any 
            questions or concerns.*'''.format(SUBREDDIT))
    s.mod.distinguish(how='yes', sticky=True)
        
        
def removeAllComedy(new_pts):
    print(new_pts)
    for post in new_pts:
        if float(post.created_utc) - float(BOT_START_TIME) > 0:
            if post.link_flair_text != None:
                if post.link_flair_text.lower() == "comedy":
                    print("HERE")
                    post.mod.remove()
                    post.reply("""Hello! 
        
Thank you for your submission - Please feel free to re-submit your post to our dedicated fun subreddit r/cryptocurrencymemes.
        
----
        
Memes and Comedy posts are now considered low quality content on this subreddit and will be removed. Repeated attempts to post this type of content on r/cryptocurrency will lead to a subreddit suspension and possibly a ban. \n\n*I am a bot, and this action was performed automatically. Please contact the [moderators of this subreddit](https://www.reddit.com/message/compose?to=%2Fr%2F{0}) if you have any questions or concerns.*""").mod.distinguish(how='yes', sticky=True)
            if post.url != None:
                if ".png" in post.url[-5:] or ".jpg" in post.url[-5:] or ".jpeg" in post.url[:-5]:
                    post.mod.remove()
                elif ".gif" in post.url[-5:] or ".gifv" in post.url[-5:] or "gfycat" in post.url or "v.redd.it" in post.url:
                    post.mod.remove()
                    post.reply("""Hello! 
        
Thank you for your submission - Please feel free to re-submit your post to our dedicated fun subreddit r/cryptocurrencymemes.
        
----
        
Memes and Comedy posts are now considered low quality content on this subreddit and will be removed. Repeated attempts to post this type of content on r/cryptocurrency will lead to a subreddit suspension and possibly a ban.\n\n*I am a bot, and this action was performed automatically. Please contact the [moderators of this subreddit](https://www.reddit.com/message/compose?to=%2Fr%2F{0}) if you have any questions or concerns.*""").mod.distinguish(how='yes', sticky=True)
def getCALL():
    pure = json.loads(requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=0').text)
    parsed = [x['name'] for x in pure] + [x['symbol'] for x in pure]
    return parsed
    
done_log_ids = []

def ban_from_logs():
    for log in r.subreddit("cryptocurrency").mod.log(limit=100):
        if 'section 1a' in str(log.details).lower() and log.id not in done_log_ids:
            done_log_ids.append(log.id)
            r.subreddit("cryptocurrency").banned.add(log.target_author, ban_message="Referral links are not allowed in /r/CryptoCurrency!\n\n>{0}".format('https://www.reddit.com'+log.target_permalink), ban_reason="Banned by /u/CryptoModBot")


def purifyList(plist):
    moderators = [str(l).lower() for l in plist[0].subreddit.moderator()]
    return list(filter(lambda x: not (x.stickied or str(x.author).lower() in moderators), plist))
    

tlist_coins = ['']
last_got = [0]


    
while True:
    try:
        if float(time.time()) - float(last_got[0]) > 300:
            last_got[0] = time.time()
            tlist_coins[0] = getCALL()
        all_coins = tlist_coins[0]
        pst = purifyList(list(r.subreddit('CryptoCurrency').new(limit=500)))
        ht_cc = purifyList(list(r.subreddit('CryptoCurrency').hot(limit=25)))
        removeAllComedy(pst)
        removeDuplicates(pst)
        limitCoins(ht_cc, all_coins)
        ban_from_logs()
        #updateSettings()
        #banReferrals()
    except Exception as e:
        print(str(e))

