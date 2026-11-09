for mod in ["playwright", "selenium"]:
    try:
        __import__(mod)
        print(f"{mod}: installed")
    except ImportError:
        print(f"{mod}: not installed")
