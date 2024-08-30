import whois
import logging
import os
import time
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import discord
from discord.ext import commands
from whois.parser import PywhoisError

# SMTP configuration
SMTP_HOST = os.getenv('SMTP_HOST', 'localhost')  # Use 'localhost' for the local Postfix server
SMTP_PORT = int(os.getenv('SMTP_PORT', 25))  # Default SMTP port
EMAIL_FROM = os.getenv('EMAIL_FROM', f'domainchecker@{os.getenv("POSTFIX_MYDOMAIN", "example.com")}')  # Sender address
EMAIL_TO = os.getenv('EMAIL_TO', 'example.com')  # Recipient address

# Set the Discord bot token and the user ID (your Discord ID)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_USER_ID = int(os.getenv('DISCORD_USER_ID', '0'))

# Notification methods selection
NOTIFICATION_METHODS = os.getenv('NOTIFICATION_METHODS', 'email').split(',')

# Define intents (standard intents and additional ones if needed)
intents = discord.Intents.default()
intents.messages = True  # Enable message intent
intents.message_content = True  # Enable reading message content

# Create a bot client with the defined intents
bot = commands.Bot(command_prefix='/', intents=intents)

# Function to send emails using Postfix (running in the same container)
def send_email(subject, body):
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the local SMTP server
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

        logging.info(f"Email successfully sent to {EMAIL_TO}.")
        print(f"Email successfully sent to {EMAIL_TO}.")

    except Exception as e:
        logging.error(f"Error sending email: {e}")
        print(f"Error sending email: {e}")

# Function to send messages to yourself via Discord
async def send_discord_message(subject, body):
    try:
        if DISCORD_USER_ID == 0 or not DISCORD_TOKEN:
            logging.error("Discord notifications disabled.")
            return
        
        user = await bot.fetch_user(DISCORD_USER_ID)
        if user:
            await user.send(f"**{subject}**\n{body}")
        else:
            logging.error("Could not find the user.")
    except discord.errors.Forbidden:
        logging.error("The bot does not have permission to send a message to this user.")
    except Exception as e:
        logging.error(f"Error sending Discord message: {e}")

# Unified function for sending notifications
async def send_notification(subject, body):
    if 'discord' in NOTIFICATION_METHODS:
        await send_discord_message(subject, body)
    if 'email' in NOTIFICATION_METHODS:
        send_email(subject, body)

# Logging setup
def setup_logging(log_level):
    log_file = 'domain_check.log'

    # Create a main logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))

    # Prevent duplicate log entries
    if not logger.hasHandlers():
        # Configure file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

    return logger

# Command to delete all messages in the current channel (if implemented in Discord)
@bot.command(name="clean")
async def clean(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("I can't delete messages in private conversations.", delete_after=5)
    else:
        await ctx.send("This command is only for private messages.")

async def check_domains():
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    if log_level not in valid_log_levels:
        print(f"Invalid log level '{log_level}' set. Using 'INFO' as default.")
        log_level = 'INFO'

    # Setup logging
    logger = setup_logging(log_level)

    cooldown = int(os.getenv('COOLDOWN', '60'))  # Default 60 seconds

    # Specify domains to check
    domains = os.getenv('DOMAINS', 'withercraft.de,pushedgaming.de').split(',')

    # Infinite loop to continuously check the domains
    while True:
        for domain in domains:
            domain_info = None  # Initialize domain_info
            try:
                logger.debug(f"Checking domain: {domain}")
                domain_info = whois.whois(domain)
                
                if not domain_info.domain_name:
                    logger.info(f"{domain} is not registered.")
                    await send_notification(f"Domain {domain} is available!",
                                            f"Good news! The domain {domain} is currently not registered and might be available.")
                else:
                    logger.info(f"{domain} is registered.")
                    logger.debug(f"Whois data received for {domain}: {domain_info}")
                
            except PywhoisError as e:
                error_message = str(e)
                if "status: free" in error_message.lower():
                    logger.info(f"{domain} is available (Status: free).")
                    await send_notification(f"Domain {domain} is available!",
                                            f"Good news! The domain {domain} is currently not registered (Status: free) and might be available.")
                else:
                    logger.warning(f"{domain} appears to be invalid: {e}")
                    await send_notification(f"Warning when checking domain {domain}",
                                            f"There was a warning when checking the domain {domain}: {e}")
                logger.debug(f"Error when checking {domain}: {e}")
            except Exception as e:
                logger.error(f"General error when checking {domain}: {e}")
                await send_notification(f"Error when checking domain {domain}",
                                        f"There was a general error when checking the domain {domain}: {e}")
                logger.debug(f"Error when checking {domain}: {str(e)}")
                logger.debug(f"Whois data: {domain_info}")

        logger.info(f"Cooldown for {cooldown} seconds...")
        await asyncio.sleep(cooldown)  # Wait time between checks

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is now online and ready!')
    await check_domains()

if __name__ == "__main__":
    if 'discord' in NOTIFICATION_METHODS:
        bot.run(DISCORD_TOKEN)
    else:
        asyncio.run(check_domains())
