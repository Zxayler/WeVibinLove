import json
from PIL.ImageColor import getrgb
from discord import Embed, Color

with open("./__database__/config.json") as f:
	data = json.load(f)

color = 0xE65C9C
token = data['token']
invite = "https://discord.com/api/oauth2/authorize?client_id=849177419520147496&permissions=17826832&scope=bot"

vote = "https://top.gg/bot/849177419520147496/vote"

def get_color(color):
	r,g,b = getrgb(color)
	return Color.from_rgb(r,g,b)