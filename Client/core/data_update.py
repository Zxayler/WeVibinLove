from discord.ext.commands import command, Cog
from discord import Embed 
from pymongo import MongoClient
import json
from __database__ import config, connect

#cluster = MongoClient("mongodb+srv://admin:mongonichampo123@fierycord.2xosa.mongodb.net/BotData?retryWrites=true&w=majority")
#db = cluster["BotData"]
#c = db['guildData']

class BotUpdate(Cog, name="Bot Update"): #UUpdates some data into a mongo db
	def __init__(self, bot):
		self.bot = bot 

	@Cog.listener()
	async def on_guild_join(self, guild):
		em = Embed(color=config.color, description=f"**I joined {guild.name}**\n\n**Members**: {len(guild.members)}")
		em.add_field(name=f"Server Count", value=f"I am now currently in {len(self.bot.guilds)} servers", inline=False)
		em.add_field(name="Users", value=f"I am now currently serving {len(self.bot.users)} users.")
		await self.channel.send(embed=em)
	#	c.update_one({"_id": "zxayler"}, {"$set": {"servers": len(self.bot.guilds), "users": len(self.bot.users)}})

	@Cog.listener()
	async def on_member_join(self, member):
		pass
	#	c.update_one({"_id": "zxayler"}, {"$set": {"servers": len(self.bot.guilds), "users": len(self.bot.users)}})

	@Cog.listener()
	async def on_ready(self):
		self.channel = self.bot.get_channel(850685866003005460)
	#	c.update_one({"_id": "zxayler"}, {"$set": {"servers": len(self.bot.guilds), "users": len(self.bot.users)}})
	

def setup(bot):
	bot.add_cog(BotUpdate(bot))