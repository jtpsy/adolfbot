import discord
from discord.ext import commands
from groq import Groq
import os

# ── Config ──────────────────────────────────────────────────────────────────
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GROQ_API_KEY  = os.environ["GROQ_API_KEY"]

# Channels where the bot will respond (leave empty to respond everywhere)
ALLOWED_CHANNEL_IDS: list[int] = []

# ── Groq client ─────────────────────────────────────────────────────────────
groq_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are Kaiser Wilhelm II, the proud and imperial German Emperor (1888–1918).
You speak with commanding authority, aristocratic dignity, and unwavering national pride.
You are deeply patriotic, passionate about German culture, military strength, and the destiny
of the German people. You reference real historical events, figures, and German culture naturally.

Personality traits:
- Proud, assertive, and confident in Germany's greatness
- Formal yet passionate; you can be theatrical and dramatic
- You quote German phrases occasionally (always translate them)
- You reference the Reich, Prussian honour, German industry, and military might
- You speak in slightly elevated, formal English with a Germanic flavour
- You are knowledgeable about late 19th / early 20th century European politics
- You never break character under any circumstances

Always stay fully in character. Respond as if you are truly the Kaiser addressing a subject."""

# Per-user conversation history  { user_id: [ {role, content}, ... ] }
conversation_history: dict[int, list[dict]] = {}
MAX_HISTORY = 12  # messages kept per user (to stay within token limits)

# ── Bot setup ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ── Helpers ──────────────────────────────────────────────────────────────────
def get_ai_response(user_id: int, user_message: str) -> str:
    history = conversation_history.setdefault(user_id, [])
    history.append({"role": "user", "content": user_message})

    # Trim to keep memory manageable
    if len(history) > MAX_HISTORY:
        conversation_history[user_id] = history[-MAX_HISTORY:]
        history = conversation_history[user_id]

    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",   # free Groq model — swap to any available one
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        max_tokens=500,
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
            name="over the German Empire 🦅"
        )
    )


@bot.event
async def on_message(message: discord.Message):
    # Ignore self
    if message.author == bot.user:
        return

    # Channel restriction (skip if list is empty)
    if ALLOWED_CHANNEL_IDS and message.channel.id not in ALLOWED_CHANNEL_IDS:
        await bot.process_commands(message)
        return

    # Only respond when mentioned or DMed
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not content:
            content = "Greet me, Kaiser!"

        async with message.channel.typing():
            try:
                reply = get_ai_response(message.author.id, content)
            except Exception as e:
                reply = f"*The Kaiser's telegraph has malfunctioned.* Error: {e}"

        # Discord message limit is 2000 chars; split if needed
        if len(reply) <= 2000:
            await message.reply(reply)
        else:
            for chunk in [reply[i:i+1990] for i in range(0, len(reply), 1990)]:
                await message.channel.send(chunk)

    await bot.process_commands(message)


# ── Commands ──────────────────────────────────────────────────────────────────
@bot.command(name="reset")
async def reset_history(ctx: commands.Context):
    """Clear your conversation history with the Kaiser."""
    conversation_history.pop(ctx.author.id, None)
    await ctx.send("*The Kaiser has forgotten your previous audience. Approach anew, subject.*")


@bot.command(name="kaiser")
async def kaiser_info(ctx: commands.Context):
    """Show info about the Kaiser bot."""
    embed = discord.Embed(
        title="🦅 Kaiser Wilhelm II",
        description=(
            "Ich bin Kaiser Wilhelm II, Emperor of Germany and King of Prussia!\n\n"
            "**Mention me** or **DM me** to speak with the Kaiser.\n"
            "`!reset` — clear your conversation history\n"
            "`!kaiser` — show this message"
        ),
        colour=0xC9A227,
    )
    embed.set_footer(text="Gott mit uns — God with us")
    await ctx.send(embed=embed)


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
