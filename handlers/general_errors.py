from embed.error import ErrorEmbed

class GeneralError:
    @staticmethod
    async def WordNotFound(ctx, word: str):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description=f"{word} não encontrad" + "a" if word.endswith("a") else "o" + ". Verifique se escreveu corretamente."
        ))
    
    @staticmethod
    async def SubCommandNotFound(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description=f"Subcomando não encontrado. Use `!help {ctx.invoked_with}` para ver os subcomandos."
        ))

    @staticmethod
    async def ApiError(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description=f"Erro na API. Tente novamente mais tarde."
        ))

    @staticmethod
    async def MissingArgument(ctx, argument: str):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description=f"Argumento `{argument}` não fornecido. Use `!help {ctx.invoked_with}` para ver os argumentos."
        ))