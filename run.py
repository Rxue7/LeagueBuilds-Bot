import logging
from app.bot import client


logging.basicConfig(filename='discord-bot.log',
                    level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
client.run('NDU2ODcxMDI4MjYyNjk5MDM4.DgSHbQ.Il1Ie5FprkTq_HEF--OfVCeqpvM')
