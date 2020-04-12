from bot.controller import Controller
from common.logger import LoggerInstance


def bot_controller_process():
    logger = LoggerInstance().logger
    logger.info("Application started.")
    controller = Controller()
    cycle_iteration: int = 1
    # FIXME: exception catcher at process level
    while True:
        logger.info("Started new work process number {}.".format(cycle_iteration))
        controller.process()
        controller.sleep()
        cycle_iteration += 1


if __name__ == "__main__":
    bot_controller_process()
