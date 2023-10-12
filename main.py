import discord
from discord import app_commands
from dotenv import load_dotenv
import os
import requests
import json
from icons import *
load_dotenv()

FUZZY_SHOW_MAX = 5

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

def add_embed_spell(embed, data):
    embed.add_field(name="{name} {icon}".format(name=data["name"], icon=attribute_icons["Spell"]), value=data["desc"], inline=False)
    embed.add_field(name="{race} Spell {icon}".format(icon=spell_trap_icons[data["race"]], race=data["race"]), value="")
    return

def add_embed_trap(embed, data):
    embed.add_field(name="{name} {icon}".format(name=data["name"], icon=attribute_icons["Trap"]), value=data["desc"], inline=False)
    embed.add_field(name="{race} Trap {icon}".format(icon=spell_trap_icons[data["race"]], race=data["race"]), value="")
    return

def add_embed_monster(embed, data):
    #default to use level. If xyz or link monster, use respective name
    level_type = "Level "
    if("XYZ" in data["type"]):
        level_type = "Rank "
    elif("Link" in data["type"]):
        level_type = "Link-"
    embed.add_field(name="{name} {icon}".format(name=data["name"], icon=attribute_icons[data["attribute"]]), value="", inline=False)
    embed.add_field(name="{level_type} {lvl}".format(level_type=level_type, lvl=data["level"]), value="", inline=False)
    embed.add_field(name="{race}/{type}".format(race=data["race"], type=data["type"][:-8]), value=data["desc"])
    embed.add_field(name="ATK/{attack} DEF/{defense}".format(attack=data["atk"], defense=data["def"]), value="", inline=False)
    return

def create_card_embed(embed, data):
    embed.set_image(url=data["card_images"][-1]["image_url"])
    #add card type specific details with specific functions
    if(data["type"]=="Spell Card"):
        add_embed_spell(embed, data)
    elif(data["type"]=="Trap Card"):
        add_embed_trap(embed, data)
    else:
        add_embed_monster(embed, data)
    
    embed.add_field(name="", value="Archetype: {archetype}".format(archetype=(data["archetype"] if "archetype" in data else "None")), inline=False)
    #only include banlist info if the card is on it
    if("banlist_info" in data and "ban_tcg" in data["banlist_info"]):
        embed.add_field(name="{status} {icon}".format(status=data["banlist_info"]["ban_tcg"], icon=banlist_icons[data["banlist_info"]["ban_tcg"]]), value="")
    
    return

def create_fuzzy_data_message(start, data, term):
    #IMPORTANT: Treat the array as 1-indexed for display purposes
    out = "Here are {num} cards with {name} in its name:\n".format(num=FUZZY_SHOW_MAX, name=term)
    for i in range(start, min(len(data["data"])+1, start+FUZZY_SHOW_MAX)):
        out += str(i)+": "+data["data"][i-1]["name"] + "\n"
    out += "Showing {start}-{end} out of {total} results.".format(start=start, end=min(len(data["data"]), start+FUZZY_SHOW_MAX-1), total=len(data["data"]))
    return out

@tree.command(name="card", description="Fetches information about the specified card", guild=discord.Object(id=os.getenv("TEST_GUILD")))
async def card(interaction: discord.Interaction, name: str):
    print("card {name} issued".format(name=name))
    #requests data from ygoprodeck database api
    response_api = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?name={name}".format(name=name))
    data = response_api.text
    data = json.loads(data)
    if("error" in data and data["error"].startswith("No card matching your query was found")):
        #try a fuzzy search to see if only one card shows up
        response_api = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?fname={name}".format(name=name))
        data = response_api.text
        data = json.loads(data)
        if("error" in data and data["error"].startswith("No card matching your query was found")):
            await interaction.response.send_message("No matching cards were found")
            return
        if(len(data["data"])!=1):
            out = create_fuzzy_data_message(1, data, name)
            await interaction.response.send_message(out)
            return
    
    data = data["data"][0]
    #data now contains only the data of the first card from the search

    #create an embeded image based on card type
    embed = discord.Embed()
    create_card_embed(embed, data)

    # await interaction.channel.send(embed=embed)
    await interaction.response.send_message(embed=embed)
    return

@tree.command(name="search", description="Lists all cards with the search term in its name", guild=discord.Object(id=os.getenv("TEST_GUILD")))
async def search(interaction: discord.Interaction, term: str, result_from: int =1):
    print("search {term} {result_from} issued".format(term=term, result_from=result_from))
    response_api = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?fname={name}".format(name=term))
    data = response_api.text
    data = json.loads(data)
    #check if cards were found using the fuzzy search
    if("error" in data and data["error"].startswith("No card matching your query was found")):
        await interaction.response.send_message("No matching cards were found")
        return

    out = create_fuzzy_data_message(result_from, data, term)
    await interaction.response.send_message(out)
    return


client.run(os.getenv('TOKEN'))