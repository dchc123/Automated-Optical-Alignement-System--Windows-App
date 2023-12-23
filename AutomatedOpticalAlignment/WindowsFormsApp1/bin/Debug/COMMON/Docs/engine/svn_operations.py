import sys
import svn.local

path = sys.argv[1]

link = svn.local.LocalClient(path)
status = link.status()
missing = []
unversioned = []
for entry in status:
    rel_path = entry.name.split('\\', 2)[-1]
    if entry.type_raw_name == 'missing':
        missing.append(entry)
        print('Deleting missing file:   {}'.format(rel_path))
        try:
            link.run_command('del', [rel_path], wd=link.path)   # no built-in del method
        except Exception as e:
            print("Failed to delete {}".format(rel_path))
            print(str(e))
    elif entry.type_raw_name == 'unversioned':
        unversioned.append(entry)
        print('Adding unversioned file: {}'.format(rel_path))
        try:
            link.add(rel_path)
        except Exception as e:
            print("Failed to add {}".format(rel_path))
            print(str(e))
