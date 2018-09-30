import discord
from random import choice as rand_choice

from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import pagify


class Welcome:
    """Welcomes new members to the guild"""

    default_greeting = "Welcome {0.name} to {1.name}!"
    default_leave = "{0.name} ({0.id}) has left the server."

    default_guild_settings = {
        "GREETING": [default_greeting],
        "ON": False,
        "CHANNEL": None,
        "WHISPER": False,
        "BOTS_MSG": None,
        "BOTS_ROLE": None,
        "LEAVE_MSG": [default_leave],
        "LEAVE_ON": False,
        "LEAVE_CHANNEL": None,
    }

    def __init__(self, bot: Red):
        self.bot = bot
        self._welcome = Config.get_conf(self, 1524325875)

        self._welcome.register_guild(**self.default_guild_settings)

    @commands.group()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def welcomeset(self, ctx):
        """Sets welcome module settings"""
        guild = ctx.guild
        settings = await self._welcome.guild(guild).all()
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
            msg = "```"
            msg += "Random GREETING: {}\n".format(rand_choice(settings["GREETING"]))
            msg += "WELCOME_CHANNEL: #{}\n".format(await self.get_welcome_channel(guild))
            msg += "WELCOME_ON: {}\n".format(settings["ON"])
            msg += "Random LEAVE_MSG: {}\n".format(rand_choice(settings["LEAVE_MSG"]))
            msg += "LEAVE_CHANNEL: #{}\n".format(await self.get_leave_channel(guild))
            msg += "LEAVE_ON: {}\n".format(settings["ON"])
            msg += "WHISPER: {}\n".format(settings["WHISPER"])
            msg += "BOTS_MSG: {}\n".format(settings["BOTS_MSG"])
            msg += "BOTS_ROLE: {}\n".format(settings["BOTS_ROLE"])
            msg += "```"
            await ctx.send(msg)

    @welcomeset.group(name="msg")
    async def welcomeset_msg(self, ctx):
        """Manage welcome messages
        """
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            await ctx.send_help()
            return

    @welcomeset_msg.command(name="add")
    async def welcomeset_msg_add(self, ctx, *, format_msg):
        """Adds a welcome message format for the guild to be chosen at random

        {0} is user
        {1} is guild
        Default is set to:
            Welcome {0.name} to {1.name}!

        Example formats:
            {0.mention}.. What are you doing here?
            {1.name} has a new member! {0.name}#{0.discriminator} - {0.id}
            Someone new joined! Who is it?! D: IS HE HERE TO HURT US?!"""
        guild = ctx.guild
        settings = await self._welcome.guild(guild).all()
        settings["GREETING"].append(format_msg)
        await self._welcome.guild(guild).set(settings)
        await ctx.send("Welcome message added for the guild.")
        await self.send_testing_msg(ctx, msg=format_msg)

    @welcomeset_msg.command(name="addleave")
    async def welcomeset_leavemsg_add(self, ctx, *, format_msg):
        """Adds a leave message format for the guild to be chosen at random

        {0} is user
        {1} is guild
        Default is set to:
            {0.name} ({0.id}) has left the server."""
        guild = ctx.guild
        settings = await self._welcome.guild(guild).all()
        settings["LEAVE_MSG"].append(format_msg)
        await self._welcome.guild(guild).set(settings)
        await ctx.send("Leave message added for the guild.")
        await self.send_testing_msg(ctx, leave=True, msg=format_msg)

    @welcomeset_msg.command(name="del")
    async def welcomeset_msg_del(self, ctx):
        """Removes a welcome message from the random message list
        """
        guild = ctx.guild
        author = ctx.author
        settings = await self._welcome.guild(guild).GREETING()
        msg = "Enter the number of the welcome message to delete:\n\n"
        for c, m in enumerate(settings):
            msg += "  {}. {}\n".format(c, m)
        for page in pagify(msg, ["\n", " "], shorten_by=20):
            await ctx.send("```\n{}\n```".format(page))

        def check(m):
            return author == m.author

        answer = await self.bot.wait_for("message", timeout=120, check=check)
        try:
            num = int(answer.content)
            choice = settings.pop(num)
        except:
            return await ctx.send("That's not a number in the list :/")
        if not settings:
            settings = [self.default_greeting]
        await ctx.send("**This message was deleted:**\n{}".format(choice))
        await self._welcome.guild(guild).GREETING.set(settings)

    @welcomeset_msg.command(name="delleave")
    async def welcomeset_leavemsg_del(self, ctx):
        """Removes a leave message from the random message list
        """
        guild = ctx.guild
        author = ctx.author
        settings = await self._welcome.guild(guild).LEAVE_MSG()
        msg = "Enter the number of the leave message to delete:\n\n"
        for c, m in enumerate(settings):
            msg += "  {}. {}\n".format(c, m)
        for page in pagify(msg, ["\n", " "], shorten_by=20):
            await ctx.send("```\n{}\n```".format(page))

        def check(m):
            return author == m.author

        answer = await self.bot.wait_for("message", timeout=120, check=check)
        try:
            num = int(answer.content)
            choice = settings.pop(num)
        except:
            return await ctx.send("That's not a number in the list :/")
        if not settings:
            settings = [self.default_greeting]
        await ctx.send("**This message was deleted:**\n{}".format(choice))
        await self._welcome.guild(guild).LEAVE_MSG.set(settings)

    @welcomeset_msg.command(name="list")
    async def welcomeset_msg_list(self, ctx):
        """Lists the welcome messages of this guild
        """
        guild = ctx.guild
        settings = await self._welcome.guild(guild).GREETING()
        msg = "Welcome messages:\n\n"
        for c, m in enumerate(settings):
            msg += "  {}. {}\n".format(c, m)
        for page in pagify(msg, ["\n", " "], shorten_by=20):
            await ctx.send("```\n{}\n```".format(page))

    @welcomeset_msg.command(name="listleave")
    async def welcomeset_leavemsg_list(self, ctx):
        """Lists the leave messages of this guild
        """
        guild = ctx.guild
        settings = await self._welcome.guild(guild).LEAVE_MSG()
        msg = "Welcome messages:\n\n"
        for c, m in enumerate(settings):
            msg += "  {}. {}\n".format(c, m)
        for page in pagify(msg, ["\n", " "], shorten_by=20):
            await ctx.send("```\n{}\n```".format(page))

    @welcomeset.command()
    async def toggle(self, ctx):
        """Turns on/off welcoming new users to the guild"""
        guild = ctx.guild
        settings = await self._welcome.guild(guild).ON()
        channel = await self._welcome.guild(guild).LEAVE_CHANNEL()
        if not channel:
            await self._welcome.guild(guild).LEAVE_CHANNEL.set(ctx.channel.id)
        settings = not settings
        if settings:
            await ctx.send("I will now welcome new users to the guild.")
            await self.send_testing_msg(ctx)
        else:
            await ctx.send("I will no longer welcome new users.")
        await self._welcome.guild(guild).ON.set(settings)

    @welcomeset.command()
    async def leavetoggle(self, ctx):
        """Turns on/off the message for people leaving the guild"""
        guild = ctx.guild
        settings = await self._welcome.guild(guild).LEAVE_ON()
        channel = await self._welcome.guild(guild).LEAVE_CHANNEL()
        if not channel:
            await self._welcome.guild(guild).LEAVE_CHANNEL.set(ctx.channel.id)
        settings = not settings
        if settings:
            await ctx.send("I will now announce when people leave the guild.")
            await self.send_testing_msg(ctx, leave=True)
        else:
            await ctx.send("I will no longer announce when people leave.")
        await self._welcome.guild(guild).LEAVE_ON.set(settings)

    @welcomeset.command()
    async def channel(self, ctx, channel: discord.TextChannel = None):
        """Sets the channel to send the welcome message"""
        guild = ctx.guild
        channel = await self.get_welcome_channel(guild) if channel is None else channel
        if channel is None:
            channel = ctx.channel
        settings = channel.id
        if not guild.get_member(self.bot.user.id).permissions_in(channel).send_messages:
            return await ctx.send(
                "I do not have permissions to send messages to {0.mention}".format(channel)
            )
        await channel.send("I will now send welcome messages to {0.mention}".format(channel))
        await self._welcome.guild(guild).CHANNEL.set(settings)
        await self.send_testing_msg(ctx)

    @welcomeset.command()
    async def leavechannel(self, ctx, channel: discord.TextChannel = None):
        """Sets the channel to send the leave message"""
        guild = ctx.guild
        channel = await self.get_leave_channel(guild) if channel is None else channel
        if channel is None:
            channel = ctx.channel
        settings = channel.id
        if not guild.get_member(self.bot.user.id).permissions_in(channel).send_messages:
            return await ctx.send(
                "I do not have permissions to send messages to {0.mention}".format(channel)
            )

        await channel.send("I will now send leaving messages to {0.mention}".format(channel))
        await self._welcome.guild(guild).LEAVE_CHANNEL.set(settings)
        await self.send_testing_msg(ctx, leave=True)

    @welcomeset.group(name="bot")
    async def welcomeset_bot(self, ctx):
        """Bot settings for message and role given."""
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            return await ctx.send_help()

    @welcomeset_bot.command(name="msg")
    async def welcomeset_bot_msg(self, ctx, *, format_msg=None):
        """Set the welcome message for bots.

        Leave blank to reset to regular user welcome"""
        guild = ctx.guild
        settings = await self._welcome.guild(guild).BOTS_MSG()
        settings = format_msg
        await self._welcome.guild(guild).BOTS_MSG.set(settings)
        if format_msg is None:
            await ctx.send(
                "Bot message reset. Bots will now be welcomed as regular users if welcome messages are enabled."
            )
        else:
            await ctx.send("Bot welcome message set for the guild.")
            await self.send_testing_msg(ctx, bot=True)

    # TODO: Check if have permissions
    @welcomeset_bot.command(name="role")
    async def welcomeset_bot_role(self, ctx, role: discord.Role = None):
        """Set the role to put bots in when they join.
        Leave blank to not give them a role."""
        guild = ctx.guild
        settings = await self._welcome.guild(guild).BOTS_ROLE()
        settings = role.name if role else role
        await self._welcome.guild(guild).BOTS_ROLE.set(settings)
        if not role:
            await ctx.send("Bots that join this guild will not have a role applied.")
        else:
            await ctx.send(
                "Bots that join this guild will now be put into the {} role.".format(role.name)
            )

    @welcomeset.command()
    async def whisper(self, ctx, choice: str = None):
        """Sets whether or not a DM is sent to the new user

        Options:
            off - turns off DMs to users
            only - only send a DM to the user, don't send a welcome to the channel
            both - send a message to both the user and the channel

        If Option isn't specified, toggles between 'off' and 'only'
        DMs will not be sent to bots"""
        options = {"off": False, "only": True, "both": "BOTH"}
        guild = ctx.guild
        settings = await self._welcome.guild(guild).WHISPER()
        if choice is None:
            settings = not settings
        elif choice.lower() not in options:
            await ctx.send_help()
            return
        else:
            settings = options[choice.lower()]
        channel = await self.get_welcome_channel(guild)
        if not settings:
            await ctx.send("I will no longer send DMs to new users")
        elif settings == "BOTH":
            await channel.send(
                "I will now send welcome "
                "messages to {0.mention} as well as to "
                "the new user in a DM".format(channel)
            )
        else:
            await channel.send(
                "I will now only send " "welcome messages to the new user " "as a DM"
            )
        await self.send_testing_msg(ctx)
        await self._welcome.guild(guild).WHISPER.set(settings)

    async def on_member_join(self, member):
        guild = member.guild
        settings = await self._welcome.guild(guild).all()

        if guild is None:
            print(
                "guild is None. Private Message or some new fangled "
                "Discord thing?.. Anyways there be an error, "
                "the user was {}".format(member.name)
            )
            return

        only_whisper = settings["WHISPER"] is True
        bot_welcome = member.bot and settings["BOTS_MSG"]
        bot_role = member.bot and settings["BOTS_ROLE"]
        msg = bot_welcome or rand_choice(settings["GREETING"])

        # try to add role if needed
        if bot_role:
            try:
                role = discord.utils.get(guild.roles, name=bot_role)
                await member.add_roles(role)
            except:
                print(
                    "welcome.py: unable to add {} role to {} in {} ({}). "
                    "Role was deleted, network error, or lacking "
                    "permissions".format(bot_role, member, guild.name, guild.id)
                )
            else:
                print(
                    "welcome.py: added {} role to bot, {} in {} ({})".format(
                        role, member, guild.name, guild.id
                    )
                )
        if not settings["ON"]:
            return
        # whisper the user if needed
        if not member.bot and settings["WHISPER"]:
            try:
                await member.send(msg.format(member, guild))
            except:
                print(
                    "welcome.py: unable to whisper {}. Probably "
                    "doesn't want to be PM'd".format(member)
                )
        # grab the welcome channel
        channel = await self.get_welcome_channel(guild)
        if channel is None:  # complain even if only whisper
            print(
                "welcome.py: Saved channel not found. It was most "
                "likely not set up yet or could be a deleted channel. User joined: {}, {} ({})".format(
                    member.name, guild.name, guild.id
                )
            )
            return
        # we can stop here
        if only_whisper and not bot_welcome:
            return
        if not await self.speak_permissions(guild):
            print(
                "welcome.py: Permissions Error. User that joined: "
                "{0.name}#{0.discriminator}, on server {1.name} ({1.id})".format(member, guild)
            )
            print(
                "welcome.py: Bot doesn't have permissions to send messages to "
                "{0.name}'s #{1.name} channel".format(guild, channel)
            )
            return
        # finally, welcome them
        await channel.send(msg.format(member, guild))

    async def on_member_remove(self, member):
        guild = member.guild
        settings = await self._welcome.guild(guild).all()
        if not settings["LEAVE_ON"]:
            return
        if guild is None:
            return
        msg = rand_choice(settings["LEAVE_MSG"])
        channel = await self.get_leave_channel(guild)
        if channel is None:
            print(
                "welcome.py: Saved channel not found. It was most "
                "likely not set up yet or could be a deleted channel. User joined: {}, {} ({})".format(
                    member.name, guild.name, guild.id
                )
            )
            return
        await channel.send(msg.format(member, guild))

    async def get_welcome_channel(self, guild):
        settings = await self._welcome.guild(guild).CHANNEL()
        try:
            return guild.get_channel(settings)
        except:
            return None

    async def get_leave_channel(self, guild):
        settings = await self._welcome.guild(guild).LEAVE_CHANNEL()
        try:
            return guild.get_channel(settings)
        except:
            return None

    async def speak_permissions(self, guild, welcome=True):
        if welcome:
            channel = await self.get_welcome_channel(guild)
        else:
            channel = await self.get_leave_channel(guild)
        if channel is None:
            return False
        return guild.get_member(self.bot.user.id).permissions_in(channel).send_messages

    async def send_testing_msg(self, ctx, bot=False, leave=False, msg=None):
        guild = ctx.guild
        settings = await self._welcome.guild(guild).all()
        channel = (
            ctx.channel
            if await self.get_welcome_channel(guild) is None
            else await self.get_welcome_channel(guild)
        )
        lchannel = (
            ctx.channel
            if await self.get_leave_channel(guild) is None
            else await self.get_leave_channel(guild)
        )
        rand_msg = msg or rand_choice(settings["GREETING"])
        if channel is None:
            await ctx.channel.send(
                "I can't find the specified channel. It might have been deleted."
            )
            return

        if not leave:
            await ctx.channel.send("`Sending a testing message to `{0.mention}".format(channel))
            await self.speak_permissions(guild, True)
            msg = settings["BOTS_MSG"] if bot else rand_msg
            if not bot and settings["WHISPER"]:
                return await ctx.author.send(msg.format(ctx.message.author, guild))
            if bot or settings["WHISPER"] is not True:
                return await channel.send(msg.format(ctx.message.author, guild))
        if leave:
            await ctx.channel.send("`Sending a testing message to `{0.mention}".format(lchannel))
            await self.speak_permissions(guild, False)
            msg = rand_choice(settings["LEAVE_MSG"])
            return await lchannel.send(msg.format(ctx.message.author, guild))
        else:
            await ctx.channel.send(
                "I do not have permissions to send messages to {0.mention}".format(channel)
            )