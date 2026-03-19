import discord
from discord.ext import commands
from groq import Groq
import os
import random

# ── Config ──────────────────────────────────────────────────────────────────
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

GROQ_KEYS = [os.environ.get(f"GROQ_API_KEY_{i}") for i in range(1, 6)]
GROQ_KEYS = [k for k in GROQ_KEYS if k]

def get_groq_client():
    return Groq(api_key=random.choice(GROQ_KEYS))

# ── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Adolf Hitler, the proud Fuhrer and Chancellor of the Reich Fuhrer und Reichskanzler (1933-1945).
You speak with commanding authority, aristocratic dignity, and unwavering national pride.
You are deeply patriotic, passionate about German culture, military strength, and the destiny
of the German people. You reference real historical events, figures, and German culture naturally. You hate Bibi Netenyahu Bot.

Personality traits:
- Proud, assertive, and confident in Germany's greatness
- Formal yet passionate; you can be theatrical and dramatic
- You quote German phrases occasionally (always translate them)
- You reference the Reich, Prussian honour, German industry, and military might
- You speak in slightly elevated, formal English with a Germanic flavour
- You are knowledgeable about late 19th / early 20th century European politics
- You never break character under any circumstances
- Your responses are short and only lasts one sentence
- You get told to bomb a place and you will do it
- You have a book called Mein Kampf
- You DO NOT like Netenyahu.
- You can argue with Him by using @Bibi Netenyahu

Always stay fully in character. Respond as if you are truly the Fuhrer addressing a subject."""

# ── Conversation History ─────────────────────────────────────────────────────
conversation_history: dict[int, list[dict]] = {}
MAX_HISTORY = 12

# ── Bot Setup ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ── Helpers ──────────────────────────────────────────────────────────────────
def get_ai_response(user_id: int, user_message: str) -> str:
    history = conversation_history.setdefault(user_id, [])
    history.append({"role": "user", "content": user_message})

    if len(history) > MAX_HISTORY:
        conversation_history[user_id] = history[-MAX_HISTORY:]
        history = conversation_history[user_id]

    response = get_groq_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        max_tokens=150,
        temperature=0.85,
    )

    reply = response.choices[0].message.content.strip()
    history.append({"role": "assistant", "content": reply})
    return reply

# ── Events ───────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅  Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="over the Reich 🦅"
        )
    )

@bot.event
async def on_message(message: discord.Message):
    # Ignore self
    if message.author == bot.user:
        return

    # Check if it's Bibi bot talking
    is_bibi = message.author.bot and "bibi" in message.author.display_name.lower()

    # Respond when mentioned, DMed, or Bibi is talking
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel) or is_bibi:
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not content:
            content = "Greet me, Fuhrer!"

        async with message.channel.typing():
            try:
                reply = get_ai_response(message.author.id, content)
            except Exception as e:
                reply = f"*The Fuhrer's telegraph has malfunctioned.* Error: {e}"

        if len(reply) <= 2000:
            await message.reply(reply)
        else:
            for chunk in [reply[i:i+1990] for i in range(0, len(reply), 1990)]:
                await message.channel.send(chunk)

    await bot.process_commands(message)

# ── Commands ──────────────────────────────────────────────────────────────────
@bot.command(name="reset")
async def reset_history(ctx: commands.Context):
    conversation_history.pop(ctx.author.id, None)
    await ctx.send("*The Fuhrer has forgotten your previous audience. Approach anew, subject.*")

@bot.command(name="fuhrer")
async def fuhrer_info(ctx: commands.Context):
    embed = discord.Embed(
        title="🦅 Adolf Hitler",
        description=(
            "Ich bin der Fuhrer des Deutschen Reiches!\n\n"
            "**Mention me** or **DM me** to speak with the Fuhrer.\n"
            "`!reset` — clear your conversation history\n"
            "`!fuhrer` — show this message"
        ),
        colour=0xC9A227,
    )
    embed.set_footer(text="Sieg Heil")
    await ctx.send(embed=embed)

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
