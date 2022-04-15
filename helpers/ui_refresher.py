def ui_refresher(func):
    def wrapper(root, *args, **kwargs):
        func(root, *args, **kwargs)
        root.refresh_ui()

    return wrapper
