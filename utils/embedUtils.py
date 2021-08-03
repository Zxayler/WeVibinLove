from discord import Embed
from __database__ import config
from discord_components import *

def newEmbed(content):
	return Embed(color=config.color,
				 description=content).set_footer(text="We Vibin")

def errorEmbed(content):
	return Embed(title=":x: Error!",
				 description=content,
				 color=0xFF0000).set_footer(text="We Vibin")

def successEmbed(content):
	return Embed(title="✔ Success!",
				 description=content,
				 color=0x00FF00).set_footer(text="We Vibin")

def field(embed, name, value, inline = False):
	embed.add_field(name=name,
					value=value,
					inline=inline)
	return embed

def redButton(label):
	return Button(label=label, style=ButtonStyle.red)
	
	
def blueButton(label):
	return Button(label=label, style=ButtonStyle.blue)
	
	
def urlButton(label):
	return Button(label=label, style=ButtonStyle.URL)
	
	
def greenButton(label):
	return Button(label=label, style=ButtonStyle.green)


def grayButton(label):
	return Button(label=label, style=ButtonStyle.gray)