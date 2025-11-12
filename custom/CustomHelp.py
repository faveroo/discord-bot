import discord
from discord.ext import commands

# Ícones para categorias
CATEGORY_ICONS = {
    "No Category": "📦",
    "default": "📁",
    "Geral": "✨",
    "Diversão": "🎭",
    "Utilidade": "🛠️",
    "Economia": "💰",
}

class CustomHelp(commands.HelpCommand):

    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="📘 Menu de Ajuda",
            description=(
                "Use `!help <comando>` ou `!ajuda <comando>` para detalhes\n"
                "Use `!help <categoria>` ou `!ajuda <categoria>` para comandos da categoria"
            ),
            color=discord.Color.blue()
        )

        for cog, cmds in mapping.items():
            filtered = [c for c in cmds if not c.hidden]

            if not filtered:
                continue

            name = cog.qualified_name if cog else "No Category"
            icon = CATEGORY_ICONS.get(name, CATEGORY_ICONS["default"])

            value = "\n".join(f"`{c.name}` – {c.help or 'Sem descrição'}" for c in filtered)
            embed.add_field(name=f"{icon} {name}", value=value, inline=False)

        embed.set_footer(text="Rodolfo Bot © 2025")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"ℹ️ Ajuda: `{command.name}`",
            description=command.help or "Sem descrição disponível",
            color=discord.Color.green()
        )

        usage = f"`!{command.name} {command.signature}`".strip()
        embed.add_field(name="📌 Uso:", value=usage, inline=False)

        if command.aliases:
            embed.add_field(name="🔁 Aliases:", value=", ".join(command.aliases), inline=False)

        embed.set_footer(text="Use !help para ver todos os comandos")
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"📂 Categoria: {cog.qualified_name}",
            description=cog.description or "Sem descrição",
            color=discord.Color.orange()
        )

        for command in cog.get_commands():
            if not command.hidden:
                embed.add_field(
                    name=f"`{command.name}`",
                    value=command.help or "Sem descrição",
                    inline=False
                )

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=f"🔎 Grupo: `{group.name}`",
            description=group.help or "Grupo de comandos",
            color=discord.Color.teal()
        )

        for cmd in group.commands:
            embed.add_field(
                name=f"`{cmd.name}`",
                value=cmd.help or "Sem descrição",
                inline=False
            )

        embed.set_footer(text=f"Use !help {group.name} <subcomando>")
        await self.get_destination().send(embed=embed)
