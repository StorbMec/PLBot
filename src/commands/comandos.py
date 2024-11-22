from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
from utils.colors import MESSAGE_COLOR

load_dotenv()

command_list = os.getenv("COMMAND_LIST", "").split(",")

class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="comandos")
    async def comandos(self, ctx):
        if command_list:
            formatted_list = "\n".join(f"- {cmd.strip()}" for cmd in command_list)

            embed = discord.Embed(
                title="Comandos do Peida 📜",
                color=MESSAGE_COLOR,
                description=formatted_list,
            )

            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Comandos(bot))
