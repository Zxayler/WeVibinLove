from discord.ext.commands import command, Cog
from discord import Embed, Member, VoiceChannel, Status, Activity, ActivityType, ChannelType
from __database__ import connect, config
from utils.embedUtils import newEmbed, successEmbed, errorEmbed, field, redButton, grayButton, blueButton, greenButton, urlButton
from discord.ext.tasks import loop
import asyncio
from datetime import datetime, timedelta
from discord_components import *

db = connect.db
c = connect.c

c.execute("CREATE TABLE IF NOT EXISTS prefix (guild BIGINT, prefix VARCHAR(5))")
db.commit()

class PremiumHandler(Cog, name="Miscellaneous"):
	def __init__(self,bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		await asyncio.sleep(10)
		self.change_presence.start()

	@loop(seconds=20)
	async def change_presence(self):
		users = len(self.bot.users)
		servers = len(self.bot.guilds)
		arg = f"af.help | {'{:,}'.format(users)} users | {'{:,}'.format(servers)} servers"
		await self.bot.change_presence(status=Status.online,
								   activity=Activity(type=ActivityType.watching,
								   					 name=arg))

	@command(description="Shows you this message", usage="help")
	async def help(self, ctx):
		p = connect.get_prefix(ctx.message)
		categories = list(filter(lambda cog: len(cog.get_commands()), list(self.bot.cogs.values())))
		commands = []
		index = 0
		page = 1
		for cog in categories:
			em = Embed(color=config.color, title=f"{cog.qualified_name} Commands")
			for com in cog.get_commands():
				em.add_field(name=f"{p}{com.usage}", value=f"{com.description}", inline=False)
			em.set_footer(text=f"Page {page}/{len(categories)}")
			em.description = f"This are all the commands for {self.bot.user.name}\n\nBot prefix is `{p}`"
			page += 1
			commands.append(em)
		m = await ctx.send(embed=commands[index], components=[[blueButton("Previous"), greenButton("Next"), redButton("Cancel")]])
		while True:
			try:
				inter = await self.bot.wait_for("button_click", timeout=60.0, check=lambda i: i.message == m)
				if inter.user.id != ctx.author.id:
					await inter.respond(type=6)
				if inter.component.label == "Previous":
					index -= 1
					if index < 0:
						index = 0
						await inter.respond(type=6)
						continue
					await m.edit(embed=commands[index])
				if inter.component.label == "Next":
					index += 1
					if index > len(commands)-1:
						index = len(commands) -1
						await inter.respond(type=6)
						continue
					await m.edit(embed=commands[index])
				if inter.component.label == "Cancel":
					await m.delete()
					await inter.respond(type=6)
					return await ctx.send("Command Cancelled.")
			except asyncio.TimeoutError:
				return await m.delete()


	@command(description="Shows you the prefix of the bot", usage="prefix")
	async def prefix(self, ctx):
		p = connect.get_prefix(ctx.message)
		em = newEmbed(f"Prefix: {p}")
		await ctx.send(embed=em)

	@command(aliases=["prefix-set"], description="Sets your prefix, must be less than 5 characters and mus not contain white spaces", usage="prefix-set <prefix>")
	async def prefix_set(self, ctx, *, prefix):
		if not ctx.guild:
			return
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("You do not have `manage server` permissions to use this command."))
		p = connect.get_prefix(ctx.message)
		if prefix is None:
			return await ctx.send(embed=errorEmbed("You did not provide the prefix.."))
		if len(prefix) > 5:
			return await ctx.send(embed=errorEmbed("Prefix must not be more than 5 characters."))
		if " " in prefix:
			return await ctx.send(embed=errorEmbed("Prefix must not contain white spaces."))
		c.execute("UPDATE prefix SET prefix = %s WHERE guild = %s", (prefix, ctx.guild.id))
		db.commit()
		return await ctx.send(embed=successEmbed(f"Successfully set the server prefix to `{prefix}`"))

	@command(description="Shows you the Bot Info", usage="info")
	async def info(self, ctx):
		em = Embed(color=config.color)
		em.set_author(name=f"{self.bot.user.name} Bot Information")
		fields = [("Name", self.bot.user.name),
				  ("ID", self.bot.user.id),
				  ("Language", "Python 3.9.5"),
				  ("Version", "1.2.0 Beta"),
				  ("Developer", "Zxayler#0001"),
				  ("Github", "[link](https://github.com/Zxayler/Aficionado)"),
				  ("Others", f"[Support Server](https://discord.gg/RYj7cbQWa4) | [Website](https://fierycord.com) | [Invite this bot.]({config.invite}) | [Vote for this bot]({config.vote})")]

		for n, v in fields:
			em.add_field(name=n, value=v, inline=False)
		em.set_thumbnail(url=self.bot.user.avatar_url)
		em.set_footer(text=self.bot.user.name)
		await ctx.send(embed=em)

	@command(description="Displayes the Invite Link of our support server", usage="support")
	async def support(self, ctx):
		embed= newEmbed("**Join the support server [here](https://discord.gg/RYj7cbQWa4)**\n\nWe have tons of bots developed just for you!")
		embed.set_thumbnail(url=self.bot.user.avatar_url)
		await ctx.send(embed=embed)

	@command(description="Gives you the invite link of the bot", usage="invite")
	async def invite(self, ctx):
		em = newEmbed(f"Thank you for inviting this bot to your server. {self.bot.user.name} is a utility discord Event Bot and can be used for blind date events!")
		em.add_field(name="Invite Link", value=f"[{self.bot.user.name} Invite]({config.invite})\n\n\nThese permissions are needed to maintain ang monitor the my features well.", inline=False)
		em.add_field(name="Vote this Bot", value=f"[vote link]({config.vote})")
		em.set_footer(text=self.bot.user.name)
		await ctx.send(embed=em)

	@command(description="Shows you the API and Bot Latency", usage="ping")
	async def ping(self, ctx):
		em = Embed(color=config.color, title="Latency")
		em.set_footer(text=self.bot.user.name)
		em.add_field(name="Bot Latency", value=str(int(float((datetime.utcnow()-ctx.message.created_at).total_seconds()*1000)))+" ms", inline=True)
		em.add_field(name="API Latency", value=f"{int(self.bot.latency*1000)} ms")
		await ctx.send(embed=em)

def setup(bot):
	bot.add_cog(PremiumHandler(bot))