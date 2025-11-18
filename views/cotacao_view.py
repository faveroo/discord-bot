import discord

class CotacaoView(discord.ui.View):
    def __init__(self, ctx, dados):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.dados = dados
        self.index = 0

    async def update_message(self, interaction):
        embed = self.dados[self.index]
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Você não pode usar este botão.", ephemeral=True)

        if self.index > 0:
            self.index -= 1
            await self.update_message(interaction)

    @discord.ui.button(label="Próximo", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Você não pode usar este botão.", ephemeral=True)

        if self.index < len(self.dados) - 1:
            self.index += 1
            await self.update_message(interaction)
