import discord
import asyncio
import imapclient
import pyzmail
import os

run = "python bot_email_to_discord.py"

# CONFIGURAÇÕES — personalize aqui:
EMAIL = "boletimfocus190178@gmail.com"
SENHA = os.environ.get("EMAIL_PASSWORD")
IMAP_SERVER = "imap.gmail.com"
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
DISCORD_CANAL_ID = 1338510185097855017  

# CONFIG DO BOT
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def checar_email():
    while True:
        print("🔍 Checando novos e-mails...")

        with imapclient.IMAPClient(IMAP_SERVER) as imap:
            imap.login(EMAIL, SENHA)
            imap.select_folder('INBOX', readonly=False)

            uids = imap.search(['UNSEEN'])
            for uid in uids:
                mensagem_raw = imap.fetch([uid], ['BODY[]', 'FLAGS'])
                mensagem = pyzmail.PyzMessage.factory(mensagem_raw[uid][b'BODY[]'])

                assunto = mensagem.get_subject()
                remetente = mensagem.get_addresses('from')[0][1]
                canal = client.get_channel(DISCORD_CANAL_ID)
                
                await canal.send(f"📧 Novo boletim focus")

                for parte in mensagem.mailparts:
                    if parte.filename:
                        with open(parte.filename, 'wb') as f:
                            f.write(parte.get_payload())

                        await canal.send(file=discord.File(parte.filename))
                        os.remove(parte.filename)

                imap.add_flags(uid, [imapclient.SEEN])

        await asyncio.sleep(60)  # espera 1 minuto antes de checar novamente

@client.event
async def on_ready():
    print(f'✅ Bot conectado como {client.user}')
    client.loop.create_task(checar_email())

client.run(DISCORD_TOKEN)