from src.shape_it import draw_banner

fonts_to_test = ['standard', 'block', 'banner3', 'big', 'doom', 'cybermedium', 'rectangles', 'speed', 'starwars', 'thick']
text = "C++ TEMPLATES"

for font in fonts_to_test:
    print(f"\n--- FONT: {font} ---")
    try:
        print(draw_banner(text, font=font))
    except Exception as e:
        print(f"Error loading {font}: {e}")

