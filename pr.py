import discord
from discord.ext import commands
from mysql.connector import connect as cxn

def connect(database: str):
	db = cxn(
			host = "thecamp.cpsih6augwli.us-east-2.rds.amazonaws.com",
			user = "admin",
			passwd = "thecamp2020Discord"
		)
	c = db.cursor()
	c.execute("CREATE DATABASE IF NOT EXISTS ?".replace("?", database))
	db.commit()
	db = cxn(
			host = "thecamp.cpsih6augwli.us-east-2.rds.amazonaws.com",
			user = "admin",
			passwd = "thecamp2020Discord",
			database = database
		)
	return db

db = connect("prefix")
c = db.cursor()

c.execute("CREATE TABLE IF NOT EXISTS prefix (guild BIGINT, prefix VARCHAR(5))")
db.commit()

def get_prefix(bot, msg):
	if msg.guild:
		c.execute("SELECT guild, prefix FROM prefix WHERE guild = %s", (msg.guild.id,))
		res = c.fetchone()
		if res is None:
			c.execute("INSERT INTO prefix (guild, prefix) VALUES (%s, %s)", (msg.guild.id, "af."))
			db.commit()
			return commands.when_mentioned_or("af.")(bot, msg)
		return commands.when_mentioned_or(list(res)[1])(bot, msg)

bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())

@bot.command()
async def prefixset(ctx, prefix = None):
	if prefix is None:
		return await ctx.send("Please provide the prefix.")
	if len(prefix) > 5:
		return await ctx.send("Prefix must not be more than 5 characters")
	if " " in prefix:
		return await ctx.send("Prefix must not contain white spaces")
	c.execute("UPDATE prefix SET prefix = %s WHERE guild = %s", (prefix, ctx.guild.id))
	db.commit()
	return await ctx.send(f"Successfully set the prefix into {prefix}")

@bot.event
async def on_ready():
	print("Ready")

bot.run("ODYwNDU3NDkwNDE0ODI5NTc4.YN7hfA.RcVfAhz9enICBT0xUfoSjpN3-ZE")