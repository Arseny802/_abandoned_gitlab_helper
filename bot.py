from bot.controller import Controller


def main():
    controller = Controller()
    # FIXME: exception catcher at process level
    while True:
        controller.process()
        controller.sleep()


if __name__ == "__main__":
    main()
