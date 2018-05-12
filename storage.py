SRC = '''# u/CryptoModBot Config


### Blacklists

---
###### Section 1A - Blacklist Regex

`\?ref=\w+`

---

### Ban Settings 



####**Note:** Only change the numbers in the section below. Do not change any of the text. If you change any of the text, it will be rejected as invalid and reverted automatically by the bot. The actual code is only updated every 5 minutes, so please be patient after pushing a change. Whole numbers only!

$-- Ban a user who posts a referral link for a month, only if their account:

- Is less than `60` days old OR

- Has made fewer than `30` prior comments/posts to /r/CryptoCurrency 

Otherwise, issue a temporary ban that is `14` days long. --$'''