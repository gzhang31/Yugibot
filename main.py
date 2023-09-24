import discord
from discord import app_commands
from dotenv import load_dotenv
import os
import requests
import json
import card_text
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True


client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    count = 0
    for guild in client.guilds:
        count += 1
        print("Connected to server: ", guild, "(id:", guild.id, ")")
    await tree.sync(guild=discord.Object(id=os.getenv("TEST_GUILD")))
    print("Connected to ", count, "servers")



@tree.command(name="get", description="fetches information about the specified card", guild=discord.Object(id=os.getenv("TEST_GUILD")))
async def slash(interaction: discord.Interaction, name: str):
    print("get command called")
    #requests data from ygoprodeck database api
    response_api = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?fname={fname}".format(fname=name))
    data = response_api.text
    data = json.loads(data)["data"][0]
    #data now contains only the data of the first card from the fuzzy search
    to_discord = card_text.card_str.format(name=data["name"], description=data["desc"], atk=data["atk"], defense=data["def"])

    #create an embeded image with the image url given from the database
    embed = discord.Embed()
    embed.set_image(url=data["card_images"][0]["image_url"])
    embed.add_field(name=data["name"], value=to_discord)
    await interaction.channel.send(embed=embed)


client.run(os.getenv('TOKEN'))