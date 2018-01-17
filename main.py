# -*- coding: utf-8 -*-
D1 = False 
import praw 
import pprint
import re
import time
from storage import SRC

settings = {'referrals':[], 'tempban': None, 'agemin': None, 'postmin': None, 'lastUpdated': 0, 'source':''}
settings['source'] = SRC
def containsReferral(text):
    return bool(re.search('|'.join(referrals), text))

r = praw.Reddit()
                     

SUBREDDIT = 'CryptoCurrency' #subreddit to run in

referrals = ["etheress.net","eth2usd.com", "futurether.com", "flyether.com", "ethereumexchange.net", "ninether.com", "livecoinchart.net", "bitcoinlondon.org", "stratoon.net", "btclondon.org", "bitcoinat.co.uk", "bitcoinasia.net", "btccc.space", "bitcoina.pw", "asibit.space", "chintra.bid", "tradingchin.win", "cryptofi.cricket", "moneytrad.party", "ficrypto.science", "xchngch.men", "btctr.racing", "zonesbtc.info", "srbtc.info", "sbtc.world", "storeofvalue.github.io", "bitcoinatrade.com", "xtradechina.net", "changecrypto.info", "trkclck.rocks", "ethereumx.site", "tradeethereum.science", "standpointresearch.com", "CoinPump.Group", "palmbeachgroup.com", "hacked.com", "goldreward.io", "wixsite.com", "ethconnect.net", "bitrapidus.com", "71republic.com", "mycryptonews.info", "coincodex.com", "ltd0.com","coin7t.com","cryptoanalyst.co", "tangleblog.com", "actioncoin.io", "twitter.com/tangleblog", "emining.club", "sphere.social", "wcibtc.com", "twitter.com/officialmcafee", "kucoin.com", "dadi.cloud/r/", "travelflex.org/?ref=", "vrlps.co/", "upcoin.com/", "digitexfutures.com", "freedoge.co.in/", "https://www.hoqu.io/?ref_id=", "https://www.binance.com/?ref="]  #list of banned links 
hot_posts = []

def checkHot():
    all_hot = []
    for post in r.subreddit(SUBREDDIT).hot(limit=25):
        if post.link_flair_text == 'COMEDY':
            all_hot.append(post.id) 
            if len(hot_posts) < 2:
                if post.id not in hot_posts:
                    hot_posts.append(post.id)
            elif post.id not in hot_posts:
                print('Removing ' + post.shortlink)
                post.mod.remove()
                c = post.reply('''Thank you for submitting to /r/{0},\n\nTo improve 
                the quality of content on the top page, rising comedy posts are occasionally removed if 
                the subreddit is already overpopulated with similar submissions. Please consider posting 
                comedy content to r/CryptoCurrencyMemes, r/CryptoHumor, or as a comment in the [daily thread]
                (https://www.reddit.com/r/CryptoCurrency/search?q=flair%3AGeneral+Discussion&restrict_sr=on&sort=new&t=all) 
                instead.\n\n*I am a bot, and this action was performed automatically. Please contact the [moderators of 
                this subreddit](https://www.reddit.com/message/compose?to=%2Fr%2F{0}) if you have any 
                questions or concerns.*'''.format(SUBREDDIT))
                c.mod.distinguish(how='yes', sticky=True)
                all_hot.remove(post.id)
        hot_posts[:] = list(set(hot_posts).intersection(all_hot))
            
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
    referrals = re.findall('\[.+?\]', banned_links)[0].replace('"','').split(',')
    agemin, postmin, tempban = re.findall('\d+', re.findall('(\$--(.|\s)+?--\$)', ban_data)[0][0])
    return referrals, int(tempban), int(agemin), int(postmin)

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
                settings['referals'], settings['tempban'], settings['agemin'], settings['postmin'] = parseWikiPage(source)
                settings['lastUpdated'] = time.time()
                settings['source'] = wikipage.content_md
                print("Valid Updated Completed")
            except:
                badUpdate(wikipage)
                

while True:
    try:
        checkHot()
        #updateSettings()
        #banReferrals()
    except Exception as e:
        print(str(e))