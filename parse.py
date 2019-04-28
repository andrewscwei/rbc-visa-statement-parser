import re
import sys
from typing import Match

from categories import categories
from config import exclude_line_regexes, max_col_widths


# Prettifies all lines in the statement, adding uniform spacing between columns.
def format_statement(match: Match) -> str:
  col_date = match.group(1).ljust(max_col_widths['date'])
  col_desc = match.group(2).ljust(max_col_widths['desc'])
  col_value = match.group(3).ljust(max_col_widths['value'])
  return r'{0}    {1}    {2}'.format(col_date, col_desc, col_value)

# Get input file from args.
file_in = sys.argv[1]
file_out = f'{file_in}-parsed'

print(f'Parsing file "{file_in}" > "{file_out}"...')

# Regex for dates.
regex_date: str = r'[A-Za-z]{3} [0-9]{2}(?:, )?(?:[0-9]{4})?'

# Regex for money values.
regex_value: str = r'-?\$[0-9,]+.?[0-9]{2}'

# Regex for transaction codes.
regex_code: str = r'[0-9]{23}'

# Store file content in string.
file = open(file_in, 'r')
read_str = file.read()
file.close()

# Count original number of lines, for output reference only.
old_cloc: int = len(read_str.split('\n'))

# Remove all blank lines but leave one at EOF for easier parsing later on.
read_str = re.sub(r'\n(?!({0}))'.format(regex_date), ' ', read_str) + '\n'

# Remove posting date that is before the transaction date and only keep
# transaction date.
read_str = re.sub(r'({0}) ({1})'.format(regex_date, regex_date), r'\1', read_str)

# Remove the currency exchange info that is before the money value.
read_str = re.sub(r'(Foreign Currency.*)({0})'.format(regex_value), r'\2', read_str)

# Move transaction code to the end.
read_str = re.sub(r'({0})(.*)({1})(.*)'.format(regex_date, regex_code), r'\1 \2 \4', read_str)

# Remove tabs.
read_str = re.sub(r'\t', ' ', read_str)

# Remove extra spaces.
read_str = re.sub(r' +', ' ', read_str)

# Remove all lines in the regexes of lines to exclude.
for regex in exclude_line_regexes:
  read_str = re.sub(re.compile('%s%s%s' % (r'(.*?)', regex, r'(.*?)\n')), '', read_str)

# Assign transactions to known categories.
for category in categories:
  for regex in categories[category]:
    read_str = re.sub(re.compile('%s%s%s' % (r'(.*?', regex, r'.*?)\n')), r'\1' + ' ' + category + r' \n', read_str)

# Apply space formatting.
read_str = re.sub(r'({0}) +(.*) +({1})'.format(regex_date, regex_value), format_statement, read_str)

# Remove trailing whitespace
read_str = re.sub(r' +(\n)', r'\1', read_str)

# Overwrite original file.
file = open(file_out, 'w')
file.write(read_str)
file.close()

# Count total lines in output string and minus one to account for the blank line
# at EOF.
new_cloc = len(read_str.split('\n')) - 1

print(read_str)
print()
print(f'Parsing file "{file_in}" > "{file_out}"... OK: {old_cloc} > {new_cloc} entr(ies) in result')
