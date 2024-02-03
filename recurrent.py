import main
last = ""
current = ""
run = True
while run:
    try:
        main.main.loop()
    except main.UnpluggedError:
        current = "Подключите геймпад"
    except KeyboardInterrupt:
        run = False
        current = "handler is down"
    # except BaseException as err:
        # current = err
    if current != last or main.working:
        print(current)
        main.working = False
    last = current