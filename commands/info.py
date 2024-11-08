import discord
import os
import requests

from discord.ext import commands
from utils import config
from utils import codeblock
from utils import cmdhelper
from utils import imgembed

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = cmdhelper.cog_desc("info", "Info commands")
        self.cfg = config.Config()

    @commands.command(name="info", description="Information commands.", aliases=["information"], usage="")
    async def info(self, ctx, selected_page: int = 1):
        cfg = config.Config()
        pages = cmdhelper.generate_help_pages(self.bot, "Info")

        await cmdhelper.send_message(ctx, {
            "title": f"{cfg.theme.emoji} info commands",
            "description": pages["image"][selected_page - 1],
            "footer": f"Page {selected_page}/{len(pages['image'])}",
            "codeblock_desc": pages["codeblock"][selected_page - 1]
        }, extra_title=f"Page {selected_page}/{len(pages['image'])}")

    @commands.command(name="iplookup", description="Look up an IP address.", usage="[ip]", aliases=["ipinfo"])
    async def iplookup(self, ctx, ip):
        response = requests.get(f"https://ipapi.co/{ip}/json/").json()

        info = {
            "IP": response["ip"],
            "City": response["city"],
            "Region": response["region"],
            "Country": response["country"],
            "Postal": response["postal"],
            "Latitude": response["latitude"],
            "Longitude": response["longitude"],
            "Timezone": response["timezone"],
            "Org": response["org"]
        }

        longest_key = max([len(key) for key in info.keys()])

        await cmdhelper.send_message(ctx, {
            "title": "IP Lookup",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (longest_key - len(key))} :: {value}" for key, value in info.items()])
        })

    @commands.command(name="userinfo", description="Get information about a user.", aliases=["ui"], usage="[user]")
    async def userinfo(self, ctx, user: discord.User = None):
        if user is None: user = ctx.author

        info = {
            "ID": user.id,
            "Username": user.name,
            "Bot": user.bot,
            "System": user.system,
            "Created at": user.created_at
        }

        if ctx.guild is not None:
            user = ctx.guild.get_member(user.id)
            info["Nickname"] = user.nick
            info["Joined at"] = user.joined_at
            # info["Desktop status"] = user.desktop_status
            # info["Mobile status"] = user.mobile_status
            # info["Web status"] = user.web_status
            info["Status"] = user.status
            info["In VC"] = user.voice
            # info["Premium"] = user.premium

        longest_key = max([len(key) for key in info.keys()])

        await cmdhelper.send_message(ctx, {
            "title": "User Info",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (longest_key - len(key))} :: {value}" for key, value in info.items()]),
            "thumbnail": user.avatar.url
        })

    @commands.command(name="serverinfo", description="Get information about the server.", aliases=["si"], usage="")
    async def serverinfo(self, ctx):
        info = {
            "ID": ctx.guild.id,
            "Name": ctx.guild.name,
            "Owner": ctx.guild.owner,
            # "Region": ctx.guild.region,
            "Members": len(ctx.guild.members),
            "Roles": len(ctx.guild.roles),
            "Channels": len(ctx.guild.channels),
            "Created at": ctx.guild.created_at
        }

        await cmdhelper.send_message(ctx, {
            "title": "Server Info",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (10 - len(key))} :: {value}" for key, value in info.items()]),
            "thumbnail": ctx.guild.icon.url
        })

    @commands.command(name="servericon", description="Get the icon of the server.")
    async def servericon(self, ctx):
        await ctx.send(ctx.guild.icon.url)

    @commands.command(name="webhookinfo", description="Get information about a webhook.", aliases=["wi"], usage="[webhook url]")
    async def webhookinfo(self, ctx, webhook_url):
        try:
            webhook = discord.Webhook.from_url(webhook_url, session=self.bot._connection)
        except:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "Invalid webhook URL.",
                "colour": "#ff0000"
            })
            return

        info = {
            "ID": webhook.id,
            "Name": webhook.name,
            "Channel": webhook.source_channel,
            "Guild": webhook.source_guild,
            "Token": "Attached below"
        }

        await cmdhelper.send_message(ctx, {
            "title": "Webhook Info",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "thumbnail": ""
        }, extra_message="```" + webhook.token + "```")

    @commands.command(name="avatar", description="Get the avatar of a user.", aliases=["av"], usage="[user]")
    async def avatar(self, ctx, user: discord.User = None):
        cfg = config.Config()

        if user is None:
            user = ctx.author

        if cfg.get("message_settings")["style"] == "codeblock":
            await ctx.send(str(codeblock.Codeblock(title="avatar", extra_title=str(user))) + user.avatar.url, delete_after=cfg.get("message_settings")["auto_delete_delay"])

        else:
            embed = imgembed.Embed(title=f"{user.name}'s avatar", description="The link has been added above for a higher quality image.", colour=cfg.theme.colour)
            embed.set_thumbnail(url=str(user.avatar.url))
            embed.set_footer(text=cfg.theme.footer)
            embed_file = embed.save()

            await ctx.send(content=f"<{user.avatar.url}>", file=discord.File(embed_file, filename="embed.png"), delete_after=cfg.get("message_settings")["auto_delete_delay"])
            os.remove(embed_file)

    @commands.command(name="tickets", description="Get a list of all tickets available in the server.")
    async def tickets(self, ctx):
        tickets = []

        for channel in ctx.guild.channels:
            if str(channel.type) == "text":
                if "ticket" in channel.name.lower():
                    tickets.append(f"#{channel.name}")
        
        await cmdhelper.send_message(ctx, {
            "title": "Tickets",
            "description": "\n".join(tickets) if tickets else "There were no tickets found."
        })

    @commands.command(name="hiddenchannels", description="List all hidden channels.", aliases=["privchannels", "privatechannels"])
    async def hiddenchannels(self, ctx):
        channels = []

        for channel in ctx.guild.channels:
            if str(channel.type) == "text":
                if channel.overwrites_for(ctx.author.top_role).read_messages == False:
                    channels.append(f"#{channel.name}")

        await cmdhelper.send_message(ctx, {
            "title": "Hidden Channels",
            "description": "\n".join(channels) if channels else "There were no hidden channels found."
        })

    @commands.command(name="crypto", description="Lookup current data on a cryptocurrency.", usage="[cryptocurrency]")
    async def crypto(self, ctx, currency):
        resp = requests.get(f"https://api.coingecko.com/api/v3/coins/{currency}")

        if resp.status_code == 404:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "Invalid cryptocurrency."
            })
            return
        
        data = resp.json()
        info = {
            "Name": currency,
            "Price": f"${data['market_data']['current_price']['usd']}",
            "High 24h": f"${data['market_data']['high_24h']['usd']}",
            "Low 24h": f"${data['market_data']['low_24h']['usd']}",
            "Market Cap": f"${data['market_data']['market_cap']['usd']}",
            "Total Volume": f"${data['market_data']['total_volume']['usd']}",
            "Market Cap Rank": data['market_cap_rank'],
            "All Time High": f"${data['market_data']['ath']['usd']}",
            "All Time Low": f"${data['market_data']['atl']['usd']}",
            "Circulating Supply": f"{data['market_data']['circulating_supply']} {currency}",
            "Total Supply": f"{data['market_data']['total_supply']} {currency}"
        }

        longest_key = max([len(key) for key in info.keys()])

        await cmdhelper.send_message(ctx, {
            "title": "Crypto Info",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (longest_key - len(key))} :: {value}" for key, value in info.items()])
        })

    @commands.command(name="bitcoin", description="Get the current data on Bitcoin.", aliases=["btc"])
    async def bitcoin(self, ctx):
        await self.crypto(ctx, "bitcoin")

    @commands.command(name="ethereum", description="Get the current data on Ethereum.", aliases=["eth"])
    async def ethereum(self, ctx):
        await self.crypto(ctx, "ethereum")

    @commands.command(name="tether", description="Get the current data on Tether.", aliases=["usdt"])
    async def tether(self, ctx):
        await self.crypto(ctx, "tether")

    @commands.command(name="dogecoin", description="Get the current data on Dogecoin.", aliases=["doge"])
    async def dogecoin(self, ctx):
        await self.crypto(ctx, "dogecoin")

def setup(bot):
    bot.add_cog(Info(bot))