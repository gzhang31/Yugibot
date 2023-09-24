import discord
from discord import app_commands
from dotenv import load_dotenv
import os
import requests
import json
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


def create_embed_spell(embed, data):
    #TODO
    return

def create_embed_trap(embed, data):
    #TODO
    return

def create_embed_monster(embed, data):
    embed.set_image(url=data["card_images"][-1]["image_url"])
    embed.add_field(name=data["name"], value=data["desc"], inline=False)
    embed.add_field(name="{race}/{attribute}".format(race=data["race"], attribute=data["attribute"]), value="")
    embed.add_field(name="", value="Archetype: {archetype}".format(archetype=(data["archetype"] if "archetype" in data else "None")))
    embed.add_field(name="ATK/{attack} DEF/{defense}".format(attack=data["atk"], defense=data["def"]), value="", inline=False)
    return


@tree.command(name="get", description="Fetches information about the specified card", guild=discord.Object(id=os.getenv("TEST_GUILD")))
async def get(interaction: discord.Interaction, name: str):
    print("get command called")
    #requests data from ygoprodeck database api
    response_api = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?name={name}".format(name=name))
    data = response_api.text
    #TODO: if no cards were found, give a list of possible cards
    data = json.loads(data)["data"][0]
    #data now contains only the data of the first card from the search

    #create an embeded image based on card type
    embed = discord.Embed()
    if(data["type"]=="Spell Card"):
        create_embed_spell(embed, data)
    elif(data["type"]=="Trap Card"):
        create_embed_trap(embed, data)
    else:
        create_embed_monster(embed, data)


    # await interaction.channel.send(embed=embed)
    await interaction.response.send_message(embed=embed)

client.run(os.getenv('TOKEN'))