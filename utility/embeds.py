import discord

def embed(title:str, description:str) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=0x36393E)