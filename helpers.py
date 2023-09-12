import os


def create_folder_if_not_exists(folder: str):
    if not os.path.exists(folder):
        os.mkdir(folder)


def get_next_index(directory: str, split_by_dot: bool = False) -> str:
    """
    Gets the next available index based on numeric filenames or foldernames in a directory.

    Args:
    - directory (str): Path to the directory to check.
    - split_by_dot (bool): Whether to split filenames by dot (for file extensions) and use the first part.

    Returns:
    - str: Next available index as a string.
    """
    listed_items = os.listdir(directory)

    if split_by_dot:
        numeric_items = [name.split(
            ".")[0] for name in listed_items if name.split(".")[0].isdigit()]
    else:
        numeric_items = [name for name in listed_items if name.isdigit()]

    if numeric_items:
        highest_num = max(map(int, numeric_items))
        return str(highest_num + 1)
    else:
        return str(0)


def read_files_from_directory(directory_path, is_nested_structure=True):
    file_texts = []

    for file_or_folder_index, _ in enumerate(os.listdir(directory_path)):
        path = os.path.join(directory_path, str(file_or_folder_index))

        if is_nested_structure and os.path.isdir(path):
            para_list = []

            for subfile_index, _ in enumerate(os.listdir(path)):
                subpath = os.path.join(path, f"{subfile_index}.txt")

                with open(subpath, 'r') as f:
                    para_list.append(f.read())

            file_texts.append(" ".join(para_list))
        elif not is_nested_structure:
            with open(f"{path}.txt", 'r') as f:
                file_texts.append(f.read())

    return file_texts


def get_references(document_type):
    return read_files_from_directory(os.path.join(os.path.curdir, "english_laws_with_abstracts", document_type))


def get_summarized(method, model):
    return read_files_from_directory(os.path.join(os.path.curdir, "english_laws_with_abstracts", "summarized", method, model), is_nested_structure=False)
