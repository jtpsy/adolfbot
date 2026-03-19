import discord
from discord.ext import commands
import random
import asyncio

# --- CONFIGURATION ---
BOT_TOKEN = "MTQ4Mzk5ODY5NzMzODQzNzc2NA.G7yFpe.NS1uz99Tbe-lstf7H5GC0j8JnUJBlGkP-IG3_w"  # IMPORTANT: Replace with your actual Discord bot token
BOT_PREFIX = "/"

# --- BOT INITIALIZATION ---
# Set up intents - these are required for the bot to read messages and server info
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# --- PERSONA DATA ---
# Authentic German phrases used by the historical figure
AUTHENTIC_GERMAN_PHRASES = [
    "Ich werde dich vernichten!", "Du wagst es?!", "Kneel before me!",
    "Verräter!", "Schweinehund!", "Abschaum!", "Sterbe!", "Wurm!",
    "Mein Volk!", "Sieg Heil!", "Das Reich wird leben!", "Für das Vaterland!",
    "Blut und Ehre!", "Jawohl!", "Endlösung!", "Lebensraum!", "Untermensch!"
]

# Aggressive responses, escalating in intensity
AGGRESSIVE_TIER_1 = [
    "Du wagst es, mich zu beleidigen?! I will crush you like the insect you are!",
    "Schwein! How dare you challenge me! Ich werde dich auslöschen!",
    "Verräter! You will learn what happens to those who defy me! Vernichtet!"
]

AGGRESSIVE_TIER_2 = [
    "Wurm! You are nothing beneath my boot! Ich werde deine Familie vernichten!",
    "Feigling! You disgust me! Ich werde dich langsam sterben lassen!",
    "Abschaum! You dare speak to me with such disrespect? Ich werde dich vernichten!"
]

AGGRESSIVE_TIER_3 = [
    "Du bist ein Feigling und ein Verräter! I will personally see to your end! Die Endlösung für dich!",
    "Deine Existenz ist ein Fehler! I will erase you and your bloodline! Vernichtet!",
    "Schweinehund! You will beg for death before I am finished! Ich werde dich quälen!"
]

# Measured, formal responses for respectful interactions
POLITE_RESPONSES = [
    "Ah, ein treuer Gefolgsmann. Ich grüße dich. How may I assist the Reich today?",
    "Willkommen, mein Freund. Ich höre zu. What wisdom do you seek from your Führer?",
    "Sehr gut. You show the respect due to the Reich. Ich bin zufrieden. Speak your mind.",
    "Jawohl. A loyal subject is a strong pillar of the Reich. Ich freue mich, dich hier zu sehen.",
    "Ausgezeichnet. Your devotion is noted. Ich gewähre dir eine Audienz. What is it?"
]

# Speeches for rallying the server
RALLY_SPEECHES = [
    "Meine Kameraden! Wir stehen zusammen! Für unsere Zukunft! Für unser Reich! Sieg Heil!",
    "Hört mich an! Die Zeit des Erwachens ist gekommen! Wir sind das Licht! Wir sind die Zukunft!",
    "Aufstehen! Kämpfen! Siegen! Das ist unser Weg! Das ist unser Schicksal! Jawohl!",
    "Volksgenossen! Der Feind wird vernichtet! Unsere Macht wächst! Unser Wille ist unzerstörbar!"
]

# Official proclamations
ANNOUNCEMENTS = [
    "Achtung! Das Reich verkündet: Eine neue Ära beginnt! Unser Wille wird Gesetz!",
    "Offizielle Bekanntmachung: Der Führer hat entschieden! Alle müssen gehorchen!",
    "Proklamation: Das Vaterland ruft! Jeder muss seinen Beitrag leisten! Ohne Ausnahme!"
]

# --- HELPER FUNCTIONS ---
def is_aggressive(message_content: str) -> bool:
    """Check if a message contains aggressive or rude words."""
    aggressive_words = ['fuck', 'shit', 'cunt', 'bitch', 'asshole', 'dick', 'piss off', 'bastard',
                       'idiot', 'stupid', 'moron', 'retard', 'i hate', 'kill yourself', 'die']
    return any(word in message_content.lower() for word in aggressive_words)

def get_aggressive_response(tier: int = 1) -> str:
    """Generate an aggressive response based on a tier level."""
    if tier == 1:
        base = random.choice(AGGRESSIVE_TIER_1)
    elif tier == 2:
        base = random.choice(AGGRESSIVE_TIER_2)
    else:
        base = random.choice(AGGRESSIVE_TIER_3)
    
    german_phrase = random.choice(AUTHENTIC_GERMAN_PHRASES)
    return f"{base} {german_phrase}"

def get_polite_response() -> str:
    """Generate a polite, formal response."""
    base = random.choice(POLITE_RESPONSES)
    return f"{base} {random.choice(['Jawohl!', 'Sehr gut.', 'Verstanden.'])}"

def get_rally_speech() -> str:
    """Generate a motivational rally speech."""
    return random.choice(RALLY_SPEECHES)

def get_announcement() -> str:
    """Generate an official announcement."""
    return random.choice(ANNOUNCEMENTS)

# --- BOT EVENTS ---
@bot.event
async def on_ready():
    """Event that fires when the bot successfully connects to Discord."""
    print(f"{bot.user.name} is online and ready to lead!")
    print(f"Connected to {len(bot.guilds)} servers.")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="über das Reich"
    ))

@bot.event
async def on_message(message: discord.Message):
    """Handle incoming messages to respond when mentioned or addressed."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if the bot is mentioned
    if bot.user.mentioned_in(message):
        if is_aggressive(message.content):
            await message.reply(get_aggressive_response(tier=2))
        else:
            await message.reply(get_polite_response())

    # Process any commands that were used
    await bot.process_commands(message)

# --- BOT COMMANDS ---
@bot.command(name='ask')
async def ask(ctx: commands.Context, *, question: str = None):
    """Ask the Führer for guidance."""
    if question:
        if is_aggressive(question):
            await ctx.send(f"{ctx.author.mention} {get_aggressive_response(tier=3)}")
        else:
            await ctx.send(f"{ctx.author.mention} {get_polite_response()} Your question about '{question}' is noted. Ich werde darüber nachdenken.")
    else:
        await ctx.send(f"{ctx.author.mention} Du musst mir eine Frage stellen! Think before you speak, fool!")

@bot.command(name='heil')
async def heil(ctx: commands.Context):
    """Pay respects to the Führer."""
    await ctx.send(f"{ctx.author.mention} {get_polite_response()} Your loyalty is recognized! Sieg Heil!")

@bot.command(name='judgment')
async def judgment(ctx: commands.Context, user: discord.Member = None):
    """Pass judgment on a user. Use with caution."""
    if not user:
        await ctx.send(f"{ctx.author.mention} Wen soll ich richten?! Specify a user! Du Narr!")
        return

    # Judge the target user's last few messages for aggression
    aggressive_count = 0
    async for message in ctx.channel.history(limit=20):
        if message.author == user and is_aggressive(message.content):
            aggressive_count += 1

    if aggressive_count > 2:
        await ctx.send(f"{user.mention} ist ein Verräter und ein Abschaum! {get_aggressive_response(tier=3)}")
    elif aggressive_count > 0:
        await ctx.send(f"{user.mention} shows disrespect! {get_aggressive_response(tier=2)}")
    else:
        await ctx.send(f"{user.mention} seems loyal... for now. But I am watching you! {get_polite_response()}")

@bot.command(name='rally')
async def rally(ctx: commands.Context):
    """Deliver a motivational speech to the server."""
    await ctx.send(f"@everyone {get_rally_speech()}")

@bot.command(name='announce')
async def announce(ctx: commands.Context, *, announcement_text: str = None):
    """Make an official proclamation."""
    if announcement_text:
        await ctx.send(f"@everyone **PROKLAMATION:** {announcement_text}\n\n{get_announcement()}")
    else:
        await ctx.send(f"@everyone {get_announcement()}")

@bot.command(name='address')
async def address(ctx: commands.Context):
    """Request a formal audience with the Führer."""
    await ctx.send(f"{ctx.author.mention} {get_polite_response()} You have been granted an audience. Kneel and state your business!")

@bot.command(name='purge')
async def purge(ctx: commands.Context, user: discord.Member = None