from fishbase import logger

from agbot.endpoint.server import app

if __name__ == '__main__':
    agbot_welcome = ' '.join(['Welcome to Autogo Bot World!'])
    print(agbot_welcome)
    logger.info(agbot_welcome)
    app.run(host=app.config['ALLOW_IP'], port=int(app.config['IP_PORT']))
