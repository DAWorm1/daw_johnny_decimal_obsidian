# Johnny Decimal - Python companion

### Instructions to set up
1. Edit `d` in `johnny_decimal.main()` function to be the absolute filepath to your Obsidian Vault
2. Run the `johnny_decimal.py` file to automatically create a `00.00 - Index.md` file within the Area with index 0 within the Obsidian Vault provided in Step 1.

**Additional Features**
- Any [File Properties](https://help.obsidian.md/Editing+and+formatting/Properties) on an `Item` object with the key `indexNotes` are included on the generated Index.
- Any items (which are also directories) at index X.00 containing the text `media` within the name are excluded from the Index. This is to avoid cluttering the index with the folder containing any media files which happen to be used in notes within that Item.
- Allows adding index metadata (`indexNotes`) to a Category and Item (directories). Properties must be stored in a MarkDown file within the category (or item) directory with index X.00 where `X` is the containing Category or Item's Index. 
- - Example: 42.00.md would hold the metadata for category index 42; 42.59.00 would hold the metadata for the item at 42.59 -- Item 42.59 is a directory and does not have a way to add a File Property within Obsidian.

**Known Limitations**
- Obsidian File Properties of the 'list' type are not supported
- Metadata at the Area level is not supported