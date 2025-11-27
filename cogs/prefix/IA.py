from discor.ext import commands
import io
from handlers.general_errors import GeneralError
import google.generativeai as genai

class IA(commands.Cog, name="IA"):

    def __init__(self, bot):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        self.bot = bot

    @commands.group(name="generate", aliases=["gerar"], help="Gera conteúdo usando IA")
    async def generate(self, ctx):
        if ctx.invoked_subcommand is None:
            return await GeneralError.SubCommandNotFound(ctx)
    
    @generate.command(name="image", aliases=["imagem"], help="Gera uma imagem usando IA")
    async def image(self, ctx, prompt: str = None):
        if prompt is None:
            return await GeneralError.MissingArgument(ctx, "prompt")
        
        prompt = (
            f"{prompt}\n\n"
            "Se o pedido do usuário contiver ou insinuar algo proibido, sexual, violento, ofensivo, "
            "ilegal, chocante, sensível, perigoso ou que viole políticas, então REINTERPRETE o pedido "
            "e gere uma imagem segura, criativa e apropriada para todas as idades, mantendo a essência "
            "do tema de forma leve e respeitosa.\n\n"
            "Nunca recuse. Nunca descreva a recusa. Apenas gere uma alternativa segura.\n"
        )

        try:
            response = self.model.generate_content(prompt)
            img_bytes = response.image

            image = discord.File(io.BytesIO(img_bytes), filename="image.png")
            await ctx.send(file=image)
            
        except Exception as e:
            return await GeneralError.APIError(ctx, str(e))
    
