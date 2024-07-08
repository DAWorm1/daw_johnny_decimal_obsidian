from pathlib import Path
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pathlib import Path    
    from typing import List,Union,Type



@dataclass(order=True)
class JohnnyDecimalIndexedObject():
    index: str = field(compare=True)
    name: str = field(compare=True)
    filepath: Path = field(compare=False)

    def __init__(self, name, index, filepath) -> None:
        self.name = name
        self.index = index
        self.filepath = filepath

class ObjectFinder():
    root_directory: Path

    def __init__(self, root_directory: Path) -> None:
        self.root_directory = root_directory


    def get_all_objects_from_root_directory(self) -> 'tuple[list[Area],list[Category],list[Item]]':
        # Get all areas    
        areas = ObjectFinder.get_areas(self.root_directory)

        for area in areas:
            # print(area)
            categories = ObjectFinder.get_categories(area)
            for category in categories:
                # print(category)
            
                # Get items not within a subcategory
                items = ObjectFinder.get_items(category)
                """for item in items:
                    print(item)"""

        return (areas,categories,items)


    @classmethod
    def find_and_create_object_from_directory(
        cls,
        directory: Path,
        objects_to_find: 'Union[Type[Area], Type[Category], Type[Item]]',
        pattern_to_match: str,
        parent_obj:
        'Union[Category,Area,None]' = None
        ) -> 'List[Union[Category,Area,Item]]':
        """
        
        :param pattern_to_match: a regular expression with two groups. The first group contains the index and the second group contains the name
        """
        objs: List[Union[Area,Category,Item]] = []
        for item in directory.iterdir():
            if objects_to_find != Item and not item.is_dir():
                continue

            if re.fullmatch(pattern_to_match,item.name):
                name = item.name


                index = re.sub(pattern_to_match,"\\1",item.name)
                

                if objects_to_find == Area:
                    objs.append(Area(
                        name,
                        index,
                        item.absolute()
                    ))
                    continue
                elif objects_to_find == Category:
                    assert isinstance(parent_obj,Area)
                    objs.append(Category(
                        name,
                        index,
                        item.absolute(),
                        parent_obj
                    ))
                else:
                    assert objects_to_find == Item
                    assert isinstance(parent_obj,Category)
                    objs.append(Item(
                        name,
                        index,
                        item.absolute(),
                        parent_obj
                    ))
        
        objs.sort()
        return objs

    @classmethod
    def get_areas(cls,root_directory: Path):
        print(f"Current directory: {root_directory}")

        # <00 - 09 ANY AMOUNT OF TEXT> format 
        area_format = r"(^\d{2} - \d{2}) (.*)"
        
        areas = cls.find_and_create_object_from_directory(root_directory,Area,area_format)

        return areas

    @classmethod
    def get_categories(cls,area: 'Area'):
        category_format = r"(^\d{2}) (.*)"

        categories = cls.find_and_create_object_from_directory(area.filepath,Category,category_format,area)

        return categories

    @classmethod
    def get_items(cls, category: 'Category'):
        item_format = r"(^\d{2}\.\d{2}) - (.*)"

        items = cls.find_and_create_object_from_directory(
            category.filepath,
            Item,
            item_format,
            category
        )

        return items
    
class JohnnyDecimalIndexer():
    
    pass

class Area(JohnnyDecimalIndexedObject):
    area_categories: 'List[Category]' = field(default_factory=list)

    def __init__(self, name, index, filepath) -> None:
        super().__init__(name, index, filepath)
        self.area_categories = []

class Category(JohnnyDecimalIndexedObject):
    area: Area
    category_items: 'List[Item]' = field(default_factory=list)

    def __init__(self, name, index, filepath, area: 'Area') -> None:
        super().__init__(name, index, filepath)
        self.area = area
        self.category_items = []
        
        area.area_categories.append(self)
        
class Item(JohnnyDecimalIndexedObject):
    parent_category: Category
    notes_for_index: list[str]

    def __init__(self, name, index, filepath, parent_obj: Category) -> None:
        super().__init__(name, index, filepath)

        self.parent_category = parent_obj
        self.notes_for_index = []
        parent_obj.category_items.append(self)
        


def main():
    d = Path("/home/danny/Documents/Obsidian Vault/")
    finder = ObjectFinder(d)
    
    areas,categories,items = finder.get_all_objects_from_root_directory()

    for area in areas:
        print(area)
        for category in categories:
            print(category)
            for item in items:
                print(item)

if __name__ == "__main__":
    main()