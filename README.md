# SNIPER GAME DISCORD BOT

This is a bot for a game played on a few UCLA student discord servers. This bot serves the purpose of keeping track of the leaderboard, also as a database exercise for myself.

The game itself involves taking a photo of an unsuspecting player when running across them, without them noticing, and posting said photo in chat to score a point.

Code is currently a work in progress and pretty garbage, use at your own risk. Bot token should be found in the credentials.py file
## User Guide
snipe @mention - snipe another user. Note there can be multiple @mentions, and it will record a snipe for each. Note this will work for anything with snipe at the beginning and an @mention

snipe leaderboard - shows a leaderboard of top snipers and snipees

snipe rank - Shows your own stats and KDR

snipe admin setChannel - sets a channel where this bot can be run

snipe admin removeChannel - removes channel where this bot can be run

snipe admin void <messageID> - voids all snipes recorded by some message ID

Admin commands require server administrator priviledges.
