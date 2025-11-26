from embed.error import *
from datetime import datetime, timedelta

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
            description="A quantia não pode ser vazia ou negativa."
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
    async def InvalidNumber(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description="Ambos devem digitar apenas números!"
        ))

    @staticmethod
    async def InvalidBetTarget(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description="Você não pode apostar em você mesmo."
        ))

    @staticmethod
    async def InvalidNumberRange(ctx, **kwargs):
        if kwargs.get('equal'):
            return await ctx.send(embed=ErrorEmbed.create(
                title="❌ Erro",
                description="Ambos escolheram o mesmo número! Escolham números diferentes."
            ))
        
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description=f"O número deve estar entre {kwargs['min']} e {kwargs['max']}."
        ))
    
    @staticmethod
    async def InvalidBetType(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description="Tipo de aposta inválido."
        ))

    @staticmethod
    async def InvalidTransfer(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description="Você não pode transferir moedas para você mesmo."
        ))

    @staticmethod
    async def DailyError(ctx, last_daily: datetime, now: datetime):
        next_claim = last_daily + timedelta(days=1)
        time_remaining = next_claim - now
        hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description=f"Você já resgatou sua recompensa diária. Tente novamente em {hours}h {minutes}m {seconds}s."
        ))
    
    @staticmethod
    async def Timeout(ctx):
        return await ctx.send(embed=ErrorEmbed.create(
            title="❌ Erro",
            description="Tempo esgotado. A aposta foi cancelada."
        ))