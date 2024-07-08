# Johnny Decimal - Python companion

This script, in its current state (as of July 2024), automatically generates an index for your Obsidian Vault which is structured using the Johnny.Decimal organization system

**Assumptions:**
Obsidian Vault directory structure:
```
├── 00 - 09 NOTES ADMINISTRATION
│   ├── 00.00 - Index.md
│   ├── 01 Organization
│   │   └── 01.01 - Johnny Decimal.md
│   └── 02 Obsidian
│       ├── 02.01 - Tips
│       │   ├── 02.01.00.md
│       │   ├── Callouts.md
│       │   └── Cheat Sheet.md
│       └── 02.02 - File Properties.md
├── 20 - 29 PERSONAL
│   └── 23 Knowledge
│       └── 23.01 - Reddit.md
├── 40 - 49 PROGRAMMING
│   ├── 42 Other projects
│   │   └── 42.01 - Email Management
│   │       ├── AI Pipeline.md
│   │       ├── AI Prompts for Emails.md
│   │       └── Email Management.md
│   ├── 43 Knowledge
│   │   ├── 43.00 - media
│   │   │   └── AI_Design_Patterns.pdf
│   │   ├── 43.01 - Logging.md
│   │   └── 43.02 - AI
│   │       ├── AI Frameworks.md
│   │       └── Design Pattern for AI.md
```
- `Areas` must start with `XX - XX` where `X` is a number
- `Categories` must start with `XX` where `X` is a number.
- - Note that categories do not have a dash
- `Items` must start with `XX.XX` where `X` is a number. 
- - `Items` can be both a directory as well as a Markdown file
- - Metadata for an `Item` which is a directory is stored in at the 0th index of the item. Example: `02.01.00.md` contains the metadata for `Item` `02.01 - Tips`

**Example Index output**
```
# 00 - 09 NOTES ADMINISTRATION
### 01 Organization
[[01.01 - Johnny Decimal]]
### 02 Obsidian
02.01 - Tips
 - This is a note I would like to see within the index.
[[02.02 - File Properties]]
 - This is a note I would like to see within the index.

# 20 - 29 PERSONAL
### 23 Knowledge
[[23.01 - Reddit]]

# 30 - 39 MUSIC
### 31 Career

# 40 - 49 PROGRAMMING
### 42 Other projects
42.01 - Email Management
### 43 Knowledge
[[43.01 - Logging]]
43.02 - AI
```
---

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
- Multiple Systems are not supported