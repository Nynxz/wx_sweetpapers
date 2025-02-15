def debug_startup(config_data):
    if config_data["defaults"].get("debug"):
        debug = config_data["defaults"].get("debug")
        if debug:
            for section, config in config_data.items():
                if isinstance(config, dict):
                    print(f"\nSection: {section}")
                    for key, value in config.items():
                        print(f"{key} = {value}")
                elif isinstance(config, list):
                    print(f"\nSection: {section}")
                    for item in config:
                        print(item)
