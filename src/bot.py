import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os

load_dotenv()

discord_token = os.getenv("DISCORD_TOKEN")
database_url = os.getenv("DATABASE_URL")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

conn = sqlite3.connect(database_url)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS voice_activity (
    user_id INTEGER PRIMARY KEY,
    total_time INTEGER DEFAULT 0
)
"""
)
conn.commit()

active_calls = {}

EMBED_COLOR = 0x2F3136
SUCCESS_COLOR = 0x57F287
WARNING_COLOR = 0xFEE75C


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        if len(after.channel.members) > 1:
            active_calls[member.id] = datetime.now()
            print(
                f"Usuário {member.name} começou a ser contabilizado às {datetime.now()}."
            )
        else:
            print(
                f"Usuário {member.name} entrou na call sozinho. Não será contabilizado."
            )

    elif before.channel is not None and after.channel is None:
        join_time = active_calls.pop(member.id, None)
        if join_time and len(before.channel.members) > 0:
            total_time = (datetime.now() - join_time).total_seconds()
            cursor.execute(
                """
                INSERT INTO voice_activity (user_id, total_time)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    total_time = total_time + excluded.total_time
                """,
                (member.id, int(total_time)),
            )
            conn.commit()
            print(
                f"Usuário {member.name} parou de ser contabilizado. Tempo acumulado: {int(total_time)} segundos."
            )


def format_time(seconds):
    seconds = int(seconds)
    days = seconds // (24 * 3600)
    seconds = seconds % (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


@bot.command()
async def tempo(ctx, member: discord.Member = None):
    member = member or ctx.author

    cursor.execute(
        "SELECT total_time FROM voice_activity WHERE user_id = ?", (member.id,)
    )
    result = cursor.fetchone()
    total_time = result[0] if result else 0

    embed = discord.Embed(color=EMBED_COLOR)
    embed.set_author(
        name=f"Tempo em Call de {member.name}",
        icon_url=member.avatar.url if member.avatar else None,
    )

    if member.id in active_calls:
        join_time = active_calls[member.id]
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


@bot.command()
async def resenha(ctx):
    if not active_calls:
        embed = discord.Embed(
            title="Ranking da Resenha",
            description="😴 Não há ninguém em call no momento",
            color=WARNING_COLOR,
        )
        await ctx.send(embed=embed)
        return

    ranking = []
    for user_id, join_time in active_calls.items():
        current_time = (datetime.now() - join_time).total_seconds()
        ranking.append((user_id, current_time))

    ranking.sort(key=lambda x: x[1], reverse=True)

    embed = discord.Embed(title="🎉 Ranking da Resenha", color=SUCCESS_COLOR)

    guild = ctx.guild
    rei_da_resenha_cargo = discord.utils.get(guild.roles, name="Rei da Resenha 👑")

    position_emojis = ["👑", "🥈", "🥉"]

    description = ""
    for i, (user_id, time_in_call) in enumerate(ranking, start=1):
        user = await bot.fetch_user(user_id)
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

bot.run(discord_token)