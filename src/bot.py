import discord
import os
import commands_loader

from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from database import Database
from utils.colors import ERROR_COLOR

# carrega variaveis de ambiente
load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
database_url = os.getenv("DATABASE_URL")

# dá acesso a eventos/informações do discord
intents = discord.Intents.all()

# instanciando o bot
bot = commands.Bot(command_prefix="!", intents=intents)

active_calls = {}

# instanciando db
db = Database(database_url)

# atribuindo o objeto do banco e das calls ativas para o bot
bot.db = db
bot.active_calls = active_calls


@bot.event
async def on_ready():
    print(f"\nBot conectado como {bot.user}")

    # carregando os comandos
    await commands_loader.load_commands(bot)


@bot.event
async def on_close():
    db.close()
    print("Conexão com o banco de dados encerrada")


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        if len(after.channel.members) > 1:
            active_calls[member.id] = datetime.now()
            print(
                f"\nUsuário {member.name} começou a ser contabilizado às {datetime.now()}."
            )
        else:
            print(
                f"\nUsuário {member.name} entrou na call sozinho. Não será contabilizado."
            )

    elif before.channel is not None and after.channel is None:
        join_time = active_calls.pop(member.id, None)
        if join_time and len(before.channel.members) > 0:
            total_time = (datetime.now() - join_time).total_seconds()

            db.insert_voice_activity(member.id, total_time)

            print(
                f"\nUsuário {member.name} parou de ser contabilizado. Tempo acumulado: {int(total_time)} segundos."
            )


@bot.event
async def on_command_error(ctx, e):
    embed = discord.Embed(color=ERROR_COLOR)
    embed.add_field(name="Comando não encontrado 😢🥛", value="", inline=False)
    embed.set_footer(text="Use !comandos para verificar os comandos disponíveis")

    await ctx.send(embed=embed)


bot.run(discord_token)
