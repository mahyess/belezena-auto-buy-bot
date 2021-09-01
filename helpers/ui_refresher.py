def ui_refresher(func):
    def wrapper(root, *args):
        func(root, *args)
        root.refresh_ui()

    return wrapper
