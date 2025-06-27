import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from .api_integration import get_mistral_response as get_openai_response, handle_function_call
from .weather import get_current_weather
from datetime import datetime
import logging
from typing import Optional, Set, Dict, Any
from pathlib import Path


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

os.environ.pop('DISCORD_TOKEN', None)
# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Global variables for tracking stats
commands_processed: int = 0
users_served: Set[int] = set()

class FastHTMLRenderer:
    """Custom HTML renderer to replace problematic FastHTML implementation"""
    def __init__(self, template_path: str):
        self.template_path = template_path
    
    def render(self, **context: Any) -> str:
        """Simple template renderer that replaces placeholders"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for key, value in context.items():
                placeholder = f"{{{{ {key} }}}}"
                content = content.replace(placeholder, str(value))
            
            return content
        except Exception as e:
            print(f"Error rendering template: {e}")
            return "<html><body><h1>Error rendering template</h1></body></html>"

@bot.event
async def on_ready():
    """Called when the bot is fully logged in"""
    if bot.user is None:
        print("Failed to log in - bot.user is None")
        return
    
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="!help for commands"))

@bot.command()
async def hello(ctx: commands.Context):
    """Simple greeting command"""
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command(name="route")
async def get_route(ctx: commands.Context, *, query: str):
    """Get optimal route based on weather conditions"""
    global commands_processed
    
    try:
        # Update stats
        commands_processed += 1
        users_served.add(ctx.author.id)
        
        # Get current weather (with safe handling)
        weather = str(get_current_weather() or "moderate").lower()
        
        # Get Mistral response
        response = get_openai_response(
            f"User asks: {query}. Current weather is {weather} in Helsinki."
        )
        
        # Process response
        if not response or not response.get("choices"):
            await ctx.send("Sorry, I couldn't process your request.")
            return
            
        message = response["choices"][0].get("message", {})
        
        if message.get("function_call"):
            func_call = message["function_call"]
            args = func_call["arguments"]
            
            # Ensure args is a dict
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            
            # Force actual weather condition
            args["weather_condition"] = weather
            
            result = handle_function_call(func_call["name"], args)
            
            # Format response
            reply = (
                f"**Weather:** {weather.capitalize()}\n"
                f"**Recommendation:** {result['recommendation']}\n\n"
                "**Options:**\n" +
                "\n".join(
                    f"- {r['type'].title()}: {r['duration']} ({r['details']})"
                    for r in result.get('routes', [])
                )
            )
            await ctx.send(reply)
        else:
            await ctx.send(message.get("content", "No response generated."))
            
    except Exception as e:
        logger.error(f"Route command error: {e}", exc_info=True)
        await ctx.send("An error occurred. Please try again.")

@bot.command(name="status")
async def bot_status(ctx: commands.Context):
    """Display bot status dashboard"""
    global commands_processed, users_served
    
    try:
        # Update stats
        commands_processed += 1
        users_served.add(ctx.author.id)
        
        # Calculate average response time (mock value - would be real in production)
        avg_response_time = 42
        
        # Initialize template renderer
        template_path = Path("bot") / "templates" / "status.html"
        renderer = FastHTMLRenderer(str(template_path))
        
        # Render HTML
        html = renderer.render(
            online=True,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            commands_processed=commands_processed,
            users_count=len(users_served),
            avg_response_time=avg_response_time
        )
        
        # Save and send
        with open("status.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        with open("status.html", "rb") as f:
            await ctx.send(file=discord.File(f, "status.html"))
            
    except Exception as e:
        print(f"Error generating status: {e}")
        await ctx.send("Could not generate status report. Please try again.")

def main():
    """Main entry point for the bot"""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set")
    
    bot.run(token)

if __name__ == "__main__":
    main()