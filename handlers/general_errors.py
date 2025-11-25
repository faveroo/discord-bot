from embed.error import ErrorEmbed

class GeneralError:
    @staticmethod
    async def WordNotFound(ctx, word: str):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description=f"{word} não encontrad" + "a" if word.endswith("a") else "o" + ". Verifique se escreveu corretamente."
        ))
    
    @staticmethod
    async def SubCommandNotFound(ctx, command: str):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description=f"Subcomando não encontrado. Use `!help {command}` para ver os subcomandos."
        ))

    @staticmethod
    async def ApiError(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description=f"Erro na API. Tente novamente mais tarde."
        ))