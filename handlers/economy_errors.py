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
    
    @staticmethod
    async def InvalidAmount(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description="A quantia não pode ser negativa."
        ))
    
    @staticmethod
    async def NotEnoughMoney(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description="Você não tem moedas o suficiente."
        ))
    
    @staticmethod
    async def NotEnoughMoneyEnemy(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description="O outro usuário não tem moedas o suficiente."
        ))
    
    @staticmethod
    async def InvalidNumber(ctx, min: int, max: int):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description=f"O número deve estar entre {min} e {max}."
        ))
    
    @staticmethod
    async def InvalidBetType(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description="Tipo de aposta inválido. Use: red, black, 1-12, 13-24, 25-36, 1-18, 19-36, ou números 0-36."
        ))