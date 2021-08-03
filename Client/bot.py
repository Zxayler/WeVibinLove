from discord.ext.commands import AutoShardedBot, when_mentioned_or
from discord import Intents, Status, Activity, ActivityType
from pathlib import Path
from __database__ import config, connect
from discord_components import *


def get_prefix(bot, msg):
	extras = connect.get_prefix(msg)
	return when_mentioned_or(extras)(bot, msg)

class Aficionado(AutoShardedBot):
	def __init__(self):
		self.core = [core.stem for core in Path(".").glob("./Client/core/*.py")]
		self.owner_ids = [
			718677972638236682,
			325544798964547588,
			325544798964547588
		]
		super().__init__(command_prefix=get_prefix,
						 case_insensitive=True,
						 strip_after_prefix=True,
						 intents=Intents.all())


	def setup_client(self):
		self.remove_command('help')
		for core in self.core:
			self.load_extension(f'Client.core.{core}')
		
		print("Setting up bot")

	def runClient(self):
		self.setup_client()
		super().run(config.token, reconnect=True)

	async def on_ready(self):
		users = len(self.users)
		servers = len(self.guilds)
		arg = f"af.help | {'{:,}'.format(users)} users | {'{:,}'.format(servers)} servers"
		await self.change_presence(status=Status.online,
								   activity=Activity(type=ActivityType.watching,
								   					 name=arg))
		print(f"Connected to discord as {self.user.name}\n\nPing:{int(self.latency*1000)} ms")
		DiscordComponents(self)

	async def close(self):
		print(f"{self.user.name} is now closed.")

	
