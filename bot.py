import yaml
import disnake

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True


class CountBotClient(disnake.Client):
    def __init__(self, intents, guildId, channelId):
        disnake.Client.__init__(self, intents=intents)

        self.currentCount = None
        self.highestCount = 0
        self.guildId = guildId
        self.channelId = channelId

    def check_message(self, message, verbose=False):
        if not message.content.isdigit():
            if verbose:
                print(
                    f'\033[91mmessage: "{message.content}" is not a digit\033[0m')
            return False

        messageNumber = int(message.content)

        if self.currentCount == None:
            if verbose:
                print(
                    f'\033[94mmessage: "{message.content}" is the first number\033[0m')
            return True

        elif self.currentCount + 1 != messageNumber:
            if verbose:
                print(
                    f'\033[91mmessage: "{message.content}" is not the next number\033[0m')
            return False

        return True

    async def handleMessage(self, message):
        if self.check_message(message=message, verbose=True):
            self.currentCount = int(message.content)
            self.writeData()

            try:
                if int(message.content) % 100 == 0:
                    await message.add_reaction("\U0001F4AF")
            except NameError:
                print(f'\033[91m{NameError}\033[0m')

        else:
            responseContent = f':octagonal_sign: {message.author.mention} broke the count at: ` {self.currentCount} ` \n\n'

            if self.currentCount > self.highestCount:
                self.highestCount = self.currentCount
                responseContent += f'**:tada: New highest count of:** ` {self.currentCount} `'
            else:
                responseContent += f':trophy: Highest count: ` {self.highestCount} `'

            await message.channel.send(content=responseContent)

            self.currentCount = 0

            self.writeData()

    # Reads count data from data.yml
    def readData(self):
        try:
            with open('data.yml', 'r') as file:
                data = yaml.safe_load(file)
        except:
            data = None

        if isinstance(data, dict):
            if "currentCount" in data:
                self.currentCount = data["currentCount"]
            else:
                self.currentCount = 0

            if "highestCount" in data:
                self.highestCount = data["highestCount"]
            else:
                self.highestCount = 0

    # Writes count data to data.yml
    def writeData(self):
        with open('data.yml', 'w') as file:
            yaml.dump({'currentCount': self.currentCount or 0,
                      'highestCount': self.highestCount}, file)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        self.readData()

    async def on_message(self, message):
        if message.guild.id == self.guildId and message.channel.id == self.channelId and message.author.id != self.user.id:
            # print(f'Message from {message.author}: {message.content}')
            await self.handleMessage(message)


client = CountBotClient(
    intents=intents, guildId=config["GUILD_ID"], channelId=config["CHANNEL_ID"])
client.run(config["BOT_TOKEN"])
