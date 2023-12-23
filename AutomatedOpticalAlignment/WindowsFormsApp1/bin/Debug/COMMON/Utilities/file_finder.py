"""
| $Revision:: 281985                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-29 19:39:42 +0100 (Wed, 29 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------
"""

import os


class FileFinder:
    """
    A utility class that provides functions capable of finding files and/or folders in a given directory.
    """
    def find_files_by_ext(self, search_dir, extension, exclusions):
        """
        Recursively searches the provided search directory to find files that match the provided extension. If a folder
        contains child folders, they will also be searched for files.

        The extension ignores files and/or folders in the exclusions list.

        :param search_dir: directory to search for files in.
        :type search_dir: str
        :param extension: extension of the files to search for.
        :type extension: str
        :param exclusions: list of files or folders to exclude during the search.
        :type exclusions: list of str
        :return: a list of files matching the extension
        :rtype: list of str
        """
        if extension is None:
            raise ValueError('Extension cannot be None! '
                             'To get a list of files without using the extension, use the find_files function!')
        elif extension in ['', ' ']:
            raise ValueError('Extension cannot be empty or a space!'
                             'To get a list of files without using the extension, use the find_files function!')
        if exclusions is None:
            exclusions = []
        found_files = []
        file_list = os.listdir(search_dir)
        if len(file_list) > 0:
            for file in file_list:
                full_path = search_dir + '\\' + file
                if file not in exclusions:
                    if extension in file and os.path.isfile(full_path):
                        found_files.append(full_path)
                    else:
                        if os.path.isdir(full_path):
                            sub_dir_files = self.find_files_by_ext(full_path, extension, exclusions)
                            if sub_dir_files is not None:
                                found_files = found_files + sub_dir_files
        return found_files

    def find_files(self, search_dir, exclusions):
        """
        Recursively searches the provided directory for files. If a directory contains child folders, they are also
        searched for files. The function returns all files in a tree of folders regardless of their extension.

        The extension ignores files and/or folders in the exclusions list.

        :param search_dir: directory to search for files in.
        :type search_dir: str
        :param exclusions: files and folders to exclude from the search.
        :type exclusions: list of str
        :return: a list of files found in the search directory tree.
        :rtype: list of str
        """
        if exclusions is None:
            exclusions = []
        found_files = []
        file_list = os.listdir(search_dir)
        if len(file_list) > 0:
            for file in file_list:
                full_path = search_dir + '\\' + file
                if file not in exclusions:
                    if os.path.isfile(full_path):
                        found_files.append(full_path)
                    else:
                        if os.path.isdir(full_path):
                            sub_dir_files = self.find_files(full_path, exclusions)
                            if sub_dir_files is not None:
                                found_files = found_files + sub_dir_files
        return found_files

    def find_folders(self, search_dir, exclusions):
        """
        Recursively searches the provided directory for folders. If a folder contains child folders, the function will
        search through them as well.

        The extension ignores files and/or folders in the exclusions list.

        :param search_dir: directory to search for folders.
        :type search_dir: str
        :param exclusions: a list of directories to exclude from the search.
        :type exclusions: list of str
        :return: a list of folders found in the search directory.
        :rtype: list of str
        """
        if exclusions is None:
            exclusions = []
        found_folders = []
        folder_list = os.listdir(search_dir)
        if len(folder_list) > 0:
            for folder in folder_list:
                full_path = search_dir + '\\' + folder
                if folder not in exclusions:
                    if os.path.isdir(full_path):
                        found_folders.append(full_path)
                        sub_dirs = self.find_folders(full_path, exclusions)
                        if sub_dirs is not None:
                            found_folders = found_folders + sub_dirs
        return found_folders
