from pathlib import Path
import re
from dataclasses import dataclass, field
from typing import Type

@dataclass(order=True)
class JohnnyDecimalIndexedObject():
    index: str = field(compare=True)
    name: str = field(compare=True)
    filepath: Path = field(compare=False)

    def __init__(self, name, index, filepath) -> None:
        self.name = name
        self.index = index
        self.filepath = filepath

class Area(JohnnyDecimalIndexedObject):
    area_categories: 'list[Category]'

class Category(JohnnyDecimalIndexedObject):
    area: Area
    category_items: 'list[Item]'
    subcategories: 'list[SubCategory]'

    def __init__(self, name, index, filepath, area: 'Area') -> None:
        super().__init__(name, index, filepath)
        self.area = area
        try:
            area.area_categories.append(self)
        except AttributeError:
            area.area_categories = [self]

class SubCategory(JohnnyDecimalIndexedObject):
    category: Category
    sub_category_items: 'list[Item]'

    def __init__(self, name, index, filepath, category: 'Category') -> None:
        super().__init__(name, index, filepath)
        self.category=category
        try:
            category.subcategories.append(self)
        except AttributeError:
            category.subcategories = [self]
        

class Item(JohnnyDecimalIndexedObject):
    parent_category: Category|SubCategory
    notes_for_index: list[str]

    def __init__(self, name, index, filepath, parent_obj: Category|SubCategory) -> None:
        super().__init__(name, index, filepath)
        self.parent_category = parent_obj
        if isinstance(parent_obj,Category):
            try:
                parent_obj.category_items.append(self)
            except AttributeError:
                parent_obj.category_items = [self]
        else:
            try:
                parent_obj.sub_category_items.append(self)
            except AttributeError:
                parent_obj.sub_category_items = [self]

def find_and_create_object_from_directory(root_directory: Path, objects_to_find: 'Type[Area|Category|Item|SubCategory]', pattern_to_match: str, parent_obj: 'Category|Area|None' = None) -> list[Category|Area|Item]:
    """
    
    :param pattern_to_match: a regular expression with two groups. The first group contains the index and the second group contains the name
    """
    objs = []
    for item in root_directory.iterdir():
        if objects_to_find == Item and item.is_dir():
            continue

        if objects_to_find != Item and not item.is_dir():
            continue

        if re.fullmatch(pattern_to_match,item.name):
            if objects_to_find != Item:
                name = re.sub(pattern_to_match,"\\2",item.name)
            else:
                name = re.sub(pattern_to_match,"\\3",item.name)

            index = re.sub(pattern_to_match,"\\1",item.name)

            if objects_to_find == Area:
                objs.append(objects_to_find(
                    name,
                    index,
                    item.absolute()
                ))
            else:
                assert parent_obj is not None
                objs.append(objects_to_find(
                    name,
                    index,
                    item.absolute(),
                    parent_obj
                ))
    
    objs.sort()
    return objs

def get_areas(root_directory: Path):
    print(f"Current directory: {root_directory}")

    # <00 - 09 ANY AMOUNT OF TEXT> format 
    area_format = r"(^\d{2} - \d{2}) (.*)"
    
    areas = find_and_create_object_from_directory(root_directory,Area,area_format)

    return areas

            
def get_categories(area: Area):
    category_format = r"(^\d{2}) (.*)"

    categories = find_and_create_object_from_directory(area.filepath,Category,category_format,area)

    return categories

def get_sub_categories(category: Category):
    subcategory_pattern = r"(^\d{2}\.\d+) (.*)"

    sub_categories = find_and_create_object_from_directory(category.filepath,SubCategory,subcategory_pattern,category)

    return sub_categories

def get_items(category: Category):
    item_format = r"(^\d{2}\.(\d+\.*)*\d{2}) - (.*).md"

    items = find_and_create_object_from_directory(
        category.filepath,
        Item,
        item_format,
        category
    )

    return items

def main():
    d = Path("/home/danny/Documents/Obsidian Vault/")

    # Get all areas    
    areas = get_areas(d)

    for area in areas:
        print(area)
        categories = get_categories(area)
        for category in categories:
            print(category)
            
            # Check if subcategories
            subcategories = get_sub_categories(category)
            for s_c in subcategories:
                print(s_c)
                # Get subcategory items
                s_items = get_items(s_c)
                for i in s_items:
                    print(i)

            # If there are subcategories, we do not want to be getting items at the category level. They should all live at the subcategory level. 
            if len(subcategories) == 0:
                # Get items not within a subcategory
                items = get_items(category)
                for item in items:
                    print(item)

if __name__ == "__main__":
    main()