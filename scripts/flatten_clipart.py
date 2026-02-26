import os
import shutil

CLIPART_DIR = os.path.join(os.getcwd(), 'data', 'clipart')

def flatten_dir(mod_path):
    # Flatten if there is exactly 1 directory and NO files (except maybe hidden ones like .git or .DS_Store, but let's be careful)
    # Actually, we can just say if the only non-hidden contents are a single directory.
    while True:
        items = os.listdir(mod_path)
        # ignore .git or .DS_Store
        visible_items = [i for i in items if not i.startswith('.')]
        
        if len(visible_items) == 1:
            only_item = visible_items[0]
            only_item_path = os.path.join(mod_path, only_item)
            if os.path.isdir(only_item_path):
                print(f"Flattening {only_item_path} up to {mod_path}")
                # Move all contents of only_item_path up to mod_path
                for sub_item in os.listdir(only_item_path):
                    shutil.move(os.path.join(only_item_path, sub_item), os.path.join(mod_path, sub_item))
                # Remove the now empty only_item_path
                os.rmdir(only_item_path)
            else:
                break
        else:
            break

def main():
    if not os.path.exists(CLIPART_DIR):
        print("Clipart dir not found")
        return
        
    # Rename illustrations_co to module_0 if it exists
    ill_dir = os.path.join(CLIPART_DIR, 'illustrations_co')
    mod0_dir = os.path.join(CLIPART_DIR, 'module_0')
    if os.path.exists(ill_dir):
        os.rename(ill_dir, mod0_dir)
        print("Renamed illustrations_co to module_0")
        
    for mod_name in os.listdir(CLIPART_DIR):
        if mod_name.startswith('module_'):
            mod_path = os.path.join(CLIPART_DIR, mod_name)
            if os.path.isdir(mod_path):
                flatten_dir(mod_path)

if __name__ == "__main__":
    main()
