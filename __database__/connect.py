from mysql.connector import connect as cxn
from discord.ext import commands
import json

with open("./__database__/config.json") as f:
	data = json.load(f)

host = data['endpoint']
user = data['host']
passwd = data['passwd']

def connect(database: str):
	db = cxn(
			host = host,
			user = user,
			passwd = passwd
		)
	c = db.cursor()
	c.execute("CREATE DATABASE IF NOT EXISTS ?".replace("?", database))
	db.commit()
	db = cxn(
			host = host,
			user = user,
			passwd = passwd,
			database = database
		)
	return db

db = connect("dating")
c = db.cursor()

from pymongo import MongoClient

def get_prefix(msg):
	db = connect("dating")
	c = db.cursor()
	if msg.guild:
		c.execute("SELECT guild, prefix FROM prefix WHERE guild = %s", (msg.guild.id,))
		res = c.fetchone()
		if res is None:
			c.execute("INSERT INTO prefix (guild, prefix) VALUES (%s, %s)", (msg.guild.id, "af."))
			db.commit()
			return "af."
		return list(res)[1]
	else:
		return "af."


