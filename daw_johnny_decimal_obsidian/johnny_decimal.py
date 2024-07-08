from pathlib import Path
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import os


if TYPE_CHECKING:
    from pathlib import Path    
    from typing import List,Union,Type



@dataclass(order=False)
class JohnnyDecimalIndexedObject():
    index: str
    name: str
    filepath: Path

    def get_obsidian_name(self):
        if self.filepath.is_dir():
            return self.filepath.name
        
        return self.filepath.stem

    def get_obsidian_link(self):
        if self.filepath.is_dir():
            return self.get_obsidian_name()
        
        return f"[[{self.get_obsidian_name()}]]"
    
    def get_index_text(self):
        raise NotImplemented
    
    def _get_obsidian_properties(self) -> None|dict:
        def read_and_parse(filepath):
            raw_properties = []
            parsed_properties = {}

            with open(filepath,"r") as fp:
                first_line = fp.readline().strip()
                
                if first_line != "---":
                    return None
                
                while True:
                    s = fp.readline().strip()
                    
                    # Make sure we haven't reached the end the properties section
                    if s == "---":
                        break

                    raw_properties.append(s)
                
                if len(raw_properties) == 0:
                    return None
            
            # Does not support lists yet.
            # Supports text, number, and date
            supported_data_types = [
                    r"([a-zA-Z_\/ ]*): (.+)"
                ]

            for property_str in raw_properties:
                for pattern in supported_data_types:
                    if re.fullmatch(pattern,property_str):
                        key = re.sub(pattern,"\\1",property_str)
                        value = re.sub(pattern,"\\2",property_str)
                        
                        parsed_properties[key] = value
                        break
            
            return parsed_properties
            
        if self.filepath.is_dir():
            # No support for metadata on areas.
            if isinstance(self,Area):
                return None
            
            # We know we're working with either an Item or Category object which is a directory. 

            # Check if we have a metadata formatted file
            files = self.filepath.glob(f"{self.index}.00*.md")
            _count = 0
            parsed_properties = None
            for path in files:
                if _count > 0:
                    break
                parsed_properties = read_and_parse(path)
                _count += 1

            return parsed_properties if parsed_properties else None
        
        parsed_properties = read_and_parse(self.filepath)        

        return parsed_properties

    def __lt__(self,other):
        if not isinstance(other,JohnnyDecimalIndexedObject):
            return NotImplemented

        return self.index < other.index

class ObjectFinder():
    root_directory: Path
    areas: 'List[Area]'
    categories: 'List[Category]'
    items: 'List[Item]'


    def __init__(self, root_directory: Path) -> None:
        self.root_directory = root_directory
        self.areas = []
        self.categories = []
        self.items = []

    def get_area_at_index(self, index: str):
        if len(self.areas) == 0:
            self.get_all_objects_from_root_directory(force_search=True)

        for area in self.areas:
            if area.index[0] == index[0]:
                return area
        
        return None

    def get_all_objects_from_root_directory(self, force_search: bool = False) -> 'tuple[list[Area],list[Category],list[Item]]':
        if not force_search:
            if len(self.areas + self.categories + self.items) != 0:
                return (self.areas, self.categories, self.items)

        print("WARNING: running full search")
        # Get all areas    
        areas = ObjectFinder.get_areas(self.root_directory) 
        categories = []  
        items = []

        # Get all categories
        for area in areas:
            categories += ObjectFinder.get_categories(area)
            
        # Get all items
        for category in categories:       
            # Get items 
            items += ObjectFinder.get_items(category)

        # Set local variables for later use
        self.areas = areas
        self.categories = categories
        self.items = items

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
                name = re.sub(pattern_to_match,"\\1",item.name)
                index = re.sub(pattern_to_match,"\\2",item.name)
                

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
                        parent_obj))
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
    finder: 'ObjectFinder'
    index: list['JohnnyDecimalIndexedObject']
    filepath: Path

    def __init__(self, finder: 'ObjectFinder') -> None:
        self.finder = finder
        
        root_area = finder.get_area_at_index("0")
        if root_area:
            self.filepath = root_area.filepath / "00.00 - Index.md"
        else:
            self.filepath = finder.root_directory / "00.00 - Index.md"

    def create_index_for_all_objects(self):
        """
        Creates an index at self.filepath. 

        Ignores any items which are a .00 index and contain media in the name
        """
        areas, categories, items = self.finder.get_all_objects_from_root_directory()
        entries = areas + categories + items
        
        entries.sort()

        if os.path.exists(self.filepath):
            os.remove(self.filepath)

        with open(self.filepath,"w") as fp:
            for i in entries:
                if isinstance(i,Item):
                    if i.index[-2:] == "00" and "media" in i.name:
                        continue
                
                fp.write(f"{i.get_index_text()}\n")

        return (entries, self.filepath)


class Area(JohnnyDecimalIndexedObject):
    children: 'List[Category]' = field(default_factory=list, compare=False)

    def __init__(self, name, index, filepath) -> None:
        super().__init__(name, index, filepath)
        self.children = []

    def get_index_text(self):
        s = f"# {self.get_obsidian_link()}"

        if self.index[0] != "0":
            s = "\n" + s
        
        return s


class Category(JohnnyDecimalIndexedObject):
    parent: Area = field(compare=False)
    children: 'List[Item]' = field(default_factory=list, compare=False)
    properties: dict|None = field(init=False, compare=False)

    def __init__(self, name, index, filepath, area: 'Area') -> None:
        super().__init__(name, index, filepath)
        self.parent = area
        self.children = []
        self.properties = self._get_obsidian_properties() if self._get_obsidian_properties() else None
        
        area.children.append(self)

    def get_index_text(self):
        s = f"### {self.get_obsidian_link()}"
        if self.properties is None:
            return s
        
        index_notes = self.properties.get("indexNotes", None)

        if index_notes:
            s = s + f"\n - {index_notes}"
        
        return s
        
class Item(JohnnyDecimalIndexedObject):
    parent: Category = field(compare=False)
    properties: dict|None = field(init=False,compare=False)
    is_dir: bool = field(init=False, compare=False)

    def __init__(self, name, index, filepath, parent_obj: Category) -> None:
        super().__init__(name, index, filepath)
        self.is_dir = self.filepath.is_dir()
        
        if not self.is_dir:
            self.name = re.sub(r"\.md$","",self.name)

        self.parent = parent_obj
        props = self._get_obsidian_properties()
        self.properties = props if props is not None else None
        parent_obj.children.append(self)
            

    def get_index_text(self):
        s = f"{self.get_obsidian_link()}"
        if self.properties is None:
            return s
        
        index_notes = self.properties.get("indexNotes", None)

        if index_notes:
            s = s + f"\n - {index_notes}"
        
        return s


def main():
    d = Path("/home/danny/Documents/Obsidian Vault/")
    finder = ObjectFinder(d)
    indexer = JohnnyDecimalIndexer(finder)

    areas,categories,items = finder.get_all_objects_from_root_directory()
    index, filepath = indexer.create_index_for_all_objects()

    

if __name__ == "__main__":
    main()