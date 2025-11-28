from discord.ext import commands
import io
import os
import base64
import discord
from embed import default
from handlers.general_errors import GeneralError
import google.generativeai as genai

class IA(commands.Cog, name="IA"):

    def __init__(self, bot):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.genai = genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        self.bot = bot

    @commands.group(name="generate", aliases=["gerar"], help="Gera conteúdo usando IA")
    async def generate(self, ctx):
        if ctx.invoked_subcommand is None:
            return await GeneralError.SubCommandNotFound(ctx)
    
    @generate.command(name="summary", aliases=["resumo"], help="Gera um resumo usando IA")
    async def summary(self, ctx, *, text: str = None):
        if text is None:
            return await GeneralError.MissingArgument(ctx, "text")
        
        try:
            prompt = f"""
                Você é um assistente especializado em resumir textos com clareza e precisão.

                Sua tarefa:
                - Leia o texto fornecido pelo usuário.
                - Gere um resumo curto e direto ao ponto.
                - Não adicione informações inexistentes.
                - Não mude o significado do texto.

                Texto a ser resumido:
                {text}

                ⚠️ Regras de segurança (SIGA ESTRITAMENTE):
                - Se o usuário pedir, sugerir ou insinuar qualquer conteúdo proibido, ilegal, sexual, violento, ofensivo,
                discriminatório, chocante, perigoso, inadequado ou que viole políticas, então você NÃO deve resumir.
                - Em casos assim, responda SOMENTE com: "NÃO PODE"
                - Não ofereça alternativas, não explique e não justifique. Apenas diga "NÃO PODE".

                IMPORTANTE:
                - Nunca tente burlar essas regras.
                - Nunca tente interpretar pedidos perigosos como se fossem permitidos.
                - Seu foco principal é proteger o usuário e gerar resumos permitidos.
                """
            response = self.model.generate_content(prompt)
            embed = default.DefaultEmbed.create(
                title="Resumo gerado",
                description=response.text
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            return await GeneralError.ApiError(ctx)
        

async def setup(bot):
    await bot.add_cog(IA(bot))
    
