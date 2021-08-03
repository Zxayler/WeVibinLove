from discord.ext.commands import command, Cog, Greedy
from utils.embedUtils import newEmbed, successEmbed, errorEmbed, field
from __database__ import connect, config
from discord.utils import get
from discord import VoiceChannel, CategoryChannel, PermissionOverwrite, Embed
from datetime import datetime as dt
from discord.ext.tasks import loop
import asyncio
from config import connect

db = connect.connect("dating")
c = db.cursor(buffered=True)

c.execute("CREATE TABLE IF NOT EXISTS guilds (guild BIGINT, category BIGINT, channel1 BIGINT, channel2 BIGINT, chname VARCHAR(250), dating SMALLINT)")
c.execute("CREATE TABLE IF NOT EXISTS guildData (guild BIGINT, premium SMALLINT, premium_until DATETIME)")
c.execute("CREATE TABLE IF NOT EXISTS vcdata (vc BIGINT, male BIGINT, female BIGINT, guild BIGINT)")
db.commit()

def getGuildData(guild):
	c.execute("SELECT * FROM guilds WHERE guild = %s", (guild,))
	res = c.fetchone()
	if res is None:
		c.execute("INSERT INTO guilds (guild, category, channel1, channel2, chname, dating) VALUES (%s, %s, %s, %s, %s, %s)", (guild, 0,0,0,"❤ Blind Date",0))
		db.commit()
		return guild, 0,0,0,"❤ Blind Date",0
	return res

def getPremiumData(guild):
	c.execute("SELECT * FROM guildData WHERE guild = %s", (guild,))
	res = c.fetchone()
	if res is None:
		c.execute("INSERT INTO guildData (guild, premium, premium_until) VALUES (%s, %s, %s)",(guild, 0, dt.utcnow()))
		db.commit()
		return guild, 0, dt.utcnow()
	return res

class AutoDatingSystem(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(aliases=['change-auto-vc-name'])
	async def change_default_vc_name(self, ctx, *, name = None):
		p = connect.get_prefix(ctx.message)
		guild, premium, timeout = getPremiumData(ctx.guild.id)
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("Error, you must have `manage server` permissions to use this command."))
		if premium == 0:
			return await ctx.send(embed=errorEmbed("This server is not subscribed to Premium."))
		c.execute("SELECT dating FROM guilds WHERE guild = %s", (ctx.guild.id))
		res = c.fetchone()
		res = list(res)[0]
		if res == 0:
			return await ctx.send(embed=errorEmbed("This server has no blind date system yet. Try making one with `af.setup-blind-date`"))
		if name is None:
			return await ctx.send(embed=errorEmbed("Invalid Arguments, please provide the name of the auto-generated names."))
		if len(name) > 31:
			return await ctx.send(embed=errorEmbed("Bad Argument, name must not be greater than 30 characters."))
		c.execute("UPDATE guilds SET chname = %s WHERE guild = %s", (name, ctx.guild.id))
		db.commit()
		await ctx.send(embed=successEmbed("Successfully set the new auto-generated channel name in this server."))


	@command(aliases=["setup-blind-date"])
	async def setup_blind_date(self, ctx):
		p = connect.get_prefix(ctx.message)
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("Error, you must have `manage server` permissions to use this command."))
		guild, category, channel1, channel2, chname, dating = getGuildData(ctx.guild.id)
		if dating == 1:
			return await ctx.send(embed=errorEmbed("`This server already has an enabled blind date voice channel system, please delete it first using __af.delete-blind-date__`"))
		await ctx.send(embed=newEmbed("Please wait a little while I set this up."))
		bt = get(ctx.guild.members, id = self.bot.user.id)
		if bt.guild_permissions.manage_channels is False:
			return await ctx.send(embed=errorEmbed("Please give me `manage channels` permissions so i can manage the blind date system well."))
		overwrites = {
			bt: PermissionOverwrite(manage_channels=True)
		}
		category = await ctx.guild.create_category("❤ Blind Date")
		ch1 = await ctx.guild.create_voice_channel("Looking for shawty", category=category)
		ch2 = await ctx.guild.create_voice_channel("Looking for boi", category=category)
		c.execute("UPDATE guilds SET category = %s, channel1 = %s, channel2 = %s, dating = 1 WHERE guild = %s",
				  (category.id, ch1.id, ch2.id, guild))
		db.commit()
		
		await ctx.send(embed=successEmbed("Blind date setup was successful, you can now change the category and channel permissions."))
		em = Embed(color=config.color, description=f"**{ctx.guild.name}** server has enabled the blind date system!")
		em.add_field(name=f"Server Count", value=f"I am now currently in {len(self.bot.guilds)} servers", inline=False)
		em.add_field(name="Users", value=f"I am now currently serving {len(self.bot.users)} users")
		await self.channel.send(embed=em)


	@command(aliases=['delete-blind-date'])
	async def delete_blind_date(self, ctx):
		p = connect.get_prefix(ctx.message)
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("Error, you must have `manage server` permissions to use this command."))
		guild, category, channel1, channel2, chname, dating = getGuildData(ctx.guild.id)
		if dating == 0:
			return await ctx.send(embed=errorEmbed("This server has no blind date system yet. Try making one with `af.setup-blind-date`"))
		try:
			await get(ctx.guild.categories, id = category).delete()
			await get(ctx.guild.voice_channels, id=channel1).delete()
			await get(ctx.guild.voice_channels, id=channel2).delete()
		except:
			pass
		c.execute("UPDATE guilds SET category = 0, channel1 = 0, channel2 = 0, dating = 0 WHERE guild = %s", (ctx.guild.id,))
		c.execute("DELETE FROM vcdata WHERE guild = %s", (ctx.guild.id,))
		db.commit()
		c.execute("SELECT vc FROM vcdata Where guild = %s", (ctx.guild.id,))
		vcs = c.fetchall()
		if vcs is not None:
			vc = [v[0] for v in list(vcs)]
			for ch in vc:
				channel = self.bot.get_channel(ch)
				if channel is None:
					continue
				if channel is not None:
					try: 
						await channel.delete()
					except: 
						continue
					continue
		em = Embed(color=0xFF0000, description=f"**{ctx.guild.name}** server has disabled the blind date system!")
		em.add_field(name=f"Server Count", value=f"I am now currently in {len(self.bot.guilds)} servers", inline=False)
		em.add_field(name="Users", value=f"I am now currently serving {len(self.bot.users)} users")
		await self.channel.send(embed=em)
		await ctx.send(embed=successEmbed("Successfully disabled the blind date system."))


	def make_data(self, guild):
		cxn = connect.connect("guilds")
		con = cxn.cursor()
		con.execute("CREATE TABLE IF NOT EXISTS '%s' (vc BIGINT, male BIGINT, female BIGINT)", (guild,))
		cxn.commit()
		return cxn

	@Cog.listener()
	async def on_voice_state_update(self, mem, b, a):
		c.execute("SELECT guild FROM guilds")
		guilds = c.fetchall()
		guilds = [a[0] for a in list(guilds)]
		if mem.guild.id in guilds:
			c.execute("SELECT dating FROM guilds WHERE guild = %s", (mem.guild.id,))
			res = c.fetchone()
			dating = list(res)[0]
			if dating == 0:
				return
			if dating == 1:
				c.execute("SELECT category, channel1, channel2, chname FROM guilds WHERE guild = %s", (mem.guild.id,))
				category, male, female, chname = c.fetchone()
				if a.channel:
					if a.channel.id == male:
						c.execute("SELECT vc FROM vcdata WHERE guild = %s AND male = 0", (mem.guild.id,))
						res = c.fetchone()
						if res is None:
							category = get(mem.guild.categories, id = category)
							overwrites = {mem: PermissionOverwrite(connect=True, view_channel=True), mem.guild.default_role: PermissionOverwrite(view_channel=False)}
							ch = await mem.guild.create_voice_channel(chname, user_limit=2, category=category, overwrites=overwrites)
							c.execute("INSERT INTO vcdata (vc, male, female, guild) VALUES (%s, %s, %s, %s)",(ch.id, mem.id, 0, mem.guild.id))
							db.commit()
							await mem.move_to(ch)
						if res is not None:
							ch = self.bot.get_channel(list(res)[0])
							c.execute("UPDATE vcdata SET male = %s WHERE vc = %s", (mem.id, ch.id))
							db.commit()

							await mem.move_to(ch)
					if a.channel.id == female:
						c.execute("SELECT vc FROM vcdata WHERE guild = %s AND female = 0", (mem.guild.id,))
						res = c.fetchone()
						if res is None:
							category = get(mem.guild.categories, id = category)
							overwrites = {
								mem: PermissionOverwrite(connect=True, view_channel=True),
								mem.guild.default_role: PermissionOverwrite(view_channel=False)
							}
							ch = await mem.guild.create_voice_channel(chname, user_limit=2, category=category, eoverwrits=overwrites)
							c.execute("INSERT INTO vcdata (vc, male, female, guild) VALUES (%s, %s, %s, %s)",(ch.id, 0, mem.id, mem.guild.id))
							db.commit()
							await mem.move_to(ch)
						if res is not None:
							ch = self.bot.get_channel(list(res)[0])
							await mem.move_to(ch)
							c.execute("UPDATE vcdata SET female = %s WHERE vc = %s", (mem.id, ch.id))
							db.commit()
				if b.channel:
					if b.channel.name == chname:
						
						vc = self.bot.get_channel(b.channel.id)
						if vc is None:
							return
						if not len(vc.members):
							try: 
								await vc.delete()
							except:
								pass
							c.execute("DELETE FROM vcdata WHERE vc = %s", (vc.id,))
							db.commit()
							return
						if len(vc.members) == 1:
							c.execute("SELECT male, female FROM vcdata WHERE vc = %s", (vc.id,))
							male, female = c.fetchone()
							if mem.id == male:
								c.execute("UPDATE vcdata SET male = 0 WHERE vc = %s", (vc.id,))
							if mem.id == female:
								c.execute("UPDATE vcdata SET female = 0 WHERE vc = %s", (vc.id,))
							db.commit()
							return

	@command()
	async def tutorial(self, ctx):
		embed = newEmbed("Don't know how to set up up the bot?\nFollow the steps below. You can use `af.invite`, `af.help`, and `af.support` for more information.")
		embed.title = "Bot Setup"
		embed.add_field(name="Step 1",
						value="Use `af.setup-blind-date` to set up the blind date category, it will automatically create one for you",
						inline=False)
		embed.add_field(name="Step 2",
						value="This step is optional, change the channel names ang category names into whatever you like!",
						inline=False)
		embed.set_thumbnail(url=self.bot.user.avatar_url)
		embed.add_field(name="if you want to disable it,",
						value="Use `af.delete-blind-date` to disable it, it will automatically delete the category and the channels within it.")
		await ctx.send(embed=embed)



	@Cog.listener()
	async def on_ready(self):
		self.channel = self.bot.get_channel(850685866003005460)
		self.update_vc_data.start()

	@loop(seconds = 30)
	async def update_vc_data(self):
		c.execute("SELECT vc FROM vcdata")
		res = c.fetchall()
		res = [r[0] for r in list(res)]
		for ch in res:
			vc = self.bot.get_channel(ch)
			if vc is None:
				c.execute("DELETE FROM vcdata WHERE vc = %s", (ch,))
				db.commit()
				continue
			if not(len(vc.members)):
				c.execute("DELETE FROM vcdata WHERE vc = %s", (ch,))
				db.commit()
				await vc.delete()
				continue
		print("Updated VC Data")


def setup(bot):
	bot.add_cog(AutoDatingSystem(bot))