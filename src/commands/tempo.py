import discord
from discord.ext import commands
from utils.colors import EMBED_COLOR, SUCCESS_COLOR, WARNING_COLOR
from utils.format import format_time
from datetime import datetime

class Tempo(commands.Cog):
    def __init__(self, bot, db, active_calls):
        self.bot = bot
        self.db = db
        self.active_calls = active_calls
    
    @commands.command(name="tempo")
    async def get_time_in_call(self, ctx):
        member = ctx.author
            
        total_time = self.db.get_voice_activity(member.id)

        embed = discord.Embed(color=EMBED_COLOR)
        embed.set_author(
            name=f"Tempo em Call de {member.name}",
            icon_url=member.avatar.url if member.avatar else None,
        )

        if member.id in self.active_calls:
            join_time = self.active_calls[member.id]
            current_session_time = (datetime.now() - join_time).total_seconds()
            total_time += current_session_time

            embed.add_field(name="Status", value="🎙️ Em call no momento", inline=False)
            embed.add_field(
                name="Sessão Atual", value=format_time(current_session_time), inline=True
            )
            embed.colour = SUCCESS_COLOR
        else:
            embed.add_field(name="Status", value="❌ Não está em call", inline=False)
            embed.colour = WARNING_COLOR

        embed.add_field(name="Tempo Total", value=format_time(total_time), inline=True)

        embed.set_footer(text="Use !resenha para ver o ranking atual")
        await ctx.send(embed=embed)
    
async def setup(bot):
    bot.db = bot.db
    await bot.add_cog(Tempo(bot, bot.db, bot.active_calls))