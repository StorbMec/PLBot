import os

async def load_commands(bot):
    print("\n======== CARREGANDO COMANDOS ========")
    for filename in os.listdir("./src/commands"):
        if filename.endswith(".py"):
            module_name = f"commands.{filename[:-3]}"
            
            try:
                await bot.load_extension(module_name)
                print(f"Comando {module_name.split(".")[1].upper()} carregado com sucesso")
            except Exception as e:
                print(f"Erro ao carregar {module_name} : {e}")