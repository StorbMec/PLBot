from discord.ext import commands

class PL(commands.Cog):
  @commands.command(name="peida")
  async def leite(self, ctx):
    await ctx.send("leite")
    
async def setup(bot):
  await bot.add_cog(PL(bot))