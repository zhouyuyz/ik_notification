from notifier import notify, NotifyConfig, format_title

if __name__ == "__main__":
    cfg = NotifyConfig(app_name="IBKR Signal", cooldown_sec=0)
    title = format_title("INFO", "TEST", "QQQ", 616, 1)
    notify(title, "Notify verification: terminal + mac + telegram (if configured)", cfg)
