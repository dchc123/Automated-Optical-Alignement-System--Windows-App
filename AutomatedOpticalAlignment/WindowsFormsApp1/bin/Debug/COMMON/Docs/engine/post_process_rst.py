"""
This script for post processes RST files, to prep them for various builds:
 * Removes "Subpackage" and "Submodule" headings to clean-up 'toctree's
 * Modify auto-generated 'toctree's with maxdepth option
"""
import glob
import sys

if len(sys.argv) > 1:
    rst_path = sys.argv[1] + r"\*.rst"
else:
    rst_path = r"source\*.rst"

rst_fnames = glob.glob(rst_path)

for fname in rst_fnames:
    content = ""
    maxdepth_prefix = " "*4    # ugly hack to fix sphinx mixed tab sizes
    with open(fname, 'r+') as f:
        for line in f:
            # Line containing subpackages is already read and will not be appended to content,
            # but we call next on f to skip to the next iteration which discards
            # the next line which is the header's underlining
            if line == "Subpackages\n":
                maxdepth_prefix = " " * 4
                next(f)
            elif line == "Submodules\n":
                maxdepth_prefix = " " * 3
                next(f)  # skip header underlining
            # Add maxdepth option to auto generated toctree
            elif line == ".. toctree::\n" and not fname.endswith("index.rst"):
                content += line + maxdepth_prefix + ":maxdepth: 2\n"
            else:
                content += line

        f.seek(0)  # go back to beginning of file
        f.write(content)  # write the new content without subpackages/submodules headings
        f.truncate()  # truncate the rest of the file
