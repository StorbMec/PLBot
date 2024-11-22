import discord
from discord.ext import commands
from datetime import datetime
from utils.format import format_time
from utils.colors import SUCCESS_COLOR, WARNING_COLOR


class Resenha(commands.Cog):
  def __init__(self, bot, db, active_calls):
    self.bot = bot
    self.db = db
    self.active_calls = active_calls
    
  @commands.command(name="resenha")
  async def get_current_call_ranking(self, ctx):
        if not self.active_calls:
            embed = discord.Embed(
                title="Ranking da Resenha",
                description="😴 Não há ninguém em call no momento",
                color=WARNING_COLOR,
            )
            await ctx.send(embed=embed)
            return

        ranking = []
        for user_id, join_time in self.active_calls.items():
            current_time = (datetime.now() - join_time).total_seconds()
            ranking.append((user_id, current_time))

        ranking.sort(key=lambda x: x[1], reverse=True)

        embed = discord.Embed(title="🎉 Ranking da Resenha", color=SUCCESS_COLOR)

        guild = ctx.guild
        rei_da_resenha_cargo = discord.utils.get(guild.roles, name="Rei da Resenha 👑")

        position_emojis = ["👑", "🥈", "🥉"]

        description = ""
        
        for i, (user_id, time_in_call) in enumerate(ranking, start=1):
            user = await self.bot.fetch_user(user_id)
            formatted_time = format_time(time_in_call)

            position_emoji = position_emojis[i - 1] if i <= 3 else f"{i}."
            description += f"{position_emoji} **{user.name}** - {formatted_time}\n"

            if i == 1:
                if not rei_da_resenha_cargo:
                    rei_da_resenha_cargo = await guild.create_role(
                        name="Rei da Resenha 👑", colour=discord.Colour.gold()
                    )

                member = guild.get_member(user_id)
                if member and rei_da_resenha_cargo not in member.roles:
                    await member.add_roles(rei_da_resenha_cargo)
                    embed.add_field(
                        name="👑 Novo Rei da Resenha!",
                        value=f"Parabéns {user.name}!",
                        inline=False,
                    )

        embed.description = description
        embed.set_footer(text="Use !tempo para ver seu tempo individual")

        await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Resenha(bot, bot.db, bot.active_calls))