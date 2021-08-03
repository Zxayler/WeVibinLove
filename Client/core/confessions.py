from discord.ext.commands import command, Cog, is_owner
from discord import Member, Embed, TextChannel, Role, Color, File
from __database__ import connect
from utils.embedUtils import successEmbed, errorEmbed, newEmbed
from discord.utils import get
import asyncio
from discord_components import *
from __database__ import config
import re
import random

colors = [0x1abc9c, 0x11806a, 0x2ecc71, 0x1f8b4c,
		  0x3498db, 0x206694, 0x9b59b6, 0x71368a,
		  0xe91e63, 0xad1457, 0xf1c40f, 0xc27c0e,
		  0xe67e22, 0xe67e22, 0xe74c3c, 0x992d22,
		  0x95a5a6, 0x607d8b, 0x607d8b, 0x979c9f,
		  0x979c9f, 0x546e7a, 0x546e7a, 0x7289da,
		  0x99aab5, 0x36393F]

db = connect.db
c = connect.c

c.execute("CREATE TABLE IF NOT EXISTS confessions (guild BIGINT, channel BIGINT, num BIGINT, title VARCHAR(50), minchar BIGINT, maxchar BIGINT, images SMALLINT, logs BIGINT, color VARCHAR(10))")
db.commit()

def get_data(guild):
	c.execute("SELECT guild, channel, num, title, minchar, maxchar, images, logs, color FROM confessions WHERE guild = %s", (guild,))
	res = c.fetchone()
	if res is None:
		c.execute("INSERT INTO confessions (guild, channel, num, title, minchar, maxchar, images, logs, color) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
				  (guild, 0, 1, "Confession #{num}", 0, 2000, 0, 0, "random"))
		db.commit()
		return guild, 0, 1, "Confession #{num}", 0, 2000, 0, 0, "random"
	return res

nums = [x for x in range(100)]
nums.pop(0)

class WeVibinConfessions(Cog, name="Confessions"):
	def __init__(self, bot):
		self.bot = bot 

	@command(aliases=["setup-confession"], description="Sets up a confession in a channel.", usage="setup-confession <channel>")
	async def setup_confession(self, ctx, channel: TextChannel = None):
		if not ctx.guild: return
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("You have no permissions to use this command."))
		if channel is None:
			return await ctx.send(embed=errorEmbed("You did not provide any channel, use `setup-confession <channel>`"))
		if not ctx.guild.me.permissions_in(channel):
			return await ctx.send(embed=errorEmbed("I have no permissions to the channel you mentioned. Please give me `send messages`, `embed links`, and `attach files` permissions."))
		get_data(ctx.guild.id)
		c.execute("UPDATE confessions SET channel = %s WHERE guild = %s", (channel.id,ctx.guild.id))
		db.commit()
		return await ctx.send(embed=successEmbed(f"Successfully set the confession in {channel.mention}"))

	@command(aliases=["set-confession-logs"], description="Sets up the logs of the confession.", usage="setup-confession-logs <channel>")
	async def set_confession_logs(self, ctx, channel: TextChannel = None):
		if not ctx.guild: return
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("You have no permissions to use this command."))
		if channel is None:
			return await ctx.send(embed=errorEmbed("You did not provide any channel, use `set-confession-logs <channel>`"))
		if not ctx.guild.me.permissions_in(channel):
			return await ctx.send(embed=errorEmbed("I have no permissions to the channel you mentioned. Please give me `send messages`, `embed links`, and `attach files` permissions."))
		get_data(ctx.guild.id)
		c.execute("UPDATE confessions SET logs = %s WHERE guild = %s", (channel.id, ctx.guild.id))
		db.commit()
		return await ctx.send(embed=successEmbed(f"Successfully set the confession logs in {channel.mention}"))

	@command(aliases=["set-confession-title"], description="Sets the confession title in the Embed, you must put `{num}` in it.", usage="setup-confession-title <title>")
	async def set_confession_title(self, ctx, *, title = None):
		if not ctx.guild: return
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("You have no permissions to use this command."))
		if title is None:
			return await ctx.send(embed=errorEmbed("You did not provide the title. Use `set-confession-title <title>`"))
		if len(title) > 50:
			return await ctx.send(embed=errorEmbed("Title must only be less than 50 characters long."))
		if not "{num}" in title:
			return await ctx.send(embed=errorEmbed("You must have a `{num}` in your title for the confession number"))
		get_data(ctx.guild.id)
		c.execute("UPDATE confessions SET title = %s WHERE guild = %s", (title, ctx.guild.id))
		db.commit()
		return await ctx.send(embed=successEmbed(f"Successfully set the title to:\n\n**{title.replace('{num}', '69')}**"))

	@command(aliases=["set-min-characters"], description="Sets the minimum character length of the confession", usage="set-min-characters <number>")
	async def set_min_characters(self, ctx, minimum = None):
		if not ctx.guild: return
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("You have no permissions to use this command."))
		if minimum is None:
			return await ctx.send(embed=errorEmbed("You did not provide the minimum character length integer"))
		if not minimum.isdigit():
			return await ctx.send(embed=errorEmbed("You did not provide an integer for the minimum character length"))
		if int(minimum) < 0 or int(minimum) > 500:
			return await ctx.send(embed=errorEmbed("Minimum character length must be in between `10-500`"))
		get_data(ctx.guild.id)
		c.execute("UPDATE confessions SET minchar = %s WHERE guild = %s", (int(minimum), ctx.guild.id))
		db.commit()
		return await ctx.send(embed=successEmbed(f"Successfully set the minimum character length of confession in this server!\n\nMinimum character length: `{minimum}`"))

	@command(aliases=["set-max-characters"], description="Sets the maximum character length of the confession", usage="set-max-characters <number>")
	async def set_max_characters(self, ctx, maximum = None):
		if not ctx.guild: return
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("You have no permissions to use this command."))
		if maximum is None:
			return await ctx.send(embed=errorEmbed("You did not provide the maximum character length integer"))
		if not maximum.isdigit():
			return await ctx.send(embed=errorEmbed("You did not provide an integer for the maximum character length"))
		if int(maximum) < 200 or int(maximum) > 2000:
			return await ctx.send(embed=errorEmbed("Maximum character length must be in between `10-500`"))
		get_data(ctx.guild.id)
		c.execute("UPDATE confessions SET maxchar = %s WHERE guild = %s", (int(maximum), ctx.guild.id))
		db.commit()
		return await ctx.send(embed=successEmbed(f"Successfully set the maximum character length of confession in this server!\n\nMaximum character length: `{maximum}`"))

	@command(aliases=["set-confession-images"], description="Enables of Disables images in a confession. It defaults to `disabled`", usage="set-confession-images")
	async def set_images(self, ctx):
		if not ctx.guild: return
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("You have no permissions to use this command."))
		get_data(ctx.guild.id)
		c.execute("SELECT images FROM confessions WHERE guild = %s", (ctx.guild.id,))
		res = c.fetchone()
		images = list(res)[0]
		if images == 0:
			c.execute("UPDATE confessions SET images = 1 WHERE guild = %s", (ctx.guild.id,))
			await ctx.send(embed=successEmbed("Successfully `ENABLED` adding images in confessions."))
		if images == 1:
			c.execute("UPDATE confessions SET images = 0 WHERE guild = %s", (ctx.guild.id,))
			await ctx.send(embed=successEmbed("Successfully `DISABLED` adding images in confessions."))

		db.commit()

	@command(aliases=["reset-confession-number"], description="Resets the confession number to `1`", usage="reset-confession-number")
	async def reset_confession_number(self, ctx):
		if not ctx.guild: return
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("You have no permissions to use this command."))
		guild, channel, num, title, minchar, maxchar, images, logs, color = get_data(ctx.guild.id)
		if channel == 0:
			return await ctx.send(embed=errorEmbed("You didn't set up the confession channel in this server yet. Use `setup-confession <channel>`"))
		c.execute("UPDATE confessions SET num = 1 WHERE guild = %s", (ctx.guild.id,))
		db.commit()
		return await ctx.send(embed=successEmbed("Successfully reset the confession number to `1`"))

	@command(aliases=["delete-confession"], description="Deletes the confession data", usage="delete-confession")
	async def delete_confession(self, ctx):
		if not ctx.guild: return
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("You have no permissions to use this command."))
		guild, channel, num, title, minchar, maxchar, images, logs, color = get_data(ctx.guild.id)
		if channel == 0:
			return await ctx.send(embed=errorEmbed("You didn't set up the confession channel in this server yet. Use `setup-confession <channel>`"))
		c.execute("DELETE FROM confessions WHERE guild = %s", (ctx.guild.id,))
		db.commit()
		return await ctx.send(embed=successEmbed("Successfully deleted confession data."))

	@command(aliases=["set-confession-color"], description="Sets the confession color, you can use `random` or search the hex code in google", usage="set-confesstion-color <random | hex code>")
	async def set_confession_color(self, ctx, color = None):
		if not ctx.guild: return
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send(embed=errorEmbed("You have no permissions to use this command."))
		if color is None:
			return await ctx.send(embed=errorEmbed("You did not provide the hex color code, must start with `#` or you can use `random`"))
		if color.lower() == "random":
			c.execute("UPDATE confessions SET color = %s WHERE guild = %s", (color, ctx.guild.id))
			db.commit()
			return await ctx.send(embed=successEmbed("Successfully set the confession color to `random`"))
		if not color.startswith("#"):
			return await ctx.send(embed=errorEmbed("the hex color code must start with `#`"))
		match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
		if not match:
			return await ctx.send(embed=errorEmbed("the hex color code you provided is invalid."))
		get_data(ctx.guild.id)
		c.execute("UPDATE confessions SET color = %s WHERE guild = %s", (color, ctx.guild.id))
		db.commit()
		return await ctx.send(embed=successEmbed(f"Successfully set the confession color to `{color}`"))


	@command(description="Confess command.", usage="confess <message>")
	async def confess(self, ctx, *, message = None):
		if ctx.guild: return
		if message is None:
			return await ctx.send(embed=errorEmbed("You did not provide the message you want to confess."))
		guilds = ctx.author.mutual_guilds
		gld = []
		for guild in guilds:
			c.execute("SELECT channel FROM confessions WHERE guild = %s and channel != 0", (guild.id,))
			res = c.fetchone()
			if res is None:
				continue
			gld.append([guild.id, list(res)[0]])
			continue
		if not len(gld):
			return await ctx.send(embed=newEmbed("There are no servers you are in that has an enabled confession."))
		glds = [f"{nums[idx]}).**{self.bot.get_guild(i[0])}**: {self.bot.get_channel(i[1])}" for idx, i in enumerate(gld)]
		chunks = [list(glds)[i:i + 20] for i in range(0, len(list(glds)), 20)]
		for i in chunks:
			em = newEmbed("\n\n".join(i))
			em.title = "Choose the number that corresponds to the server you want to confess in. You have 60 Seconds."
			em.set_footer(text=f"{self.bot.user.name}")
			await ctx.send(embed=em)
		try:
			m = await self.bot.wait_for("message", timeout=60.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
			if not m.content.isdigit():
				return await ctx.send(embed=errorEmbed("You did not provide a proper integer or position of the server."))
			if int(m.content)-1 > len(gld) or int(m.content) < 0:
				return await ctx.send(embed=errorEmbed("You provided an invalid position."))
			guild, channel, num, title, minchar, maxchar, images, logs, color = get_data(gld[int(m.content)-1][0])
			if len(message) < minchar:
				return await ctx.send(embed=errorEmbed(f"Minimum character length must be `{minchar}`.").set_footer(text="minimum character defaults to 10 can be unique in a specific server."))
			if len(message) > maxchar:
				return await ctx.send(embed=errorEmbed(f"Maximum character length must be `{maxchar}`.").set_footer(text="maximum character defaults to 2000 can be unique in a specific server."))
			clr = random.choice(colors)
			if color != "random":
				clr = config.get_color(color)
			
			em = Embed(color=clr, description=message, title=title.replace("{num}", str(num))).set_footer(text="DM me `af.confess` to confess.")
			ch = self.bot.get_channel(channel)
			if len(ctx.message.attachments):
				if images == 1:
					em.set_image(url=ctx.message.attachments[0].url)
			try: await ch.send(embed=em)
			except: return await ctx.send(embed=errorEmbed("I can't send your message to the confession channel, maybe it does not exist or i do not have permissions"))
			if logs != 0:
				lgs = self.bot.get_channel(logs)
				if lgs is not None:
					await lgs.send(embed=em, content=f"{ctx.author.mention}\nID: `[{ctx.author.id}]`")
			c.execute("UPDATE confessions SET num = num + 1 WHERE guild = %s", (guild,))
			db.commit()
			await ctx.send(embed=successEmbed(f"Successfully sent your confession to {ch.mention}"))
		except asyncio.TimeoutError:
			return await ctx.send("Command Cancelled. You did not respond in time.")


def setup(bot):
	bot.add_cog(WeVibinConfessions(bot))