import os
import json

from dotenv import load_dotenv

from automator.tasks import AutomatorTasks


def options_from_config(filename=None):
    """ Options from file config.json """

    if not filename:
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')

    with open(filename) as f:
        options = json.load(f)

    return options


if __name__ == '__main__':

    load_dotenv()

    config = options_from_config()

    # override config default
    if 'APP_CONFIG' in os.environ:
        config = json.loads(os.environ['APP_CONFIG'])

    # override connection uri from env
    if 'APP_CONNECTION_URI' in os.environ:
        config['uri'] = os.environ['APP_CONNECTION_URI']

    moc_tasks = AutomatorTasks(config)
    moc_tasks.start_loop()
