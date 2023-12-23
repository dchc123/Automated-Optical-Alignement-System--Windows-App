"""
| :$Revision:: 278820                                       $:  Revision of last commit
| :$Author:: sgotic@SEMNET.DOM                              $:  Author of last commit
| :$Date:: 2018-07-03 23:08:08 +0100 (Tue, 03 Jul 2018)     $:  Date of last commit
| --------------------------------------------------------------------------------

"""

# Standard Imports
import hashlib


class CSRHashGenerator:
    def _get_file_contents(self, file):
        """

        :param file: The CSR file to get the contents from
        :type file: str
        :return: List of every line in the file
        :rtype: list of str
        """
        # Open the CSR file
        #csr_file = open(file, 'r', encoding='utf-8')
        csr_file = open(file, 'rb')
        # Read in the contents of the CSR file
        file_contents = csr_file.readlines()
        # Close the file
        csr_file.close()
        # Return the contents of the file
        return file_contents

    def get_hash(self, file):
        """
        Generates a sha3_512 hash in hex format for the passed in CSR file. The function excludes the hash and revision
        portions of the file which are located at both the bottom and the top of the file.

        :param file: csr file to generate a hash for
        :type file: str
        :return: the sha3_512 hash of the csr file
        :rtype: str
        """
        # Create a sha3_512 hash generator object
        sha3_512_hash = hashlib.sha3_512()
        # Get the file contents
        file_contents = self._get_file_contents(file)
        # Add each line to the sha3_512 generator but do not include the SVN revision or extra parameter information
        for line in file_contents[8:(len(file_contents) - 2)]:
            # sha3_512_hash.update(line.encode('utf-8'))
            sha3_512_hash.update(line)

        # Return the digested sha3_512 hash
        return sha3_512_hash.hexdigest()

    def update_hash(self, file):
        """
        Generates a new sha3_512 has for the passed in CSR file and updates the one currently in the file.

        :param file: csr file to update the hash for
        :type file: str
        """
        # Get the files hash
        csr_hash = self.get_hash(file)
        # Get the file contents
        file_contents = self._get_file_contents(file)
        # Calculate the offset to the CSR hash parameter stored in the CSR file
        seek_pos = 0
        for line in file_contents[0:(len(file_contents) - 2)]:
            seek_pos += len(line)
        # Open the CSR file
        csr_file = open(file, 'r+')
        # Position the file pointer to start at the hash parameter line
        csr_file.seek(seek_pos)
        # Read in the line
        hash_line = csr_file.readline()
        # Get the parameter name as this must match
        csr_name = hash_line.split('=')[0]
        # The read moved the file pointer so reset it back
        csr_file.seek(seek_pos)
        # Write the updated hash
        csr_file.write('{0}= "{1}"\n'.format(csr_name, csr_hash))
        # Close the file
        csr_file.close()
