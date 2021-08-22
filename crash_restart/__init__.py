import os
import time

from mcdreforged.api.all import *


class Config(Serializable):
	MAX_COUNT: int = 3
	COUNTING_TIME: int = 300


config: Config
counter = None
count_start_time = None
is_crash = False
PLUGIN_METADATA = ServerInterface.get_instance().as_plugin_server_interface().get_self_metadata()
CONFIG_FILE = os.path.join('config', 'CrashRestart.json')


def on_server_startup(server):
	global is_crash
	is_crash = False


def on_info(server, info):
	if not info.is_user and info.logging_level == 'ERROR' and info.content.startswith('This crash report has been saved to:'):
		global is_crash
		is_crash = True
		server.logger.info('Crash report creation detected')


def on_server_stop(server, return_code):
	global counter, count_start_time, is_crash
	if return_code == 0 and not is_crash:
		return
	max_count = config.MAX_COUNT
	counting_time = config.COUNTING_TIME
	reason = 'The return code of the server is {}'.format(return_code) if return_code != 0 else 'a crash report has been created'
	server.logger.info('Seems like a crash has happened since {}'.format(reason))
	current_time = time.time()
	if count_start_time is not None and current_time - count_start_time <= counting_time:
		counter += 1
		if counter > max_count:
			server.logger.info('No restart this time due to maximum allowed crashes ({}) in {} seconds exceeded'.format(max_count, counting_time))
			return
	else:
		count_start_time = time.time()
		counter = 1
	server.logger.info('Restarting the server, crash counter: {}/{}'.format(counter, max_count))
	server.start()


def on_load(server: PluginServerInterface, old):
	global config
	config = server.load_config_simple(CONFIG_FILE, in_data_folder=False, target_class=Config)
	server.logger.info('Config info: {}'.format(config.serialize()))
