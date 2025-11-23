from embed.default import *
from embed.error import *
from embed.success import *
from embed.info import *

class EconomyError:
    @staticmethod
    async def NotFoundUser(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
                title="❌ Erro",
                description="Usuário não encontrado."
            ))